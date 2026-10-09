from config import REPAIR_COSTS_FILE
from constants.car import car_class, car_size
from constants.parts import PARTS
from llm.repair_costs import search_repair_cost
from models.repair_costs import RepairCosts
from utils.file_parser import get_json_file, write_to_json


__REPAIR_COST = get_json_file(REPAIR_COSTS_FILE)


def get_repair_cost(part: str, car: str, body_type: str, severity: str) -> int:
    if part not in __REPAIR_COST:
        name, category, _ = PARTS[part]
        costs = search_repair_cost(name, category)
        if not is_repair_cost_valid(costs):
            raise ValueError(f"repair costs for {part} failed validation")
        __REPAIR_COST[part] = costs.model_dump()
        write_to_json(REPAIR_COSTS_FILE, __REPAIR_COST)
    return __REPAIR_COST[part][car_class(car.split()[0])][car_size(body_type)][severity]


def get_total_repair_cost(damages: dict[str, str], car: str, body_type: str) -> tuple[int, dict[str, int]]:
    breakdown = {part: get_repair_cost(part, car, body_type, severity) for part, severity in damages.items()}
    return sum(breakdown.values()), breakdown


def is_repair_cost_valid(costs: RepairCosts) -> bool:
    for car_class in (costs.normal, costs.luxury):
        for size in (car_class.hatchback, car_class.sedan, car_class.suv):
            figures = (size.severity_1, size.severity_2, size.severity_3)
            if not all(200 <= f <= 500_000 for f in figures):
                return False
            if not figures[0] <= figures[1] <= figures[2]:
                return False
    for size in ("hatchback", "sedan", "suv"):
        if getattr(costs.luxury, size).severity_2 < getattr(costs.normal, size).severity_2:
            return False
    return True
