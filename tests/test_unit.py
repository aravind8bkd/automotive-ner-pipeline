import asyncio
import json
from pathlib import Path

import httpx
import pytest

from automotive_ner.api import app
from automotive_ner.extractor import Extractor
from automotive_ner.linker import EntityLinker
from automotive_ner.pii_guard import redact_pii

ROOT = Path(__file__).resolve().parents[1]


def load_taxonomy() -> dict:
    return json.loads((ROOT / "config" / "taxonomy.json").read_text(encoding="utf-8"))


def test_pii_guard_redacts_email_and_phone() -> None:
    redacted = redact_pii("Contact me at alex@example.com or 415-555-0132.")

    assert "alex@example.com" not in redacted
    assert "415-555-0132" not in redacted
    assert redacted.count("[REDACTED]") == 2


def test_linker_normalizes_case_and_punctuation() -> None:
    linker = EntityLinker(load_taxonomy())

    assert linker.link("BRAKE-PADS") == {
        "canonical_id": "brake_system",
        "canonical_name": "Brake system",
    }
    assert linker.link("unknown component") is None


def test_extractor_returns_offsets_into_redacted_text() -> None:
    extractor = Extractor(load_taxonomy())
    redacted, entities = extractor.extract("Email alex@example.com; BRAKE pads feel great.")

    assert "alex@example.com" not in redacted
    assert len(entities) == 1
    entity = entities[0]
    assert redacted[entity["start"]:entity["end"]] == entity["text"] == "BRAKE pads"


def test_linker_rejects_ambiguous_taxonomy_alias() -> None:
    taxonomy = {
        "components": [
            {"id": "part_a", "canonical_name": "Part A", "aliases": ["shared"]},
            {"id": "part_b", "canonical_name": "Part B", "aliases": ["shared"]},
        ]
    }

    with pytest.raises(ValueError, match="maps to multiple components"):
        EntityLinker(taxonomy)


def test_api_extracts_entities_and_does_not_return_pii() -> None:
    async def request():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                "/extract",
                json={"text": "Email alex@example.com; brake pads feel great."},
            )

    response = asyncio.run(request())
    assert response.status_code == 200
    result = response.json()
    assert "alex@example.com" not in result["redacted_text"]
    assert result["entities"][0]["canonical_id"] == "brake_system"
