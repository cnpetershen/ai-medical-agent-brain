from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "05_Runtime" / "backend"
DATA_DIR = REPO_ROOT / "04_Output" / "Demo实施包" / "data"
WORKFLOW_DIR = REPO_ROOT / "04_Output" / "Demo实施包" / "workflows"
STATE_DIR = BACKEND_DIR / "runtime_state"
REVIEW_DIR = Path(__file__).resolve().parent / "review_state"

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from demo_runner import build_runtime, load_jsonl, load_patient_context  # noqa: E402
from workflow_engine.workflow_loader import WorkflowLoader  # noqa: E402


class RuntimeAdapter:
    """Thin HTTP-facing adapter around the existing Runtime MVP."""

    valid_workflows = {"pre_visit", "during_visit", "post_visit"}
    valid_decisions = {"approve", "modify", "reject"}

    def __init__(self) -> None:
        self.workflow_loader = WorkflowLoader(WORKFLOW_DIR)
        REVIEW_DIR.mkdir(parents=True, exist_ok=True)

    def run_workflow(
        self,
        workflow_name: str,
        patient_id: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if workflow_name not in self.valid_workflows:
            raise ValueError(f"Unsupported workflow: {workflow_name}")

        payload = payload or {}
        decision = payload.get("decision") or payload.get("initial_decision") or "approve"
        if decision not in self.valid_decisions:
            raise ValueError(f"Invalid human decision: {decision}")

        patient_context = load_patient_context(BACKEND_DIR)
        if patient_context["patient_id"] != patient_id:
            raise ValueError(f"Unknown patient_id: {patient_id}")

        workflow_definition = self.workflow_loader.load(workflow_name)
        orchestrator = build_runtime(BACKEND_DIR)
        workflow_input = self._build_workflow_input(workflow_name, payload)
        result = orchestrator.run(
            workflow_definition,
            patient_context,
            human_decision={workflow_name: decision},
            workflow_input=workflow_input,
        )
        return self._workflow_response(result)

    def get_patient_profile(
        self,
        patient_id: str,
        include_recent_vitals: bool = True,
        include_risk_profile: bool = True,
    ) -> dict[str, Any]:
        profile = self._load_json(DATA_DIR / "patient_wang_001.json")
        if profile["patient_id"] != patient_id:
            raise ValueError(f"Unknown patient_id: {patient_id}")

        response = {
            "patient_id": profile["patient_id"],
            "profile": profile.get("profile", {}),
            "history": profile.get("history", {}),
            "current_medications": profile.get("current_medications", []),
            "previous_visit_summary": profile.get("previous_visit_summary", {}),
            "privacy_note": profile.get("privacy_note"),
        }
        if include_recent_vitals:
            response["recent_vitals"] = profile.get("recent_vitals", [])
        if include_risk_profile:
            response["risk_profile"] = self.get_risk_profile(patient_id)
        return response

    def get_patient_memory(self, patient_id: str, section: str = "all") -> dict[str, Any]:
        memory = self._load_json(DATA_DIR / "patient_memory_wang_001.json")
        if memory["patient_id"] != patient_id:
            raise ValueError(f"Unknown patient_id: {patient_id}")

        if section == "all":
            return memory
        if section not in memory:
            raise ValueError(f"Unknown memory section: {section}")
        return {
            "patient_id": patient_id,
            section: memory[section],
            "last_confirmation_id": memory.get("last_confirmation_id"),
        }

    def get_risk_profile(self, patient_id: str) -> dict[str, Any]:
        risk_profile = self._load_json(DATA_DIR / "risk_profile_wang_001.json")
        if risk_profile["patient_id"] != patient_id:
            raise ValueError(f"Unknown patient_id: {patient_id}")
        return risk_profile

    def get_workflow_state(self, workflow_id: str) -> dict[str, Any]:
        return self._load_state(workflow_id)

    def get_workflow_audit(self, workflow_id: str) -> dict[str, Any]:
        state = self._load_state(workflow_id)
        return {
            "workflow_id": workflow_id,
            "workflow_name": state.get("workflow_name"),
            "workflow_status": state.get("workflow_status"),
            "audit_log": state.get("audit_log", []),
            "execution_log": state.get("execution_log", []),
        }

    def submit_human_review(
        self,
        workflow_id: str,
        decision: str,
        doctor_id: str | None = None,
        modified_content: dict[str, Any] | None = None,
        review_comment: str | None = None,
    ) -> dict[str, Any]:
        if decision not in self.valid_decisions:
            raise ValueError(f"Invalid human decision: {decision}")
        if decision == "modify" and not modified_content:
            raise ValueError("modified_content is required when decision is modify")

        state = self._load_state(workflow_id)
        workflow_name = state["workflow_name"]
        confirmation_id = self._confirmation_id(workflow_name, decision)
        memory_write_allowed = decision in {"approve", "modify"}
        next_action = "continue_workflow" if memory_write_allowed else "stop_workflow"

        review_record = {
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "node_name": self._human_node_name(workflow_name),
            "decision": decision,
            "doctor_id": doctor_id or "DOCTOR-DEMO-001",
            "modified_content": modified_content,
            "review_comment": review_comment,
            "doctor_confirmation_id": confirmation_id,
            "memory_write_allowed": memory_write_allowed,
            "next_action": next_action,
            "safety_note": "医生确认仅打开可信写回门禁，不自动诊断、不自动处方、不自动改药。",
        }
        review_path = REVIEW_DIR / f"{workflow_id}.json"
        with review_path.open("w", encoding="utf-8") as handle:
            json.dump(review_record, handle, ensure_ascii=False, indent=2)
        return review_record

    def _build_workflow_input(
        self,
        workflow_name: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        if workflow_name == "pre_visit":
            return {"source": payload.get("source", "patient_wang_001.json")}

        if workflow_name == "during_visit":
            workflow_input: dict[str, Any] = {
                "doctor_question_or_instruction": payload.get(
                    "doctor_question_or_instruction",
                    "请整理高血压复诊管理关注点",
                )
            }
            pre_visit_workflow_id = payload.get("pre_visit_workflow_id")
            if pre_visit_workflow_id:
                workflow_input["pre_visit_context"] = self._load_state(pre_visit_workflow_id)
            if "confirmed_pre_visit_context" in payload:
                workflow_input["confirmed_pre_visit_context"] = payload[
                    "confirmed_pre_visit_context"
                ]
            return workflow_input

        workflow_input = {
            "followup_events": load_jsonl(DATA_DIR / "followup_events.jsonl"),
        }
        during_visit_workflow_id = payload.get("during_visit_workflow_id")
        if during_visit_workflow_id:
            workflow_input["during_visit_context"] = self._load_state(
                during_visit_workflow_id
            )
        if "confirmed_doctor_orders" in payload:
            workflow_input["confirmed_doctor_orders"] = payload[
                "confirmed_doctor_orders"
            ]
        return workflow_input

    def _load_state(self, workflow_id: str) -> dict[str, Any]:
        path = STATE_DIR / f"{workflow_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Workflow state not found: {workflow_id}")
        return self._load_json(path)

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @staticmethod
    def _workflow_response(state: dict[str, Any]) -> dict[str, Any]:
        return {
            "workflow_id": state["workflow_id"],
            "workflow_name": state["workflow_name"],
            "workflow_status": state["workflow_status"],
            "patient_id": state["patient_id"],
            "current_node": state["current_node"],
            "node_outputs": state["node_outputs"],
            "doctor_confirmation": state["doctor_confirmation"],
            "human_review_required": bool(state.get("doctor_confirmation")),
            "memory_context": state.get("memory_context"),
            "audit_log": state.get("audit_log", []),
            "started_at": state.get("started_at"),
            "updated_at": state.get("updated_at"),
        }

    @staticmethod
    def _human_node_name(workflow_name: str) -> str:
        return {
            "pre_visit": "doctor_review_pre_visit_summary",
            "during_visit": "doctor_review_during_visit_output",
            "post_visit": "doctor_review_post_visit_status",
        }[workflow_name]

    @staticmethod
    def _confirmation_id(workflow_name: str, decision: str) -> str:
        base_id = {
            "pre_visit": "HITL-PRE-001",
            "during_visit": "HITL-DURING-001",
            "post_visit": "HITL-POST-001",
        }[workflow_name]
        return f"{base_id}-REJECT" if decision == "reject" else base_id
