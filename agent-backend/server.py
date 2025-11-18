from fastapi import FastAPI, UploadFile, File, Body, HTTPException
import os
import requests
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware   # 👈 make sure this line exists
from tools.firestore_tools import log_user
from tools.firestore_tools import log_violation, get_vehicle_details
from tools.email_tools import send_violation_email

# Firestore tools
from tools.firestore_tools import log_violation, get_all_violations

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # you can also use ["https://your-front-url.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ----------------------
# Basic health endpoints
# ----------------------
@app.get("/")
def root():
    return {"status": "agent-backend-ok"}

@app.post("/register_user")
async def register_user(payload: dict = Body(...)):
    name = payload.get("name")
    plate = payload.get("plate")
    email = payload.get("email")

    if not name or not plate or not email:
        raise HTTPException(status_code=400, detail="Missing fields")

    try:
        log_user(name, plate, email)
        return {"status": "success", "message": "User added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/violations")
def get_violations():
    """
    Return a list of violations stored in Firestore.
    """
    try:
        violations = get_all_violations()
        return {"violations": violations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"health": "alive"}

# ----------------------
# Vision backend config
# ----------------------
VISION_URL = os.getenv("VISION_URL")
if not VISION_URL:
    print("WARNING: VISION_URL not set!")

# ----------------------
# TEMPORARY analyze endpoint (disabled logic)
# ----------------------
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    return {"message": "analyze disabled temporarily"}

# ------------------------------------------
# NEW analyze_url endpoint (with Firestore)
# ------------------------------------------
@app.post("/analyze_url")
async def analyze_url(payload: dict = Body(...)):
    image_url = payload.get("url")
    if not image_url:
        raise HTTPException(status_code=400, detail="Missing field: url")

    if not VISION_URL:
        raise HTTPException(status_code=500, detail="VISION_URL not set")

    try:
        r = requests.get(image_url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch image: {e}")

    content_type = r.headers.get("Content-Type", "image/jpeg")

    try:
        files = {
            "file": ("remote.jpg", r.content, content_type)
        }
        resp = requests.post(
            f"{VISION_URL.rstrip('/')}/analyze",
            files=files,
            timeout=30
        )
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Vision backend error: {e}")

    try:
        result = resp.json().get("vision_result", {})
    except Exception:
        return {"vision_raw": resp.text}

    # ----------------------
    # SAVE VIOLATION TO FIRESTORE
    # ----------------------
    severity = (
        int(result.get("helmet_violation", False))
        + int(result.get("triple_riding", False))
        + int(result.get("overloaded", False))
        + int(result.get("seatbelt_violation", False))
        + int(result.get("mobile_use", False))
        + int(result.get("underage_driver", False))
    )

    violation_entry = {
        "image_url": image_url,
        "number_plate": result.get("number_plate", ""),
        "vehicle_type": result.get("vehicle_type", "unknown"),
        "summary": result.get("summary", ""),
        "helmet_violation": result.get("helmet_violation"),
        "triple_riding": result.get("triple_riding"),
        "overloaded": result.get("overloaded"),
        "seatbelt_violation": result.get("seatbelt_violation"),
        "mobile_use": result.get("mobile_use"),
        "underage_driver": result.get("underage_driver"),
        "timestamp": datetime.utcnow().isoformat(),
        "status": "pending",
        "severity_score": severity
    }

    log_violation(violation_entry)

    # -------------------------
    # SEND EMAIL TO USER
    # -------------------------
    plate = result.get("number_plate", "")
    user_data = get_vehicle_details(plate)

    print(plate, "plate")

    email_status = {"status": "no_user_found"}

    if user_data and "email" in user_data:
        subject = f"Traffic Violation Detected – {plate}"
        body = f"""
Hi {user_data.get('name', 'User')},

A traffic violation has been detected involving your vehicle ({plate}).

Summary: {result.get('summary', 'No details')}
Severity Score: {severity}

Please review this violation and take necessary action.

Regards,
Traffic Vision Authority (TVA)
"""
        email_status = send_violation_email(user_data["email"], subject, body)

    # ----------------------
    # FINAL API RESPONSE
    # ----------------------
    return {
        "vision_result": result,
        "stored": True,
        "severity": severity,
        "email_status": email_status
    }
