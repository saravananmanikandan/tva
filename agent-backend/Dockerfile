FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    google-cloud-firestore \
    google-cloud-storage \
    google-cloud-aiplatform \
    google-generativeai \
    python-dotenv \
    requests

EXPOSE 8080

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]

