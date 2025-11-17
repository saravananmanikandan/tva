# ~/Tva/vision-backend/server.py

import os
import json
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# NEW SDK
from google import genai
from google.genai import types

load_dotenv()

# -----------------------
# API KEY + CLIENT SETUP
# -----------------------
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
client = None

if not GEMINI_KEY:
    print("WARNING: GEMINI_API_KEY not set. Vision backend will run in dummy mode.")
else:
    try:
        client = genai.Client(api_key=GEMINI_KEY)
    except Exception as e:
        print("Failed to init GenAI client:", e)
        client = None

# -----------------------
# FASTAPI APP SETUP
# -----------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"status": "vision-backend-ok"}


# ---------------------------------------------------------
#  /analyze — actual traffic violation + OCR processing
# ---------------------------------------------------------
@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    """
    Accepts a multipart-form image upload and returns JSON with:
    - traffic violation flags
    - number plate OCR
    - vehicle type
    """

    img_bytes = await file.read()
    content_type = file.content_type or "image/jpeg"

    # If no API KEY → return a fake predictable result
    if not client:
        dummy = {
            "helmet_violation": True,
            "triple_riding": False,
            "overloaded": False,
            "seatbelt_violation": False,
            "mobile_use": False,
            "underage_driver": False,
            "number_plate": "TN00DEMO",
            "vehicle_type": "motorcycle",
            "summary": "Detected rider without helmet. Plate TN00DEMO.",
        }
        return {"vision_result": dummy}

    # Prompt for detection
    prompt = """
You are an advanced traffic violation detection system. Analyze the attached image.
Return a STRICT JSON with the following fields:

- helmet_violation: boolean
- triple_riding: boolean
- overloaded: boolean
- seatbelt_violation: boolean
- mobile_use: boolean
- underage_driver: boolean
- number_plate: string
- vehicle_type: "motorcycle" | "scooter" | "car" | "auto" | "unknown"
- summary: string (one sentence)

DO NOT return anything except valid JSON.
"""

    try:
        # Proper new-SDK multimodal call
        response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[
        prompt,
        types.Part.from_bytes(
            data=img_bytes,
            mime_type=content_type
        )
    ],
    config=types.GenerateContentConfig(
        response_mime_type="application/json"
    )
)

        raw_text = response.text or ""

    except Exception as e:
        return {
            "vision_result": {
                "error": "gemini_call_failed",
                "message": str(e),
            }
        }

    # Try parsing JSON
    try:
        parsed = json.loads(raw_text)
    except Exception:
        parsed = {"raw": raw_text}

    return {"vision_result": parsed}
