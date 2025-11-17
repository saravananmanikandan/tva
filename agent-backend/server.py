from fastapi import FastAPI, UploadFile, File, Body, HTTPException
import os
import requests
from datetime import datetime

# Firestore tools
from tools.firestore_tools import log_violation

app = FastAPI()

# ----------------------
# Basic health endpoints
# ----------------------
@app.get("/")
def root():
    return {"status": "agent-backend-ok"}

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

    # ----------------------
    # Fetch the image
    # ----------------------
    try:
        r = requests.get(image_url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch image: {e}")

    content_type = r.headers.get("Content-Type", "image/jpeg")

    # ----------------------
    # Forward to Vision backend
    # ----------------------
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

    # Extract structured vision result
    try:
        result = resp.json().get("vision_result", {})
    except Exception:
        return {"vision_raw": resp.text}

    # ----------------------
    # SAVE VIOLATION INTO FIRESTORE
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

        # Violations
        "helmet_violation": result.get("helmet_violation"),
        "triple_riding": result.get("triple_riding"),
        "overloaded": result.get("overloaded"),
        "seatbelt_violation": result.get("seatbelt_violation"),
        "mobile_use": result.get("mobile_use"),
        "underage_driver": result.get("underage_driver"),

        # Auto fields
        "timestamp": datetime.utcnow().isoformat(),
        "status": "pending",
        "severity_score": severity
    }

    # Log into Firestore
    log_violation(violation_entry)

    # ----------------------
    # Return API result
    # ----------------------
    return {
        "vision_result": result,
        "stored": True,
        "severity": severity
    }
