from utils.file_parser import get_csv_file, file_exists
from config import RAW_DATA_FILE, CLEAN_DATA_FILE

def prepare_cleaned_data():
    if file_exists(CLEAN_DATA_FILE):
        print("clean data already exists")
        return get_csv_file(CLEAN_DATA_FILE)

    raw_data = get_csv_file(RAW_DATA_FILE)
    raw_data = raw_data.drop(columns=["Unnamed: 0"])
    raw_data = raw_data.rename(columns={
        "Car Name": "name",
        "Year": "year",
        "Distance": "km",
        "Owner": "owner",
        "Fuel": "fuel",
        "Location": "rto",
        "Drive": "transmission",
        "Type": "body_type",
        "Price": "price",
    })
    raw_data = raw_data.dropna(subset=["name", "year"])
    raw_data = raw_data[raw_data["km"] < 300_000]
    raw_data["year"] = raw_data["year"].astype(int)
    raw_data["make"] = raw_data["name"].str.split().str[0]           # "Maruti Swift" -> "Maruti"
    raw_data["model"] = raw_data["name"].str.split(n=1).str[1]       # "Maruti Swift" -> "Swift"
    raw_data["state"] = raw_data["rto"].str[:2]                      # "HR-26" -> "HR" (context only, not a filter)
    raw_data.to_csv(CLEAN_DATA_FILE, index=False)
    print(f"wrote {len(raw_data)} rows to {CLEAN_DATA_FILE}")
    return raw_data
