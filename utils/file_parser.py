import json
from pathlib import Path
import pandas as pd

def file_exists(file_path):
    return Path(file_path).exists()


def get_csv_file(file_path):
    try:
        data = pd.read_csv(file_path)
        return data
    except Exception:
        print("Exception occurred while fetching CSV data from path", file_path)
        raise


def get_json_file(file_path):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data
    except Exception as e:
        print("exception occurred while fetching json data from path ", file_path)
        raise e

def write_to_json(file_path, data):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        print("exception occurred while writing json data on path ", file_path)
        raise e
