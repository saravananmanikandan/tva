# ~/Tva/vision-backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY . .

# NEW SDK + Required libs
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    python-multipart \
    python-dotenv \
    google-genai \
    requests

EXPOSE 8080

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]
