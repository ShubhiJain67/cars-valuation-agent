FUELS = ("PETROL", "DIESEL", "CNG", "LPG")
TRANSMISSIONS = ("MANUAL", "AUTOMATIC")
SEVERITIES = ("severity_1", "severity_2", "severity_3")

MAX_KM = 300_000
MAX_OWNERS = 4

# body_type as it appears in the Cars24 data -> car size used in repair_costs.json.
# Cars24's "Lux_" labels mark premium models (XUV500, Corolla Altis), not luxury brands,
# so whether a car is luxury is decided by its make (see car_class), never by body type.
BODY_TYPES = {
    "HatchBack": "hatchback",
    "Sedan": "sedan",
    "SUV": "suv",
    "Lux_hatchback": "hatchback",
    "Lux_sedan": "sedan",
    "Lux_SUV": "suv",
}

# First word of the car name, uppercased ("Land Rover Defender" -> "LAND")
LUXURY_MAKES = {"AUDI", "BMW", "JAGUAR", "LAND", "LEXUS", "MASERATI", "MERCEDES", "MERCEDES-BENZ",
                "MINI", "PORSCHE", "VOLVO"}


def car_class(make: str) -> str:
    """'luxury' or 'normal', from the make. Luxury cars are only ever compared with luxury cars."""
    return "luxury" if make.upper() in LUXURY_MAKES else "normal"


def car_size(body_type: str) -> str:
    return {k.upper(): v for k, v in BODY_TYPES.items()}[body_type.upper()]
