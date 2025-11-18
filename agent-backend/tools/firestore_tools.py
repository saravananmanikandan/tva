from google.cloud import firestore

db = firestore.Client()

def get_vehicle_details(plate: str):
    doc = db.collection("vehicles").document(plate).get()
    if doc.exists:
        return doc.to_dict()
    return {"error": "Vehicle not found"}

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
