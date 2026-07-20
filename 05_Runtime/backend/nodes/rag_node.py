from __future__ import annotations

from pathlib import Path
from typing import Any


class RAGNode:
    """Minimal file-backed RAG node."""

    def __init__(self, knowledge_path: Path) -> None:
        self.knowledge_path = knowledge_path

    def run(self, node: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        with self.knowledge_path.open("r", encoding="utf-8") as handle:
            content = handle.read()
        sections = []
        for block in content.split("## ")[1:4]:
            title, _, body = block.partition("\n")
            sections.append({"title": title.strip(), "content": body.strip()})
        return {
            "mock": True,
            "node_name": node["node_name"],
            "retrieval_status": "succeeded",
            "sections": sections,
        }

