# Demo 实施包

本目录用于把 MiniMax3 的 Demo 方案落到可执行资产，目标是支撑 1 名高血压复诊模拟患者完成诊前、诊中、诊后和反馈回流演示。

## 阅读顺序

1. `落地评估与实施计划.md`
2. `Agent架构强化说明.md`
3. `dify/build_steps.md`
4. `dify/prompts.md`
5. `dify/tool_schemas.json`
6. `data/patient_wang_001.json`
7. `data/patient_memory_wang_001.json`
8. `data/risk_profile_wang_001.json`
9. `data/knowledge_hypertension_demo.md`
10. `data/followup_tasks.jsonl`
11. `data/followup_events.jsonl`
12. `演示脚本.md`
13. `验收清单.md`

## Demo 表达主线

不要展示功能清单，要展示王某的一次完整医疗旅程：诊前带着问题进入系统，诊中由医生确认管理计划，诊后产生真实执行反馈，最后这些反馈写入 Patient Memory 并更新风险画像，成为下一次诊前最重要的上下文。

## 使用边界

全部数据均为虚构模拟数据，仅用于 Demo。AI 输出只作为医生审核前的辅助草稿，不用于真实诊疗、诊断、处方或患者管理。
