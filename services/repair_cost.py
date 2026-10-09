from utils.file_parser import get_csv_file
from config import REPAIR_COSTS_FILE
from llm.repair_costs import search_repair_cost
from models.repair_costs import RepairCosts


__REPAIR_COST = get_csv_file(REPAIR_COSTS_FILE)

def get_repair_cost(part, car_type, severity):
    if part not in __REPAIR_COST:
        __REPAIR_COST[part] = search_repair_cost(part).model_dump()
    return __CAR_FACTS[car]

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

