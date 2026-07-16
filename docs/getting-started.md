# Getting Started

This guide walks you from a clone to a running interface.

## 1. Prerequisites

- Python 3.10+
- ~2 GB free disk (EasyOCR + Ultralytics pull in PyTorch)
- The five trained model weights (see step 3)
- A Telegram bot token and (optionally) a Yandex Disk token, only for the bot

## 2. Install

```bash
git clone https://github.com/simeonkolchin/logo-error-checker.git
cd logo-error-checker
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

> `requirements.txt` is a full environment freeze. If you only need the API, the core packages are: `fastapi`, `uvicorn`, `ultralytics`, `onnxruntime`, `easyocr`, `python-Levenshtein`, `opencv-python`, `pillow`, `numpy`, `torch`, `torchvision`. The bot additionally needs `aiogram`, `pandas`, `openpyxl`, `yadisk`; the UI needs `streamlit`.

## 3. Add model weights

The pipeline loads five files from `app/ml/weights/` (empty in the repo):

```
app/ml/weights/
├── logo_detector.pt
├── search_people.pt
├── classification_crop.onnx
├── classification_direction.onnx
└── classification_check_good.onnx
```

Obtain them by training with the notebooks in [`train/`](../train) or by requesting the pre-trained set from the maintainer. See the README's [Model weights](../README.md#-model-weights) section.

## 4. Configure secrets

```bash
cp .env.example .env
```

Fill in `TELEGRAM_BOT_TOKEN` (and `YANDEX_DISK_TOKEN` if you use the bot's archive feature), then export them into your shell:

```bash
export $(grep -v '^#' .env | xargs)
```

## 5. Run an interface (from the repo root)

**REST API**

```bash
uvicorn app.api.api:app --host 0.0.0.0 --port 8000
# POST an image:
curl -X POST "http://localhost:8000/check_errors/" -F "file=@example.jpg"
```

**Streamlit UI**

```bash
streamlit run app/ui/layout.py
```

**Telegram bot**

```bash
PYTHONPATH=. python app/bot/telegram_bot.py
```

The bot creates a local SQLite database (`branding_photos.db`) on first run and, when a photo is accepted, uploads it to Yandex Disk and records the metadata.

## 6. Docker (API)

```bash
docker build -t logo-error-checker .
docker run --rm -p 8000:8000 --env-file .env \
  -v "$PWD/app/ml/weights:/app/app/ml/weights" logo-error-checker
```

Mounting the weights directory keeps the (large) model files out of the image.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `FileNotFoundError` / ONNX load error on startup | Weights are missing from `app/ml/weights/`. |
| `RuntimeError: TELEGRAM_BOT_TOKEN is not set` | Export the variable or check your `.env`. |
| `ModuleNotFoundError: app` when running the bot | Run from the repo root with `PYTHONPATH=.`. |
| EasyOCR downloads models on first run | Expected — it caches detection/recognition weights on first use. |
