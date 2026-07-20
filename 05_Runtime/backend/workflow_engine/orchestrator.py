from __future__ import annotations

from typing import Any

from nodes.human_node import HumanNode
from nodes.llm_node import LLMNode
from nodes.memory_node import MemoryNode
from nodes.rag_node import RAGNode
from nodes.tool_node import ToolNode


class Orchestrator:
    """Executes nodes according to the workflow definition."""

    def __init__(
        self,
        state_manager: Any,
        llm_node: LLMNode,
        rag_node: RAGNode,
        tool_node: ToolNode,
        human_node: HumanNode,
        memory_node: MemoryNode,
    ) -> None:
        self.state_manager = state_manager
        self.handlers = {
            "LLM": llm_node,
            "RAG": rag_node,
            "TOOL": tool_node,
            "HUMAN": human_node,
            "MEMORY": memory_node,
        }

    def run(
        self,
        workflow_definition: dict[str, Any],
        patient_context: dict[str, Any],
        human_decision: str = "approve",
    ) -> dict[str, Any]:
        context = self.state_manager.initialize_context(workflow_definition, patient_context)
        context["workflow_status"] = "running"
        context["human_decision_override"] = human_decision

        for node in workflow_definition["nodes"]:
            node_name = node["node_name"]
            node_type = node["node_type"]
            self.state_manager.log_event(
                context, f"Executing node: {node_name} ({node_type})"
            )
            handler = self.handlers[node_type]

            try:
                output = handler.run(node, context)
                if node_type == "LLM":
                    self.state_manager.log_event(
                        context, f"LLM output for {node_name}: {output}"
                    )
                if node_type == "HUMAN":
                    self.state_manager.log_event(
                        context, f"Human confirmation: {output['human_decision']}"
                    )
                    context["doctor_confirmation"] = output
                    if output["human_decision"] == "reject":
                        self.state_manager.update_node(context, node_name, "rejected", output)
                        self.state_manager.finalize(context, "rejected")
                        return context

                if node_type == "MEMORY" and node_name == "write_confirmed_pre_visit_context":
                    before = output["before"]["pre_visit_memory"]
                    after = output["after"]["pre_visit_memory"]
                    self.state_manager.log_event(
                        context,
                        "Memory change: "
                        f"before={before} -> after={after}",
                    )

                self.state_manager.update_node(context, node_name, "succeeded", output)
            except Exception as exc:  # noqa: BLE001
                self.state_manager.log_event(
                    context, f"Node failed: {node_name} error={exc}"
                )
                self.state_manager.update_node(
                    context,
                    node_name,
                    "failed",
                    {"error": str(exc)},
                )
                self.state_manager.finalize(context, "failed")
                return context

        self.state_manager.finalize(context, "completed")
        return context

