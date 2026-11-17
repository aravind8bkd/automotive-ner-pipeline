"""Normalize mentions to canonical component IDs."""

import re
from typing import Any


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


class EntityLinker:
    """Resolve taxonomy aliases to their canonical component records."""

    def __init__(self, taxonomy: dict[str, Any]) -> None:
        self._components = {
            component["id"]: component for component in taxonomy.get("components", [])
        }
        self._aliases: dict[str, str] = {}
        for component_id, component in self._components.items():
            for alias in [component["canonical_name"], *component.get("aliases", [])]:
                normalized = _normalize(alias)
                existing = self._aliases.get(normalized)
                if existing is not None and existing != component_id:
                    raise ValueError(f"Taxonomy alias {alias!r} maps to multiple components")
                self._aliases[normalized] = component_id

    def link(self, mention: str) -> dict[str, str] | None:
        """Return the canonical record for a known mention, otherwise None."""
        component_id = self._aliases.get(_normalize(mention))
        if component_id is None:
            return None
        component = self._components[component_id]
        return {
            "canonical_id": component_id,
            "canonical_name": component["canonical_name"],
        }
