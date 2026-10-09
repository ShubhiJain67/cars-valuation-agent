import sys
from datetime import date

from constants.car import BODY_TYPES, FUELS, MAX_KM, MAX_OWNERS, SEVERITIES, TRANSMISSIONS
from constants.parts import PARTS
from models.car_facts import CarFacts
from services.car_facts import get_facts, is_fact_valid
from services.images import process_images
from services.valuation import get_valuation


def validate_request(car, year, km_driven, owner_count, fuel, transmission, body_type, damages, state=None) -> list[str]:
    """Returns a list of problems with the request; empty list means valid."""
    errors = []
    car_facts = get_facts(car)
    if not is_fact_valid(car_facts):
        errors.append(f"unknown or unverifiable car model: {car}")
    elif not _year_valid(year, car_facts):
        errors.append(f"{car} was not sold new in {year}")
    if not 0 <= km_driven < MAX_KM:
        errors.append(f"km_driven must be between 0 and {MAX_KM}")
    if not 1 <= owner_count <= MAX_OWNERS:
        errors.append(f"owner_count must be between 1 and {MAX_OWNERS}")
    if fuel.upper() not in FUELS:
        errors.append(f"fuel must be one of {FUELS}")
    if transmission.upper() not in TRANSMISSIONS:
        errors.append(f"transmission must be one of {TRANSMISSIONS}")
    if body_type not in BODY_TYPES:
        errors.append(f"body_type must be one of {tuple(BODY_TYPES)}")
    for part, severity in damages.items():
        if part not in PARTS:
            errors.append(f"unknown part: {part}")
        if severity not in SEVERITIES:
            errors.append(f"{part}: severity must be one of {SEVERITIES}")
    return errors


def _year_valid(year: int, car_facts: CarFacts) -> bool:
    last_year = car_facts.last_year or date.today().year
    return car_facts.first_year <= year <= min(last_year, date.today().year)


def main():
    request = {
        "car": "Maruti S PRESSO",
        "year": 2020,
        "km_driven": 10000,
        "owner_count": 2,
        "fuel": "PETROL",
        "transmission": "Manual",
        "body_type": "HatchBack",
        "state": "DL",
        "damages": {
            "front_bumper": "severity_1",
            "bonnet": "severity_3",
        },
    }

    image_paths = sys.argv[1:]  # python main.py photo1.jpg photo2.jpg ...
    if image_paths:
        if not _apply_images(request, image_paths):
            return

    errors = validate_request(**request)
    if errors:
        print("Invalid car details:")
        for error in errors:
            print(f"  - {error}")
        return

    try:
        valuation = get_valuation(**request)
    except ValueError as e:
        print(e)
        return
    print(f"Base price: ₹{valuation['base_price']:,} (range ₹{valuation['low']:,} – ₹{valuation['high']:,})")
    print(f"  {len(valuation['comparables'])} comparables, {valuation['exact_matches']} exact matches (same model, fuel, transmission)")
    print("  nearest listings (listed in 2023; aged to your car's age):")
    for c in valuation["comparables"]:
        print(f"    d={c['distance']:.2f} | {c['name']} {c['fuel']} {c['transmission']} | {c['year']} | {c['km']:,} km | owner {c['owner']} | {c['state']} "
              f"| listed ₹{c['listed_price']:,} -> ₹{c['price_at_your_age']:,}")
    print("Repairs:")
    for part, cost in valuation["repair_breakdown"].items():
        print(f"  {part}: ₹{cost:,}")
    print(f"  total: ₹{valuation['repair_total']:,}")
    print(f"Final price: ₹{valuation['final_price']:,} (range ₹{valuation['final_low']:,} – ₹{valuation['final_high']:,})")


def _apply_images(request: dict, image_paths: list[str]) -> bool:
    """Replace the request's damages with those found in the photos. False if no photo is usable."""
    result = process_images(image_paths)
    for r in result["rejected"]:
        print(f"Discarded {r['image']}: {r['reason']}")
    if not result["accepted"]:
        print("No usable photos: include at least one photo of the number plate, "
              "and every photo must clearly show that same number.")
        return False
    print(f"Registration number {result['registration_number']}, {len(result['accepted'])} photos used")
    for f in result["findings"]:
        status = "" if f["priced"] else " (low confidence, not priced)"
        print(f"  {f['part']}: {f['severity']} - {f['description']}{status}")
    if result["unclear_areas"]:
        print(f"  could not judge: {', '.join(result['unclear_areas'])}")
    request["damages"] = result["damages"]
    return True


if __name__ == "__main__":
    main()
