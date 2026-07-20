from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from runtime_adapter import RuntimeAdapter


router = APIRouter(prefix="/patient", tags=["Patient"])
runtime = RuntimeAdapter()


@router.get("/{patient_id}/profile")
def get_patient_profile(
    patient_id: str,
    include_recent_vitals: bool = Query(default=True),
    include_risk_profile: bool = Query(default=True),
) -> dict[str, Any]:
    try:
        return runtime.get_patient_profile(
            patient_id,
            include_recent_vitals=include_recent_vitals,
            include_risk_profile=include_risk_profile,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{patient_id}/memory")
def get_patient_memory(
    patient_id: str,
    section: str = Query(default="all"),
) -> dict[str, Any]:
    try:
        return runtime.get_patient_memory(patient_id, section=section)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
