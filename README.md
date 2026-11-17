# Automotive NER Pipeline

A small, auditable starting point for extracting automotive components from customer reviews and linking them to canonical part IDs. The production package uses a taxonomy-backed phrase matcher so it runs without downloading model weights; transformer experiments belong in the notebooks and are not loaded by the API.

## Architecture

- `src/automotive_ner/` contains the API contracts, PII guard, phrase extractor, canonical linker, and FastAPI app.
- `config/taxonomy.json` is the canonical vocabulary used by the rule-based baseline. Add aliases there; keep notebook experiments out of the production package.
- `data/sample_reviews.jsonl` is a sanitized, tiny fixture. Other files under `data/` are ignored by Git.
- `scripts/train.py` validates labeled JSONL and writes a training-data audit. The current rule-based baseline has no learned weights to train.
- `scripts/evaluate.py` compares extracted canonical IDs with labeled IDs and reports micro precision, recall, and F1.

## Quick start

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
python scripts/evaluate.py
python scripts/train.py --input data/sample_reviews.jsonl --output training_summary.json
uvicorn automotive_ner.api:app --reload
```

The API is available at `http://127.0.0.1:8000`; OpenAPI docs are at `/docs`.

## Benchmarks and trade-offs

Run `python scripts/evaluate.py` to generate metrics for the checked-in sample. That small, curated fixture is a smoke-test benchmark, not evidence of production accuracy. The phrase matcher is deterministic, fast, and easy to audit, but it cannot recognize unseen paraphrases or resolve context the taxonomy does not encode. The notebooks provide isolated places to compare rules with spaCy and DeBERTa before considering a model-backed production implementation.

## Safety and privacy

Email addresses and phone numbers are redacted before extraction. Returned offsets refer to the redacted text, which is returned alongside entities. This lightweight guard is not a substitute for a full privacy review; extend and test it for the data sources and jurisdictions in which the service will operate. Safety-critical parts are identified in the taxonomy, but the sample set is too small to establish safety-critical recall.
