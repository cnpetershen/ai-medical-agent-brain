from __future__ import annotations

import copy
import json
from datetime import datetime
from pathlib import Path
from typing import Any


class StateManager:
    """Tracks workflow context and execution logs for the runtime MVP."""

    def __init__(self, state_dir: Path) -> None:
        self.state_dir = state_dir
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def initialize_context(
        self,
        workflow_definition: dict[str, Any],
        patient_context: dict[str, Any],
        workflow_input: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        workflow_name = workflow_definition["workflow_name"]
        patient_id = patient_context["patient_id"]
        workflow_id = f"{workflow_name}-{patient_id}-{self._timestamp_for_id()}"
        context = {
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "workflow_status": "created",
            "current_node": None,
            "patient_id": patient_id,
            "patient_context": patient_context,
            "workflow_input": workflow_input or {},
            "memory_context": None,
            "node_outputs": {},
            "execution_log": [],
            "audit_log": [],
            "doctor_confirmation": None,
            "started_at": self._now(),
            "updated_at": self._now(),
        }
        self.log_event(context, f"Workflow started: {workflow_name} ({workflow_id})")
        self.save_context(context)
        return context

    def update_node(
        self,
        context: dict[str, Any],
        node_name: str,
        status: str,
        output: Any = None,
    ) -> None:
        context["current_node"] = node_name
        context["node_outputs"][node_name] = {
            "status": status,
            "output": output,
            "updated_at": self._now(),
        }
        context["updated_at"] = self._now()
        self.save_context(context)

    def log_event(self, context: dict[str, Any], message: str) -> None:
        entry = {"timestamp": self._now(), "message": message}
        context["execution_log"].append(entry)
        context["updated_at"] = entry["timestamp"]

    def log_audit(self, context: dict[str, Any], event: dict[str, Any]) -> None:
        record = copy.deepcopy(event)
        record["logged_at"] = self._now()
        context["audit_log"].append(record)
        context["updated_at"] = record["logged_at"]

    def finalize(self, context: dict[str, Any], status: str) -> None:
        context["workflow_status"] = status
        context["updated_at"] = self._now()
        self.log_event(context, f"Workflow finished with status: {status}")
        self.save_context(context)
        self.save_text_log(context)

    def save_context(self, context: dict[str, Any]) -> None:
        path = self.state_dir / f"{context['workflow_id']}.json"
        with path.open("w", encoding="utf-8") as handle:
            json.dump(context, handle, ensure_ascii=False, indent=2)

    def save_text_log(self, context: dict[str, Any]) -> None:
        path = self.state_dir / f"{context['workflow_id']}.log"
        with path.open("w", encoding="utf-8") as handle:
            for entry in context["execution_log"]:
                handle.write(f"[{entry['timestamp']}] {entry['message']}\n")

    @staticmethod
    def _now() -> str:
        return datetime.now().isoformat(timespec="seconds")

    @staticmethod
    def _timestamp_for_id() -> str:
        return datetime.now().strftime("%Y%m%d%H%M%S")
