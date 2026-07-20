from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from runtime_adapter import RuntimeAdapter


router = APIRouter(prefix="/workflow", tags=["Workflow State"])
runtime = RuntimeAdapter()


@router.get("/{workflow_id}/state")
def get_workflow_state(workflow_id: str) -> dict[str, Any]:
    try:
        return runtime.get_workflow_state(workflow_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{workflow_id}/audit")
def get_workflow_audit(workflow_id: str) -> dict[str, Any]:
    try:
        return runtime.get_workflow_audit(workflow_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
