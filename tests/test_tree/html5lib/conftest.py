from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Html5libTreeCase:
    fixture_file: str
    description: str
    data: str
    expected_tree: str
    context: str | None
    script_mode: str


def _parse_dat_file(path: Path) -> list[Html5libTreeCase]:
    """Parse an html5lib tree-construction ``.dat`` fixture file."""
    text = path.read_bytes().decode("utf-8", errors="replace")
    lines = text.splitlines()

    cases: list[Html5libTreeCase] = []
    current: dict[str, list[str] | str | None] = {
        "data": [],
        "document": [],
        "document-fragment": [],
    }
    section: str | None = None

    def flush_case() -> None:
        data_lines = current.get("data") or []
        expected_lines = current.get("document") or []
        if not data_lines and not expected_lines:
            return
        data = "\n".join(data_lines)
        expected_tree = "\n".join(expected_lines)
        context_lines = current.get("document-fragment") or []
        context = context_lines[0] if context_lines else None
        script_mode = str(current.get("script_mode") or "off")
        desc_lines = current.get("#errors") or []
        description = desc_lines[0] if desc_lines else data[:80]
        cases.append(
            Html5libTreeCase(
                fixture_file=path.name,
                description=description,
                data=data,
                expected_tree=expected_tree,
                context=context,
                script_mode=script_mode,
            )
        )

    for line in lines:
        if line.startswith("#"):
            marker = line[1:]
            if marker == "data":
                flush_case()
                current = {"data": [], "document": [], "document-fragment": []}
            section = marker
            if marker in {"script-on", "script-off"}:
                current["script_mode"] = "on" if marker == "script-on" else "off"
            continue

        if section is None:
            continue
        bucket = current.setdefault(section, [])
        if isinstance(bucket, list):
            bucket.append(line)

    flush_case()
    return cases
