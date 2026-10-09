from bootstrap.car_facts import prepare_car_facts
from bootstrap.data_prepration import prepare_cleaned_data
from bootstrap.database_prepration import load_data_in_vector_db
from bootstrap.repair_costs import prepare_repair_costs

def setup():
    clean_data = prepare_cleaned_data()
    prepare_car_facts()
    # load_data_in_vector_db(clean_data)
    prepare_repair_costs()

setup()
