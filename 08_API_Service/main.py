from __future__ import annotations

from fastapi import FastAPI

from routers.human_review_router import router as human_review_router
from routers.patient_router import router as patient_router
from routers.workflow_router import router as workflow_router
from routers.workflow_state_router import router as workflow_state_router


app = FastAPI(
    title="AI Medical Agentic Workflow Runtime API",
    version="demo-v1",
    description=(
        "HTTP API for the doctor-led medical Agentic Workflow Runtime. "
        "AI outputs are auxiliary drafts and require doctor confirmation "
        "before trusted Memory writeback."
    ),
)

app.include_router(workflow_router)
app.include_router(patient_router)
app.include_router(workflow_state_router)
app.include_router(human_review_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "runtime-api-service",
        "safety": "doctor_confirmation_required_before_memory_write",
    }
