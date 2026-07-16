# Logo Error Checker — API image.
# Model weights are NOT baked in; mount app/ml/weights/ at runtime.
FROM python:3.11-slim

# System libraries required by OpenCV / EasyOCR / Ultralytics.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libglib2.0-0 \
        libgl1 \
        libsm6 \
        libxext6 \
        libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Serve the FastAPI app. Mount weights: -v "$PWD/app/ml/weights:/app/app/ml/weights"
CMD ["uvicorn", "app.api.api:app", "--host", "0.0.0.0", "--port", "8000"]
