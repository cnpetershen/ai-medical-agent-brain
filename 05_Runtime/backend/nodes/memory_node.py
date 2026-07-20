from __future__ import annotations

from typing import Any

from memory.patient_memory_store import PatientMemoryStore
from tools.registry import ToolRegistry


class MemoryNode:
    """Reads and writes patient memory for the runtime MVP."""

    def __init__(
        self,
        memory_store: PatientMemoryStore,
        tool_registry: ToolRegistry,
        state_manager: Any,
    ) -> None:
        self.memory_store = memory_store
        self.tool_registry = tool_registry
        self.state_manager = state_manager

    def run(self, node: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        node_name = node["node_name"]
        if node_name in {
            "load_continuity_memory",
            "load_confirmed_patient_memory",
            "load_confirmed_post_visit_memory",
        }:
            memory = self.memory_store.read()
            self.state_manager.log_event(context, "Memory read: patient_memory_wang_001.json")
            self.state_manager.log_audit(
                context,
                {
                    "memory_operation": "read",
                    "workflow_stage": context["workflow_name"],
                    "workflow_node": node_name,
                    "output": memory,
                },
            )
            context["memory_context"] = memory
            return memory

        if node_name in {
            "write_confirmed_pre_visit_context",
            "write_confirmed_during_visit_decisions",
            "write_confirmed_post_visit_feedback",
        }:
            before = self.memory_store.read()
            patch = self._build_patch(node_name, context)
            tool_payload = {
                "patient_id": context["patient_id"],
                "confirmed_memory_patch": patch,
                "doctor_confirmation_id": context["doctor_confirmation"][
                    "doctor_confirmation_id"
                ],
            }
            self.state_manager.log_event(
                context, f"Tool call: update_patient_memory with input {tool_payload}"
            )
            tool_result = self.tool_registry.execute("update_patient_memory", tool_payload)
            after = tool_result["after"]
            memory_change = {"before": before, "after": after}
            self.state_manager.log_audit(
                context,
                {
                    "memory_operation": "write",
                    "workflow_stage": context["workflow_name"],
                    "workflow_node": node_name,
                    "input": tool_payload,
                    "output": memory_change,
                },
            )
            context["memory_context"] = after
            return memory_change

        raise NotImplementedError(f"Memory node behavior not defined for {node_name}")

    @staticmethod
    def _build_patch(node_name: str, context: dict[str, Any]) -> dict[str, Any]:
        if node_name == "write_confirmed_pre_visit_context":
            summary = context["node_outputs"]["generate_structured_pre_visit_summary"][
                "output"
            ]
            return {
                "pre_visit_memory": {
                    "chief_complaint": context["patient_context"]["profile"][
                        "chief_complaint"
                    ],
                    "bp_pattern": summary["recent_vitals_trend"],
                    "adherence_signal": context["patient_context"][
                        "current_medications"
                    ][0]["adherence"],
                    "lifestyle_signal": "近期工作压力大、睡眠不足、饮食偏咸。",
                }
            }

        if node_name == "write_confirmed_during_visit_decisions":
            draft = context["node_outputs"]["generate_order_draft"]["output"]
            return {
                "in_visit_memory": {
                    "confirmed_management_plan": draft["confirmed_order"],
                    "confirmed_at": "runtime-demo",
                }
            }

        summary = context["node_outputs"]["summarize_execution_and_flag_risks"]["output"]
        return {
            "post_visit_memory": {
                "task_adherence_summary": summary["execution_summary"],
                "abnormal_events": summary["execution_summary"]["abnormal_events"],
                "next_previsit_summary": summary["next_pre_visit_context"],
                "confirmed_at": "runtime-demo",
            }
        }
