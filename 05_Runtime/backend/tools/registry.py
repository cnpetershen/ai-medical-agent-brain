from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import yaml

from tools.patient_tools import (
    get_patient_memory,
    get_patient_profile,
    get_recent_vitals,
    get_risk_profile,
    update_patient_memory,
)


class ToolRegistry:
    """Loads tool contracts and exposes executable tool functions."""

    def __init__(self, contracts_path: Path, data_dir: Path) -> None:
        self.contracts_path = contracts_path
        self.data_dir = data_dir
        self.contracts = self._load_contracts()
        self.mapping = self.contracts["workflow_tool_mapping"]
        self.functions: dict[str, Callable[..., Any]] = {
            "get_patient_profile": get_patient_profile,
            "get_patient_memory": get_patient_memory,
            "get_risk_profile": get_risk_profile,
            "get_recent_vitals": get_recent_vitals,
            "update_patient_memory": update_patient_memory,
        }

    def get_tools_for_node(self, workflow_name: str, node_name: str) -> list[str]:
        return self.mapping.get(workflow_name, {}).get(node_name, [])

    def get_contract(self, tool_name: str) -> dict[str, Any]:
        for tool in self.contracts["tools"]:
            if tool["tool_name"] == tool_name:
                return tool
        raise KeyError(f"Tool contract not found for {tool_name}")

    def execute(self, tool_name: str, payload: dict[str, Any]) -> Any:
        if tool_name not in self.functions:
            raise NotImplementedError(f"Tool not implemented in MVP: {tool_name}")
        return self.functions[tool_name](self.data_dir, **payload)

    def _load_contracts(self) -> dict[str, Any]:
        with self.contracts_path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)

