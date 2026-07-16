# Contributing

Thanks for your interest in improving Logo Error Checker!

## Getting set up

```bash
git clone https://github.com/simeonkolchin/logo-error-checker.git
cd logo-error-checker
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install ruff
cp .env.example .env   # add your tokens
```

Place the trained model weights in `app/ml/weights/` — see the [Model weights](README.md#-model-weights) section of the README. Most code paths load a model at import time, so nothing runs end-to-end without them.

## Ground rules

- **Never commit secrets or weights.** Tokens live in `.env` (gitignored); weights stay out of the repo.
- Keep each interface (API / bot / Streamlit) runnable from the repo root.
- New ML components go in `app/ml/` as a small class with a `predict()` / `run()` / `detect()` method, wired into `app/ml/ml.py`.
- Training code and experiments belong in `train/` as notebooks.

## Before opening a PR

- Run the linter: `ruff check .`
- Describe what changed in the pipeline behaviour and, where relevant, attach a before/after example image.

## Reporting bugs

Open an issue with the input image (or a description), the interface used (API / bot / UI), and the full report or traceback.
