"""FastAPI application for automotive component extraction."""

from fastapi import FastAPI

from automotive_ner.extractor import Extractor
from automotive_ner.schemas import Entity, ExtractionRequest, ExtractionResponse

app = FastAPI(title="Automotive NER API", version="0.1.0")
extractor = Extractor()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/extract", response_model=ExtractionResponse)
def extract(request: ExtractionRequest) -> ExtractionResponse:
    redacted_text, entities = extractor.extract(request.text)
    return ExtractionResponse(
        redacted_text=redacted_text,
        entities=[Entity(**entity) for entity in entities],
    )
