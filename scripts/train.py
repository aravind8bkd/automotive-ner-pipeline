"""Validate labeled JSONL and write a dataset audit for the rule-based baseline."""

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def load_taxonomy(path: Path) -> set[str]:
    with path.open(encoding="utf-8") as file:
        taxonomy = json.load(file)
    return {component["id"] for component in taxonomy["components"]}


def audit_dataset(input_path: Path, taxonomy_ids: set[str]) -> dict[str, Any]:
    counts: Counter[str] = Counter()
    rows = 0
    with input_path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{input_path}:{line_number}: invalid JSON: {error}") from error
            if not isinstance(record.get("text"), str) or not record["text"]:
                raise ValueError(f"{input_path}:{line_number}: non-empty text is required")
            for entity in record.get("entities", []):
                component_id = entity.get("canonical_id")
                if component_id not in taxonomy_ids:
                    raise ValueError(
                        f"{input_path}:{line_number}: unknown canonical_id {component_id!r}"
                    )
                counts[component_id] += 1
            rows += 1
    return {"rows": rows, "entity_counts": dict(sorted(counts.items()))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/sample_reviews.jsonl"))
    parser.add_argument("--taxonomy", type=Path, default=Path("config/taxonomy.json"))
    parser.add_argument("--output", type=Path, default=Path("training_summary.json"))
    args = parser.parse_args()

    summary = audit_dataset(args.input, load_taxonomy(args.taxonomy))
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {summary['rows']} rows; wrote audit to {args.output}")
    print("The taxonomy-backed baseline has no learned model weights to train.")


if __name__ == "__main__":
    main()
