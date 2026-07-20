from __future__ import annotations

import copy
from typing import Any


class HumanNode:
    """Simulates doctor review with approve / modify / reject decisions."""

    def __init__(self, default_decision: str = "approve") -> None:
        self.default_decision = default_decision

    def run(self, node: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        decision = context.get("human_decision_override", self.default_decision)
        latest_llm = context["node_outputs"]["generate_structured_pre_visit_summary"][
            "output"
        ]
        if decision == "modify":
            modified = copy.deepcopy(latest_llm)
            modified["doctor_note"] = "医生补充：重点核对头晕频率与家庭血压测量方式。"
            return {
                "human_decision": "modify",
                "confirmed_content": modified,
                "doctor_confirmation_id": "HITL-PRE-001",
            }
        if decision == "reject":
            return {
                "human_decision": "reject",
                "rejection_reason": "医生认为摘要需补充更多诊前信息。",
                "doctor_confirmation_id": "HITL-PRE-REJECT-001",
            }
        return {
            "human_decision": "approve",
            "confirmed_content": latest_llm,
            "doctor_confirmation_id": "HITL-PRE-001",
        }

