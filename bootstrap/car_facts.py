from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.file_parser import get_json_file, get_csv_file, write_to_json
from config import CAR_FACTS_FILE, CLEAN_DATA_FILE
from llm.car_facts import search_fact


BATCH_SIZE = 5


def __get_cars_to_search(raw_data, existing_data):
    cars_to_search = set()

    for _, car_item in raw_data.iterrows():
        car = car_item["name"]
        if car not in existing_data:
            cars_to_search.add(car)

    print(f"Need to search for a total of {len(cars_to_search)} cars")
    return cars_to_search


def __fetch_cars_data(cars):
    cars_data = {}
    failed_cars = []

    def fetch(car):
        print(f"Searching for {car}")
        car_fact = search_fact(car)
        return car, car_fact.model_dump()

    with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
        futures = {
            executor.submit(fetch, car): car
            for car in cars
        }
        for future in as_completed(futures):
            car = futures[future]
            try:
                car, data = future.result()
                cars_data[car] = data
                print(f"Successfully fetched: {car}")
            except Exception as e:
                failed_cars.append(car)
                print(f"Failed to fetch {car}: {e}")

    print(f"Successfully fetched: {len(cars_data)}")
    print(f"Failed: {len(failed_cars)}")
    return cars_data


def prepare_car_facts():
    print("Preparing car facts")
    raw_data = get_csv_file(CLEAN_DATA_FILE)
    existing_car_facts = get_json_file(CAR_FACTS_FILE)
    cars_to_search = list(__get_cars_to_search(raw_data, existing_car_facts))
    total_cars = len(cars_to_search)

    for start in range(0, total_cars, BATCH_SIZE):
        batch = cars_to_search[start:start + BATCH_SIZE]
        print(
            f"\nProcessing batch {start // BATCH_SIZE + 1}: "
            f"{len(batch)} cars"
        )
        new_cars_data = __fetch_cars_data(batch)
        existing_car_facts.update(new_cars_data)
        write_to_json(CAR_FACTS_FILE, existing_car_facts)
        print(f"Saved {len(new_cars_data)} new car facts. " f"Total cached: {len(existing_car_facts)}")
    print("Car facts preparation completed.")
