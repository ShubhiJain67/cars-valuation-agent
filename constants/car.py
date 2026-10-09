FUELS = ("PETROL", "DIESEL", "CNG", "LPG")
TRANSMISSIONS = ("MANUAL", "AUTOMATIC")
SEVERITIES = ("severity_1", "severity_2", "severity_3")

MAX_KM = 300_000
MAX_OWNERS = 4

# body_type as it appears in the Cars24 data -> (car class, size) used in repair_costs.json
BODY_TYPES = {
    "HatchBack": ("normal", "hatchback"),
    "Sedan":     ("normal", "sedan"),
    "SUV":       ("normal", "suv"),
    "Lux_hatchback": ("luxury", "hatchback"),
    "Lux_sedan": ("luxury", "sedan"),
    "Lux_SUV":   ("luxury", "suv"),
}
