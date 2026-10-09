from bootstrap.car_facts import prepare_car_facts
from bootstrap.data_prepration import prepare_cleaned_data
from bootstrap.repair_costs import prepare_repair_costs


def setup():
    prepare_cleaned_data()
    prepare_car_facts()
    prepare_repair_costs()


if __name__ == "__main__":
    setup()
