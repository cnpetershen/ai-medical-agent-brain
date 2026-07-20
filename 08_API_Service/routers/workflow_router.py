from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from runtime_adapter import RuntimeAdapter


router = APIRouter(prefix="/workflow", tags=["Workflow"])
runtime = RuntimeAdapter()


class WorkflowRunRequest(BaseModel):
    patient_id: str = Field(default="SIM-HTN-001")
    decision: Literal["approve", "modify", "reject"] = "approve"
    source: str | None = None
    pre_visit_workflow_id: str | None = None
    during_visit_workflow_id: str | None = None
    confirmed_pre_visit_context: dict[str, Any] | None = None
    confirmed_doctor_orders: dict[str, Any] | None = None
    doctor_question_or_instruction: str | None = None


def _run(workflow_name: str, request: WorkflowRunRequest) -> dict[str, Any]:
    try:
        if hasattr(request, "model_dump"):
            payload = request.model_dump(exclude_none=True)
        else:
            payload = request.dict(exclude_none=True)
        return runtime.run_workflow(
            workflow_name,
            request.patient_id,
            payload,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/pre_visit")
def run_pre_visit(request: WorkflowRunRequest) -> dict[str, Any]:
    return _run("pre_visit", request)


@router.post("/during_visit")
def run_during_visit(request: WorkflowRunRequest) -> dict[str, Any]:
    return _run("during_visit", request)


@router.post("/post_visit")
def run_post_visit(request: WorkflowRunRequest) -> dict[str, Any]:
    return _run("post_visit", request)
