from concurrent.futures import ThreadPoolExecutor, as_completed

from config import REPAIR_COSTS_FILE
from constants.parts import PARTS
from llm.repair_costs import search_repair_cost
from services.repair_cost import is_repair_cost_valid
from utils.file_parser import get_json_file, write_to_json

BATCH_SIZE = 5


def __get_parts_to_search(existing_data: dict) -> list[str]:
    return [part for part in PARTS if part not in existing_data]


def __fetch_repair_costs(parts: list[str]) -> dict:
    def fetch(part: str):
        name, category, _ = PARTS[part]
        costs = search_repair_cost(name, category)
        if not is_repair_cost_valid(costs):
            raise ValueError("costs failed validation")
        return part, costs.model_dump()

    results, failed = {}, []
    with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
        futures = {executor.submit(fetch, part): part for part in parts}
        for future in as_completed(futures):
            part = futures[future]
            try:
                key, costs = future.result()
                results[key] = costs
                print(f"  ok      {part}")
            except Exception as e:
                failed.append(part)
                print(f"  failed  {part}: {e}")

    return results


def prepare_repair_costs():
    existing_repair_costs = get_json_file(REPAIR_COSTS_FILE) or {}
    parts_to_search = __get_parts_to_search(existing_repair_costs)

    total_parts = len(parts_to_search)
    print(f"{len(existing_repair_costs)} parts already stored, {total_parts} to search")

    for start in range(0, total_parts, BATCH_SIZE):
        batch = parts_to_search[start:start + BATCH_SIZE]
        print(f"batch {start // BATCH_SIZE + 1}: {batch}")

        existing_repair_costs.update(__fetch_repair_costs(batch))
        write_to_json(REPAIR_COSTS_FILE, existing_repair_costs)

    print(f"done: {len(existing_repair_costs)}/{len(PARTS)} parts stored")
