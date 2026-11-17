import json
from pathlib import Path

from automotive_ner.extractor import Extractor

ROOT = Path(__file__).resolve().parents[1]


def make_extractor() -> Extractor:
    taxonomy = json.loads((ROOT / "config" / "taxonomy.json").read_text(encoding="utf-8"))
    return Extractor(taxonomy)


def test_entity_extraction_is_case_invariant() -> None:
    extractor = make_extractor()

    _, lower = extractor.extract("The brake pads squeak.")
    _, upper = extractor.extract("THE BRAKE PADS SQUEAK.")

    assert [entity["canonical_id"] for entity in lower] == ["brake_system"]
    assert [entity["canonical_id"] for entity in upper] == ["brake_system"]


def test_safety_critical_parts_are_recalled_in_sample_phrasings() -> None:
    extractor = make_extractor()
    reviews = [
        "The brake pedal feels soft.",
        "The side airbag warning light is on.",
        "The steering wheel vibrates.",
        "The seatbelt will not latch.",
    ]
    expected = {"brake_system", "airbag", "steering_system", "seat_belt"}

    found = {
        entity["canonical_id"]
        for review in reviews
        for entity in extractor.extract(review)[1]
    }

    safety_critical_recall = len(expected & found) / len(expected)
    assert safety_critical_recall >= 0.95
