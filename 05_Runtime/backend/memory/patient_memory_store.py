from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


class PatientMemoryStore:
    """Handles runtime reads and writes for patient memory."""

    def __init__(self, memory_path: Path) -> None:
        self.memory_path = memory_path

    def read(self) -> dict[str, Any]:
        with self.memory_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def update_pre_visit_memory(
        self,
        patch: dict[str, Any],
        doctor_confirmation_id: str,
    ) -> dict[str, Any]:
        if not doctor_confirmation_id:
            raise ValueError("doctor_confirmation_id is required")

        current = self.read()
        before = copy.deepcopy(current)
        current["pre_visit_memory"].update(patch)
        current["pre_visit_memory"]["doctor_confirmed"] = True
        current["last_confirmation_id"] = doctor_confirmation_id

        with self.memory_path.open("w", encoding="utf-8") as handle:
            json.dump(current, handle, ensure_ascii=False, indent=2)

        return {"before": before, "after": current}

