from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_patient_profile(data_dir: Path, patient_id: str) -> dict[str, Any]:
    profile = _load_json(data_dir / "patient_wang_001.json")
    if profile["patient_id"] != patient_id:
        raise ValueError(f"Unknown patient_id for get_patient_profile: {patient_id}")
    return profile


def get_patient_memory(data_dir: Path, patient_id: str) -> dict[str, Any]:
    memory = _load_json(data_dir / "patient_memory_wang_001.json")
    if memory["patient_id"] != patient_id:
        raise ValueError(f"Unknown patient_id for get_patient_memory: {patient_id}")
    return memory


def get_risk_profile(data_dir: Path, patient_id: str) -> dict[str, Any]:
    profile = _load_json(data_dir / "risk_profile_wang_001.json")
    if profile["patient_id"] != patient_id:
        raise ValueError(f"Unknown patient_id for get_risk_profile: {patient_id}")
    return profile


def get_recent_vitals(data_dir: Path, patient_id: str, days: int) -> list[dict[str, Any]]:
    profile = get_patient_profile(data_dir, patient_id)
    vitals = profile.get("recent_vitals", [])
    return vitals[-days:] if days < len(vitals) else vitals


def update_patient_memory(
    data_dir: Path,
    patient_id: str,
    confirmed_memory_patch: dict[str, Any],
    doctor_confirmation_id: str,
) -> dict[str, Any]:
    if not doctor_confirmation_id:
        raise ValueError("doctor_confirmation_id is required for update_patient_memory")

    memory_path = data_dir / "patient_memory_wang_001.json"
    memory = get_patient_memory(data_dir, patient_id)
    before = copy.deepcopy(memory)

    for section_name, section_patch in confirmed_memory_patch.items():
        if not isinstance(section_patch, dict):
            continue
        current_section = memory.setdefault(section_name, {})
        current_section.update(section_patch)
        if section_name in {
            "pre_visit_memory",
            "in_visit_memory",
            "post_visit_memory",
        }:
            current_section["doctor_confirmed"] = True

    memory["last_confirmation_id"] = doctor_confirmation_id

    with memory_path.open("w", encoding="utf-8") as handle:
        json.dump(memory, handle, ensure_ascii=False, indent=2)

    return {
        "updated": True,
        "requires_doctor_confirmation": True,
        "before": before,
        "after": memory,
    }


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def get_followup_status(data_dir: Path, patient_id: str) -> list[dict[str, Any]]:
    events = _load_jsonl(data_dir / "followup_events.jsonl")
    return [event for event in events if event["patient_id"] == patient_id]


def record_patient_feedback(
    data_dir: Path,
    task_id: str,
    feedback: dict[str, Any],
) -> dict[str, Any]:
    return {
        "recorded": True,
        "task_id": task_id,
        "feedback": feedback,
        "source": "synthetic_demo_feedback",
    }


def create_followup_tasks(
    data_dir: Path,
    patient_id: str,
    confirmed_order: str,
) -> list[dict[str, Any]]:
    tasks = _load_jsonl(data_dir / "followup_tasks.jsonl")
    return [
        {
            **task,
            "patient_id": patient_id,
            "source_confirmed_order": confirmed_order,
        }
        for task in tasks
        if task["patient_id"] == patient_id
    ]
