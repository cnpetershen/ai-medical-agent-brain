from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


class WorkflowLoader:
    """Loads workflow definitions from the generated YAML specs."""

    def __init__(self, workflow_dir: Path) -> None:
        self.workflow_dir = workflow_dir

    def load(self, workflow_name: str) -> dict[str, Any]:
        path = self.workflow_dir / f"{workflow_name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Workflow definition not found: {path}")

        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)

        self._validate(data, path)
        return data

    def load_all(self) -> dict[str, dict[str, Any]]:
        workflows: dict[str, dict[str, Any]] = {}
        for path in sorted(self.workflow_dir.glob("*.yaml")):
            if path.name == "tool_contracts.yaml":
                continue
            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle)
            self._validate(data, path)
            workflows[data["workflow_name"]] = data
        return workflows

    @staticmethod
    def _validate(data: dict[str, Any], path: Path) -> None:
        required = {
            "workflow_name",
            "business_goal",
            "input_data",
            "nodes",
            "output_data",
            "hitl_confirmation_points",
        }
        missing = sorted(required.difference(data))
        if missing:
            raise ValueError(f"Workflow {path} missing fields: {missing}")

        valid_node_types = {"LLM", "RAG", "TOOL", "HUMAN", "MEMORY"}
        for node in data["nodes"]:
            node_type = node.get("node_type")
            if node_type not in valid_node_types:
                raise ValueError(
                    f"Workflow {path} has unsupported node type: {node_type}"
                )

