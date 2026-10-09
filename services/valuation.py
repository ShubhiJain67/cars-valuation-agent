from datetime import date

from services.nearest_cars import INDEX, find_comparables
from services.repair_cost import get_total_repair_cost


def get_base_price(car, year, km_driven, owner_count, fuel, transmission, body_type) -> dict:
    """Market price in good condition, from the nearest comparable Cars24 listings."""
    query = {
        "name": car.upper(),
        "make": car.split()[0].upper(),
        "fuel": fuel.upper(),
        "transmission": transmission.upper(),
        "body_type": body_type.upper(),
        "year": year,
        "age": date.today().year - year,
        "km": km_driven,
        "owner": owner_count,
    }
    result = find_comparables(INDEX, query)

    comparables = [
        {
            "name": INDEX["name"][row],
            "year": int(INDEX["year"][row]),
            "km": int(INDEX["km"][row]),
            "owner": int(INDEX["owner"][row]),
            "fuel": INDEX["fuel"][row],
            "transmission": INDEX["transmission"][row],
            "state": INDEX["state"][row],
            "listed_price": int(INDEX["price"][row]),
            "price_at_your_age": _round(adjusted),
            "distance": round(float(distance), 3),
        }
        for row, adjusted, distance in zip(result["rows"], result["adjusted_prices"], result["distances"])
    ]
    return {
        "base_price": _round(result["estimate"]),
        "low": _round(result["low"]),
        "high": _round(result["high"]),
        "exact_matches": result["exact_matches"],
        "comparables": comparables,
    }


def get_valuation(car, year, km_driven, owner_count, fuel, transmission, body_type, damages, **_) -> dict:
    base = get_base_price(car, year, km_driven, owner_count, fuel, transmission, body_type)
    repair_total, repair_breakdown = get_total_repair_cost(damages, body_type)
    return {
        **base,
        "repair_total": repair_total,
        "repair_breakdown": repair_breakdown,
        "final_price": max(base["base_price"] - repair_total, 0),
        "final_low": max(base["low"] - repair_total, 0),
        "final_high": max(base["high"] - repair_total, 0),
    }


def _round(price: float) -> int:
    return int(round(price, -3))
