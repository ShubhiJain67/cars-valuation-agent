from langchain_core.documents import Document
from external.database.faiss import create_index

def load_data_in_vector_db(cars_data):
    documents = []

    for _, row in cars_data.iterrows():
        name = row["name"]

        content = (
            f"Used car listing: {name}. "
            f"Make: {row['make']}. "
            f"Model: {row['model']}. "
            f"Registration year: {row['year']}. "
            f"Kilometers driven: {row['km']}. "
            f"Previous owners: {row['owner']}. "
            f"Fuel: {row['fuel']}. "
            f"Transmission: {row['transmission']}. "
            f"Body type: {row['body_type']}. "
            f"Registration state: {row['state']}. "
            f"Used listing price: ₹{row['price']}. "
        )

        metadata = {
            "name": str(name),
            "make": str(row["make"]),
            "model": str(row["model"]),
            "year": int(row["year"]),
            "km": int(row["km"]),
            "owner": int(row["owner"]),
            "fuel": str(row["fuel"]),
            "transmission": str(row["transmission"]),
            "body_type": str(row["body_type"]),
            "state": str(row["state"]),
            "used_price": float(row["price"]),
        }

        documents.append(
            Document(
                page_content=content,
                metadata=metadata,
            )
        )

    create_index(documents)
    print(f"Loaded {len(documents)} cars into FAISS")
