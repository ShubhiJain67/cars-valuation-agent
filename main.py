from datetime import date

from constants.car import BODY_TYPES, FUELS, MAX_KM, MAX_OWNERS, SEVERITIES, TRANSMISSIONS
from constants.parts import PARTS
from models.car_facts import CarFacts
from services.car_facts import get_facts, is_fact_valid
from services.repair_cost import get_total_repair_cost


def validate_request(car, year, km_driven, owner_count, fuel, transmission, body_type, damages) -> list[str]:
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
        "damages": {
            "front_bumper": "severity_1",
            "bonnet": "severity_3",
        },
    }

    errors = validate_request(**request)
    if errors:
        print("Invalid car details:")
        for error in errors:
            print(f"  - {error}")
        return

    print("Valid car details")
    total, breakdown = get_total_repair_cost(request["damages"], request["body_type"])
    for part, cost in breakdown.items():
        print(f"  {part}: ₹{cost:,}")
    print(f"Total repair cost: ₹{total:,}")


if __name__ == "__main__":
    main()
