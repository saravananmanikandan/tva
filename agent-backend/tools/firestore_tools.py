from google.cloud import firestore

db = firestore.Client()

def get_vehicle_details(plate: str):
    doc = db.collection("vehicles").document(plate).get()
    if doc.exists:
        return doc.to_dict()
    return {"error": "Vehicle not found"}

def log_violation(data: dict):
    db.collection("violations").add(data)
    return {"status": "logged"}
