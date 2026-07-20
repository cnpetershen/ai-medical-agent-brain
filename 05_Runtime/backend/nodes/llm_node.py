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
        if node_name == "determine_information_need":
            return {
                "mock": True,
                "information_needs": [
                    "诊前摘要中的血压趋势与症状变化",
                    "当前用药与依从性",
                    "家庭血压测量记录",
                    "相关高血压知识依据",
                ],
            }
        if node_name == "organize_clinical_context":
            return self._organize_clinical_context(context)
        if node_name == "generate_order_draft":
            return self._generate_order_draft(context)
        if node_name == "decompose_orders_into_tasks":
            return self._decompose_orders_into_tasks(context)
        if node_name == "summarize_execution_and_flag_risks":
            return self._summarize_execution(context)
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

    def _organize_clinical_context(self, context: dict[str, Any]) -> dict[str, Any]:
        pre_visit = context["workflow_input"].get("pre_visit_context", {})
        rag = context["node_outputs"].get("retrieve_medical_knowledge", {}).get(
            "output", {}
        )
        sections = rag.get("sections", [])
        return {
            "mock": True,
            "draft_type": "医生辅助信息草稿",
            "confirmed_pre_visit_status": pre_visit.get("workflow_status", "available"),
            "key_context": [
                "患者近期家庭血压多次偏高",
                "患者报告间断头晕",
                "当前存在漏服药线索",
            ],
            "knowledge_references": [section["title"] for section in sections],
            "clinical_assistance": [
                "请医生核对家庭血压记录的测量方式、时间和连续趋势。",
                "请医生核对头晕症状与血压变化、漏服药之间的时间关系。",
                "请医生结合检查结果和患者情况判断后续管理方向。",
            ],
            "safety_note": "仅供医生核对，不构成诊断或处方。",
        }

    def _generate_order_draft(self, context: dict[str, Any]) -> dict[str, Any]:
        assistance = context["node_outputs"]["organize_clinical_context"]["output"]
        return {
            "mock": True,
            "draft_type": "医嘱草稿",
            "doctor_assistance": assistance["clinical_assistance"],
            "confirmed_order": (
                "供医生确认的管理计划草稿：继续按医生确认方案进行规范管理，"
                "连续记录家庭血压，落实低盐饮食、规律作息和适度运动，"
                "异常情况提交医生复核。"
            ),
            "medical_decision_status": "待医生确认",
            "safety_note": "AI不自动开方、不自动改药、不自动修改治疗方案。",
        }

    def _decompose_orders_into_tasks(self, context: dict[str, Any]) -> dict[str, Any]:
        return {
            "mock": True,
            "task_plan_source": "医生确认后的管理计划",
            "task_categories": ["用药", "血压监测", "生活方式", "复查", "随访"],
            "safety_note": "任务拆解不执行医疗行为。",
        }

    def _summarize_execution(self, context: dict[str, Any]) -> dict[str, Any]:
        events = context["workflow_input"].get("followup_events", [])
        abnormal = [
            event
            for event in events
            if event.get("doctor_review_required") or event.get("agent_flag") in {
                "missed_medication",
                "abnormal_bp_or_symptom",
            }
        ]
        return {
            "mock": True,
            "execution_summary": {
                "event_count": len(events),
                "abnormal_event_count": len(abnormal),
                "abnormal_events": abnormal,
            },
            "risk_update_draft": [
                "血压控制风险：需要医生结合连续记录复核。",
                "用药依从性风险：随访期间出现 1 次漏服事件。",
                "症状变化风险：第 3 天头晕较前明显，后续减轻。",
            ],
            "next_pre_visit_context": (
                "上次诊后 7 天内完成多数反馈记录，出现 1 次漏服；"
                "第 3 天头晕较前明显，后续减轻；家庭血压多数仍偏高。"
            ),
            "doctor_confirmation_required": True,
            "safety_note": "仅供医生审核，不自动调整医嘱。",
        }
