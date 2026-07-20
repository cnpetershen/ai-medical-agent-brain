from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from runtime_adapter import RuntimeAdapter


router = APIRouter(tags=["Human Review"])
runtime = RuntimeAdapter()


class HumanReviewRequest(BaseModel):
    node_name: str | None = None
    decision: Literal["approve", "modify", "reject"]
    doctor_id: str | None = "DOCTOR-DEMO-001"
    modified_content: dict[str, Any] | None = None
    review_comment: str | None = None


@router.post("/human-review/{workflow_id}")
def submit_human_review(
    workflow_id: str,
    request: HumanReviewRequest,
) -> dict[str, Any]:
    try:
        return runtime.submit_human_review(
            workflow_id=workflow_id,
            decision=request.decision,
            doctor_id=request.doctor_id,
            modified_content=request.modified_content,
            review_comment=request.review_comment,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
