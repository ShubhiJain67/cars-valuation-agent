"""
Comparable-car search, fully in memory.

At import, the Cars24 listings are loaded from the CSV and each listing becomes a vector of
[age, log km, owners], standardised and weighted. A query then:
  1. takes every listing of the same class (luxury brand or not) and size (hatchback/sedan/suv);
     luxury and normal cars are never mixed, and with too few in the pool no price is given
  2. scores each by Manhattan distance on [age, log km, owners], plus a penalty for each
     mismatch in model, make, fuel and transmission
  3. keeps the 15 nearest: exact matches come first, near-matches fill the rest
  4. ages each comparable's price to the requested car's age
  5. returns the weighted median and the 10th-90th percentile range

Penalties instead of hard filters mean a rare or unseen model still gets its closest
relatives (same make, same fuel...) rather than falling off a cliff to a broad filter.

8k listings fit in memory and a brute-force pass over a few thousand rows is exact and takes
well under a millisecond, so no database or vector index is needed at this size.

Run `python -m services.nearest_cars` to check accuracy on held-out listings.
"""
import numpy as np

from config import CLEAN_DATA_FILE, LISTING_YEAR
from constants.car import car_class, car_size
from utils.file_parser import get_csv_file

# Added to the distance when a listing differs from the car on that attribute.
# Tuned on held-out listings (python -m services.nearest_cars), in the same units as the distance.
MISMATCH_PENALTIES = {"name": 1.0, "make": 0.25, "fuel": 0.5, "transmission": 1.0, "body_type": 0.5}
K = 15
MIN_POOL = 5  # fewer comparable cars of the same class and size than this: refuse to price
# How much each dimension [age, log km, owners] counts in the distance, after standardising
WEIGHTS = np.array([1.0, 0.6, 0.3])
# 10th-90th percentile of the comparables: held-out tests put ~75% of real prices inside it
RANGE = (0.10, 0.90)
TEXT_COLUMNS = ("name", "make", "fuel", "transmission", "body_type", "state")


def build_index(data) -> dict:
    raw = _raw_features(LISTING_YEAR - data["year"], data["km"], data["owner"])
    mean, std = raw.mean(axis=0), raw.std(axis=0)
    return {
        "mean": mean,
        "std": std,
        "yearly_depreciation": _yearly_depreciation(data),
        "vectors": (raw - mean) / std * WEIGHTS,
        "age": (LISTING_YEAR - data["year"]).to_numpy(float),
        "price": data["price"].to_numpy(float),
        "year": data["year"].to_numpy(int),
        "km": data["km"].to_numpy(int),
        "owner": data["owner"].to_numpy(int),
        **{c: data[c].astype(str).str.upper().to_numpy() for c in TEXT_COLUMNS},
        "car_class": data["make"].map(car_class).to_numpy(),
        "size": data["body_type"].map(car_size).to_numpy(),
    }


def find_comparables(index: dict, car: dict, k=K) -> dict:
    """
    car: name, make, fuel, transmission, body_type (uppercase), year, km, owner, age (today)

    Matching uses the car's age as of LISTING_YEAR, so a 2020 car is compared with 2020 listings
    (same point in their life when listed). The price is then aged to the car's age today.
    """
    wanted_class, wanted_size = car_class(car["make"]), car_size(car["body_type"])
    pool = np.flatnonzero((index["car_class"] == wanted_class) & (index["size"] == wanted_size))
    if len(pool) < MIN_POOL:
        return {"insufficient": True, "car_class": wanted_class, "size": wanted_size, "pool_size": len(pool)}

    listing_age = LISTING_YEAR - car["year"]
    query = (_raw_features(listing_age, car["km"], car["owner"]) - index["mean"]) / index["std"] * WEIGHTS
    distances = np.abs(index["vectors"][pool] - query).sum(axis=1)  # Manhattan
    for key, penalty in MISMATCH_PENALTIES.items():
        distances += penalty * (index[key][pool] != car[key])

    order = np.argsort(distances)[:k]
    nearest, nearest_distances = pool[order], distances[order]

    # Listings are a 2023 snapshot; age each comparable to the requested car's age
    # using the depreciation rate learned from the data (adjusted-comparables method).
    age_gap = car["age"] - index["age"][nearest]
    adjusted = index["price"][nearest] * np.exp(index["yearly_depreciation"] * age_gap)
    weights = 1 / (nearest_distances + 0.05)
    exact = (index["name"][nearest] == car["name"]) & (index["fuel"][nearest] == car["fuel"]) \
        & (index["transmission"][nearest] == car["transmission"])

    return {
        "insufficient": False,
        "car_class": wanted_class,
        "exact_matches": int(exact.sum()),
        "rows": nearest,
        "distances": nearest_distances,
        "adjusted_prices": adjusted,
        "estimate": _weighted_quantile(adjusted, weights, 0.5),
        "low": _weighted_quantile(adjusted, weights, RANGE[0]),
        "high": _weighted_quantile(adjusted, weights, RANGE[1]),
    }


def _raw_features(age, km, owner) -> np.ndarray:
    return np.column_stack([np.asarray(age, float), np.log1p(np.asarray(km, float)), np.asarray(owner, float)])


def _yearly_depreciation(data) -> float:
    """Within each car model, how much log(price) drops per extra year of age, holding km fixed."""
    age = (LISTING_YEAR - data["year"]).astype(float)
    log_km = np.log1p(data["km"].astype(float))
    log_price = np.log(data["price"].astype(float))
    demean = lambda s: (s - s.groupby(data["name"]).transform("mean")).to_numpy()
    slope, *_ = np.linalg.lstsq(np.column_stack([demean(age), demean(log_km)]), demean(log_price), rcond=None)
    return float(slope[0])


def _weighted_quantile(values, weights, q) -> float:
    order = np.argsort(values)
    values, weights = values[order], weights[order]
    cumulative = (np.cumsum(weights) - 0.5 * weights) / weights.sum()
    return float(np.interp(q, cumulative, values))


LISTINGS = get_csv_file(CLEAN_DATA_FILE)
INDEX = build_index(LISTINGS)


def evaluate(holdout_share=0.2, seed=7):
    """Price 20% of listings using only the other 80% and report the error."""
    test = LISTINGS.sample(frac=holdout_share, random_state=seed)
    index = build_index(LISTINGS.drop(test.index))
    errors, inside = [], 0
    for row in test.itertuples():
        car = {c: str(getattr(row, c)).upper() for c in TEXT_COLUMNS}
        car |= {"year": row.year, "age": LISTING_YEAR - row.year, "km": row.km, "owner": row.owner}
        result = find_comparables(index, car)
        if result["insufficient"]:
            continue
        errors.append(abs(result["estimate"] / row.price - 1))
        inside += result["low"] <= row.price <= result["high"]
    errors = np.array(errors)
    print(f"{len(errors)} held-out cars: median error {np.median(errors):.1%}, "
          f"80% within {np.quantile(errors, 0.8):.1%}, actual price inside range {inside / len(errors):.0%}")


if __name__ == "__main__":
    evaluate()
