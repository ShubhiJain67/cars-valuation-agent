from datetime import date

from config import CAR_FACTS_FILE
from models.car_facts import CarFacts
from utils.file_parser import get_json_file
from llm.car_facts import search_fact

__CAR_FACTS = get_json_file(CAR_FACTS_FILE)

def get_facts(car):
    if car not in __CAR_FACTS:
        __CAR_FACTS[car] = search_fact(car).model_dump()
    return __CAR_FACTS[car]

def is_fact_valid(facts: CarFacts):
    if not facts.is_real_model:
        return False
    if facts.first_year is None:
        return False
    if facts.last_year is not None and facts.last_year < facts.first_year:
        return False
    if not (2000 <= facts.first_year <= date.today().year):
        return False
    if facts.ex_showroom_min is None or facts.ex_showroom_max is None:
        return False
    if facts.ex_showroom_max < facts.ex_showroom_min:
        return False
