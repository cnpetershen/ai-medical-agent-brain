from __future__ import annotations

from typing import Any


class LLMNode:
    """Mock LLM node for the MVP runtime."""

    def run(self, node: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        node_name = node["node_name"]
        patient = context["patient_context"]
        if node_name == "identify_key_and_missing_information":
            return self._identify_key_information(patient, context)
        if node_name == "generate_structured_pre_visit_summary":
            return self._generate_pre_visit_summary(patient, context)
        return {
            "mock": True,
            "node_name": node_name,
            "message": f"Mock output generated for {node_name}",
        }

    def _identify_key_information(
        self,
        patient: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        vitals = context["node_outputs"].get("load_pre_visit_context", {}).get(
            "output", {}
        ).get("get_recent_vitals", [])
        latest = vitals[-1] if vitals else {}
        return {
            "mock": True,
            "key_facts": [
                patient["profile"]["chief_complaint"],
                patient["history"]["present_illness"],
                f"当前用药：{patient['current_medications'][0]['name']} {patient['current_medications'][0]['dose']}",
                f"最近一次家庭血压：{latest.get('sbp', 'N/A')}/{latest.get('dbp', 'N/A')} mmHg",
            ],
            "risk_signals": [
                "近两周家庭血压持续偏高",
                "存在漏服药情况",
                "近期睡眠不足、饮食偏咸",
            ],
            "missing_questions": [
                "头晕出现的时间、频率和持续时长如何？",
                "近期是否有胸闷、胸痛或视物模糊？",
                "家庭血压测量是否固定在晨起和晚间进行？",
            ],
        }

    def _generate_pre_visit_summary(
        self,
        patient: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        tool_output = context["node_outputs"]["load_pre_visit_context"]["output"]
        memory_output = context["node_outputs"]["load_continuity_memory"]["output"]
        analysis = context["node_outputs"]["identify_key_and_missing_information"][
            "output"
        ]
        risk_profile = tool_output["get_risk_profile"]
        recent_vitals = tool_output["get_recent_vitals"]
        trend = ", ".join(
            [f"{item['date']} {item['sbp']}/{item['dbp']}" for item in recent_vitals[-3:]]
        )

        return {
            "mock": True,
            "summary_title": "诊前摘要草稿",
            "patient_alias": patient["profile"]["name_alias"],
            "continuous_care_clues": memory_output["pre_visit_memory"],
            "basic_information": patient["profile"],
            "current_medication": patient["current_medications"],
            "recent_vitals_trend": trend,
            "risk_prompt": risk_profile["overall_demo_risk_level"],
            "key_questions": analysis["missing_questions"],
            "doctor_confirmation_required": True,
            "draft_text": (
                f"{patient['profile']['name_alias']}，{patient['profile']['age']}岁，"
                f"{patient['profile']['visit_type']}。近两周家庭血压偏高并伴间断头晕，"
                "近期存在漏服药、睡眠不足和饮食偏咸等线索。"
            ),
        }

