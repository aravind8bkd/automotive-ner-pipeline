"""Evaluate canonical entity IDs against labeled JSONL records."""

import argparse
import json
from pathlib import Path
from typing import Any

from automotive_ner.extractor import Extractor


def evaluate(input_path: Path, extractor: Extractor) -> dict[str, Any]:
    true_positive = false_positive = false_negative = 0
    rows = 0
    with input_path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{input_path}:{line_number}: invalid JSON: {error}") from error
            _, predictions = extractor.extract(record["text"])
            expected = {entity["canonical_id"] for entity in record.get("entities", [])}
            predicted = {entity["canonical_id"] for entity in predictions}
            true_positive += len(expected & predicted)
            false_positive += len(predicted - expected)
            false_negative += len(expected - predicted)
            rows += 1

    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "rows": rows,
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "micro_precision": precision,
        "micro_recall": recall,
        "micro_f1": f1,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/sample_reviews.jsonl"))
    args = parser.parse_args()
    print(json.dumps(evaluate(args.input, Extractor()), indent=2))


if __name__ == "__main__":
    main()
