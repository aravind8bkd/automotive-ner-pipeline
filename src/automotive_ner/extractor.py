"""Taxonomy-backed phrase extraction with redacted-text offsets."""

import json
import re
from pathlib import Path
from typing import Any

from automotive_ner.linker import EntityLinker
from automotive_ner.pii_guard import redact_pii


def _default_taxonomy_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "taxonomy.json"


class Extractor:
    """Extract known automotive component aliases from review text."""

    def __init__(self, taxonomy: dict[str, Any] | None = None) -> None:
        if taxonomy is None:
            with _default_taxonomy_path().open(encoding="utf-8") as file:
                taxonomy = json.load(file)
        self._linker = EntityLinker(taxonomy)
        aliases: list[tuple[str, str]] = []
        for component in taxonomy.get("components", []):
            aliases.extend(
                (alias, component["id"])
                for alias in [component["canonical_name"], *component.get("aliases", [])]
            )
        aliases.sort(key=lambda item: len(item[0]), reverse=True)
        self._pattern = (
            re.compile(
                r"(?<!\w)(?:" + "|".join(re.escape(alias) for alias, _ in aliases) + r")(?!\w)",
                re.IGNORECASE,
            )
            if aliases
            else None
        )

    def extract(self, text: str) -> tuple[str, list[dict[str, Any]]]:
        """Return the redacted text and non-overlapping linked mentions."""
        redacted_text = redact_pii(text)
        if self._pattern is None:
            return redacted_text, []

        entities: list[dict[str, Any]] = []
        occupied_until = -1
        for match in self._pattern.finditer(redacted_text):
            if match.start() < occupied_until:
                continue
            linked = self._linker.link(match.group())
            if linked is None:
                continue
            entities.append(
                {
                    **linked,
                    "text": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                }
            )
            occupied_until = match.end()
        return redacted_text, entities
