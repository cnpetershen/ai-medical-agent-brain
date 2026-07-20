from __future__ import annotations

from typing import Any

from tools.registry import ToolRegistry


class ToolNode:
    """Executes tool calls based on workflow-to-tool mapping."""

    def __init__(self, registry: ToolRegistry, state_manager: Any) -> None:
        self.registry = registry
        self.state_manager = state_manager

    def run(self, node: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        workflow_name = context["workflow_name"]
        node_name = node["node_name"]
        tool_names = self.registry.get_tools_for_node(workflow_name, node_name)
        if not tool_names:
            return {}

        outputs: dict[str, Any] = {}
        for tool_name in tool_names:
            if tool_name == "record_patient_feedback":
                outputs[tool_name] = self._record_all_feedback(context, workflow_name, node_name)
                continue
            payload = self._build_payload(tool_name, context)
            self.state_manager.log_event(
                context, f"Tool call: {tool_name} with input {payload}"
            )
            result = self.registry.execute(tool_name, payload)
            outputs[tool_name] = result
            self.state_manager.log_audit(
                context,
                {
                    "tool_name": tool_name,
                    "input": payload,
                    "output": result,
                    "workflow_stage": workflow_name,
                    "workflow_node": node_name,
                },
            )
        return outputs

    def _build_payload(self, tool_name: str, context: dict[str, Any]) -> dict[str, Any]:
        patient_id = context["patient_id"]
        if tool_name in {"get_patient_profile", "get_patient_memory", "get_risk_profile"}:
            return {"patient_id": patient_id}
        if tool_name == "get_recent_vitals":
            return {"patient_id": patient_id, "days": 14}
        if tool_name == "update_patient_memory":
            confirmation = context.get("doctor_confirmation") or {}
            llm_output = context["node_outputs"]["generate_structured_pre_visit_summary"][
                "output"
            ]
            patch = {
                "pre_visit_memory": {
                    "chief_complaint": llm_output["draft_text"],
                    "bp_pattern": llm_output["recent_vitals_trend"],
                    "adherence_signal": context["patient_context"]["current_medications"][0][
                        "adherence"
                    ],
                    "lifestyle_signal": context["patient_context"]["history"]["present_illness"],
                }
            }
            return {
                "patient_id": patient_id,
                "confirmed_memory_patch": patch,
                "doctor_confirmation_id": confirmation.get("doctor_confirmation_id", ""),
            }
        if tool_name == "get_followup_status":
            return {"patient_id": patient_id}
        if tool_name == "create_followup_tasks":
            during_context = context["workflow_input"].get("during_visit_context", {})
            confirmation = during_context.get("doctor_confirmation") or {}
            confirmed = confirmation.get("confirmed_content", {})
            return {
                "patient_id": patient_id,
                "confirmed_order": confirmed.get(
                    "confirmed_order",
                    "医生确认后的诊后管理计划",
                ),
            }
        raise NotImplementedError(f"Payload builder not implemented for {tool_name}")

    def _record_all_feedback(
        self,
        context: dict[str, Any],
        workflow_name: str,
        node_name: str,
    ) -> list[dict[str, Any]]:
        events = context["workflow_input"].get("followup_events", [])
        results = []
        for event in events:
            payload = {
                "task_id": event["task_id"],
                "feedback": event,
            }
            self.state_manager.log_event(
                context,
                f"Tool call: record_patient_feedback with input {payload}",
            )
            result = self.registry.execute("record_patient_feedback", payload)
            results.append(result)
            self.state_manager.log_audit(
                context,
                {
                    "tool_name": "record_patient_feedback",
                    "input": payload,
                    "output": result,
                    "workflow_stage": workflow_name,
                    "workflow_node": node_name,
                },
            )
        return results
