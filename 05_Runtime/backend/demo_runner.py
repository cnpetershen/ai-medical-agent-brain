from __future__ import annotations

import json
from pathlib import Path

from memory.patient_memory_store import PatientMemoryStore
from nodes.human_node import HumanNode
from nodes.llm_node import LLMNode
from nodes.memory_node import MemoryNode
from nodes.rag_node import RAGNode
from nodes.tool_node import ToolNode
from tools.registry import ToolRegistry
from workflow_engine.orchestrator import Orchestrator
from workflow_engine.state_manager import StateManager
from workflow_engine.workflow_loader import WorkflowLoader


def build_runtime(base_dir: Path) -> Orchestrator:
    repo_root = base_dir.parent.parent
    spec_dir = repo_root / "04_Output" / "Demo实施包"
    workflow_dir = spec_dir / "workflows"
    data_dir = spec_dir / "data"
    contracts_path = spec_dir / "tools" / "tool_contracts.yaml"
    knowledge_path = data_dir / "knowledge_hypertension_demo.md"
    memory_path = data_dir / "patient_memory_wang_001.json"
    state_dir = base_dir / "runtime_state"

    state_manager = StateManager(state_dir)
    tool_registry = ToolRegistry(contracts_path=contracts_path, data_dir=data_dir)
    memory_store = PatientMemoryStore(memory_path=memory_path)

    return Orchestrator(
        state_manager=state_manager,
        llm_node=LLMNode(),
        rag_node=RAGNode(knowledge_path=knowledge_path),
        tool_node=ToolNode(tool_registry, state_manager),
        human_node=HumanNode(default_decision="approve"),
        memory_node=MemoryNode(memory_store, tool_registry, state_manager),
    )


def load_patient_context(base_dir: Path) -> dict:
    repo_root = base_dir.parent.parent
    patient_path = repo_root / "04_Output" / "Demo实施包" / "data" / "patient_wang_001.json"
    with patient_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    repo_root = base_dir.parent.parent
    workflow_loader = WorkflowLoader(
        repo_root / "04_Output" / "Demo实施包" / "workflows"
    )
    workflow_definition = workflow_loader.load("pre_visit")
    patient_context = load_patient_context(base_dir)
    orchestrator = build_runtime(base_dir)
    result = orchestrator.run(workflow_definition, patient_context, human_decision="approve")

    print("=" * 80)
    print("Workflow Execution Log")
    print("=" * 80)
    for entry in result["execution_log"]:
        print(f"[{entry['timestamp']}] {entry['message']}")

    print("\n" + "=" * 80)
    print("Workflow Final Status")
    print("=" * 80)
    print(
        json.dumps(
            {
                "workflow_id": result["workflow_id"],
                "workflow_name": result["workflow_name"],
                "workflow_status": result["workflow_status"],
                "current_node": result["current_node"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
