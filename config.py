from pathlib import Path


ROOT = Path(__file__).resolve().parents[0]

DATA_DIR = ROOT / "data"

RAW_DATA_FILE = DATA_DIR / "raw" / "cars_24_combined.csv"
CLEAN_DATA_FILE = DATA_DIR / "cars_24_data.csv"

CAR_FACTS_FILE = DATA_DIR / "car_facts.json"
REPAIR_COSTS_FILE = DATA_DIR / "repair_costs.json"

WEB_SEARCH_MODEL = "gpt-6-luna"

FAISS_DIRECTORY = ROOT / "data" / "db" / "car_faiss_index"
