from google.cloud import firestore

db = firestore.Client()

# tools/firestore_tools.py

def get_vehicle_details(plate: str):
    try:
        # Normalize the plate format
        plate = plate.strip().upper()
        print("in_plate", plate)
        # Try to match by querying Firestore
        users_ref = db.collection("users")
        query = users_ref.where("plate", "==", plate).stream()

        print("query", query)

        for doc in query:
            return doc.to_dict()  # Return FIRST matching user

        print("No exact plate match, trying partial match...")

        # Try approximate match if needed (first 4 characters)
        partial_query = users_ref.where("plate", ">=", plate[:4]).where("plate", "<=", plate[:4] + "\uf8ff").stream()
        for doc in partial_query:
            return doc.to_dict()

        return None

    except Exception as e:
        print("🔥 Firestore plate lookup failed:", e)
        return None


def log_violation(data: dict):
    db.collection("violations").add(data)

def log_user(name: str, plate: str, email: str):
    db.collection("users").document(plate).set({
        "name": name,
        "plate": plate,
        "email": email
    })


def get_all_violations():
    """
    Returns list of violation documents sorted by timestamp (latest first).
    """
    try:
        docs = (
            db.collection("violations")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .stream()
        )
    except Exception:
        docs = db.collection("violations").stream()

    results = []
    for d in docs:
        item = d.to_dict()
        item["id"] = d.id
        results.append(item)

    return results
