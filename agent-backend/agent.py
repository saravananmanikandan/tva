import os
import requests
from google.generativeai import Agent, tool

VISION_URL = os.getenv("VISION_URL")

@tool
def vision_analysis(image_url: str):
    """
    Fetch the image from Cloud Storage and send to vision-backend
    """
    img_bytes = requests.get(image_url).content

    r = requests.post(
        f"{VISION_URL}/analyze",
        files={"file": ("image.jpg", img_bytes, "image/jpeg")}
    )
    return r.json()
