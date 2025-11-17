from fastapi import FastAPI, UploadFile, File, Body, HTTPException
import os
import requests

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

# ----------------------
# NEW analyze_url endpoint
# ----------------------
@app.post("/analyze_url")
async def analyze_url(payload: dict = Body(...)):
    image_url = payload.get("url")
    if not image_url:
        raise HTTPException(status_code=400, detail="Missing field: url")

    if not VISION_URL:
        raise HTTPException(status_code=500, detail="VISION_URL not set")

    # Fetch the image
    try:
        r = requests.get(image_url, timeout=10)
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch image: {e}")

    content_type = r.headers.get("Content-Type", "image/jpeg")

    # Forward to Vision backend
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

    # Return JSON
    try:
        return resp.json()
    except:
        return {"vision_raw": resp.text}

