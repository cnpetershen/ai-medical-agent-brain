from __future__ import annotations

import copy
from typing import Any


class HumanNode:
    """Simulates doctor review with approve / modify / reject decisions."""

    def __init__(self, default_decision: str = "approve") -> None:
        self.default_decision = default_decision

    def run(self, node: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        decision = context.get("human_decision_override", self.default_decision)
        if isinstance(decision, dict):
            decision = decision.get(context["workflow_name"], self.default_decision)

        latest_llm = self._latest_reviewable_output(context)
        confirmation_id = {
            "pre_visit": "HITL-PRE-001",
            "during_visit": "HITL-DURING-001",
            "post_visit": "HITL-POST-001",
        }.get(context["workflow_name"], "HITL-001")
        if decision == "modify":
            modified = copy.deepcopy(latest_llm)
            modified["doctor_note"] = "医生修改：请重点核对异常反馈与后续复诊安排。"
            return {
                "human_decision": "modify",
                "confirmed_content": modified,
                "doctor_confirmation_id": confirmation_id,
            }
        if decision == "reject":
            return {
                "human_decision": "reject",
                "rejection_reason": "医生拒绝当前草稿，需要补充或人工处理。",
                "doctor_confirmation_id": f"{confirmation_id}-REJECT",
            }
        return {
            "human_decision": "approve",
            "confirmed_content": latest_llm,
            "doctor_confirmation_id": confirmation_id,
        }

    @staticmethod
    def _latest_reviewable_output(context: dict[str, Any]) -> dict[str, Any]:
        preferred = {
            "pre_visit": "generate_structured_pre_visit_summary",
            "during_visit": "generate_order_draft",
            "post_visit": "summarize_execution_and_flag_risks",
        }.get(context["workflow_name"])
        if preferred and preferred in context["node_outputs"]:
            return context["node_outputs"][preferred]["output"]
        for record in reversed(list(context["node_outputs"].values())):
            if isinstance(record.get("output"), dict):
                return record["output"]
        return {}
