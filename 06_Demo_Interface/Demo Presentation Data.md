# Demo Presentation Data

本文定义 Demo Presentation Layer 该消费哪些 Runtime 输出字段，并把它们映射为医生可理解的展示数据。

## 一、数据来源总览

Presentation Layer 只读取现有输出，不生成新的业务数据。

主要数据来源：

| 来源 | 用途 |
| --- | --- |
| `05_Runtime/backend/runtime_state/pre_visit-*.json` | 诊前展示数据 |
| `05_Runtime/backend/runtime_state/during_visit-*.json` | 诊中展示数据 |
| `05_Runtime/backend/runtime_state/post_visit-*.json` | 诊后展示数据 |
| `04_Output/Demo实施包/data/patient_memory_wang_001.json` | 最新可信 Patient Memory |
| `04_Output/Demo实施包/data/risk_profile_wang_001.json` | 风险画像展示 |
| `04_Output/Demo实施包/data/followup_tasks.jsonl` | 随访任务展示 |
| `04_Output/Demo实施包/data/followup_events.jsonl` | 患者反馈事件展示 |

## 二、诊前展示数据

### 诊前患者摘要卡

数据来源：

- `pre_visit.node_outputs.load_pre_visit_context.output.get_patient_profile`
- `pre_visit.node_outputs.generate_structured_pre_visit_summary.output`

字段映射：

| 展示字段 | 数据来源 |
| --- | --- |
| 患者姓名别名 | `profile.name_alias` |
| 年龄 | `profile.age` |
| 性别 | `profile.sex` |
| 就诊类型 | `profile.visit_type` |
| 本次主诉 | `profile.chief_complaint` |
| 当前用药 | `current_medication` |
| 近期血压趋势 | `recent_vitals_trend` |

### 风险画像卡

数据来源：

- `get_risk_profile`
- `risk_profile_wang_001.json`

字段映射：

| 展示字段 | 数据来源 |
| --- | --- |
| 总体风险提示 | `overall_demo_risk_level` |
| 风险维度列表 | `risk_dimensions[]` |
| 风险依据 | `risk_dimensions[].evidence` |
| 医生关注动作 | `risk_dimensions[].doctor_action` |

### AI整理结果卡

数据来源：

- `identify_key_and_missing_information.output`
- `generate_structured_pre_visit_summary.output`

字段映射：

| 展示字段 | 数据来源 |
| --- | --- |
| 关键事实 | `key_facts[]` |
| 风险线索 | `risk_signals[]` |
| AI诊前摘要草稿 | `draft_text` |
| 连续照护线索 | `continuous_care_clues` |

### 待确认信息卡

数据来源：

- `identify_key_and_missing_information.output.missing_questions`
- `doctor_review_pre_visit_summary.output`

字段映射：

| 展示字段 | 数据来源 |
| --- | --- |
| 待确认问题列表 | `missing_questions[]` |
| 医生确认结果 | `human_decision` |
| 医生确认 ID | `doctor_confirmation_id` |

## 三、诊中展示数据

### RAG参考依据卡

数据来源：

- `during_visit.node_outputs.retrieve_medical_knowledge.output.sections`

字段映射：

| 展示字段 | 数据来源 |
| --- | --- |
| 片段标题 | `sections[].title` |
| 片段内容摘要 | `sections[].content` |
| 检索状态 | `retrieval_status` |

### 辅助建议卡

数据来源：

- `during_visit.node_outputs.organize_clinical_context.output`

字段映射：

| 展示字段 | 数据来源 |
| --- | --- |
| 草稿类型 | `draft_type` |
| 诊中关键上下文 | `key_context[]` |
| 医生可核对管理方向 | `clinical_assistance[]` |
| 安全提示 | `safety_note` |

### 医嘱草稿卡

数据来源：

- `during_visit.node_outputs.generate_order_draft.output`

字段映射：

| 展示字段 | 数据来源 |
| --- | --- |
| 管理计划草稿 | `confirmed_order` |
| 辅助核对点 | `doctor_assistance[]` |
| 决策状态 | `medical_decision_status` |
| 安全提示 | `safety_note` |

### 医生确认状态卡

数据来源：

- `during_visit.node_outputs.doctor_review_during_visit_output.output`
- `patient_memory_wang_001.json.in_visit_memory`

字段映射：

| 展示字段 | 数据来源 |
| --- | --- |
| 确认结果 | `human_decision` |
| 医生确认 ID | `doctor_confirmation_id` |
| 是否已写入诊中 Memory | `in_visit_memory.doctor_confirmed` |
| 已确认管理计划 | `in_visit_memory.confirmed_management_plan` |

## 四、诊后展示数据

### 随访任务卡

数据来源：

- `post_visit.node_outputs.create_and_track_followup_tasks.output.create_followup_tasks`

字段映射：

| 展示字段 | 数据来源 |
| --- | --- |
| 任务 ID | `task_id` |
| 任务标题 | `title` |
| 任务类型 | `type` |
| 执行频率 | `schedule` |
| 当前状态 | `status` |
| 来源 | `source` |

### 患者反馈事件卡

数据来源：

- `post_visit.node_outputs.load_post_visit_inputs.output.get_followup_status`
- `post_visit.node_outputs.create_and_track_followup_tasks.output.record_patient_feedback`

字段映射：

| 展示字段 | 数据来源 |
| --- | --- |
| 事件日期 | `date` |
| 事件类型 | `type` |
| 反馈内容 | `payload` |
| agent flag | `agent_flag` |
| 是否需医生复核 | `doctor_review_required` |

### Memory变化卡

数据来源：

- `post_visit.node_outputs.write_confirmed_post_visit_feedback.output.before`
- `post_visit.node_outputs.write_confirmed_post_visit_feedback.output.after`

字段映射：

| 展示字段 | 数据来源 |
| --- | --- |
| 写回前 Memory | `before` |
| 写回后 Memory | `after` |
| 新增异常事件 | `after.post_visit_memory.abnormal_events` |
| 新增依从性摘要 | `after.post_visit_memory.task_adherence_summary` |
| 新增回流摘要 | `after.post_visit_memory.next_previsit_summary` |

展示建议：

- 默认不直接展示整份 JSON
- 应提炼成 before / after 差异视图

### 下一次诊前上下文卡

数据来源：

- `post_visit.node_outputs.summarize_execution_and_flag_risks.output.next_pre_visit_context`
- `patient_memory_wang_001.json.post_visit_memory.next_previsit_summary`

字段映射：

| 展示字段 | 数据来源 |
| --- | --- |
| 下一次诊前摘要 | `next_pre_visit_context` |
| 是否已写回可信 Memory | `post_visit_memory.doctor_confirmed` |
| 最后确认 ID | `last_confirmation_id` |

## 五、医生确认状态字段

展示层统一使用以下确认状态：

| 状态 | 数据来源 | 含义 |
| --- | --- | --- |
| `approve` | HUMAN Node 输出 | 医生认可当前草稿，可进入下一步 |
| `modify` | HUMAN Node 输出 | 医生修改后认可，展示应以修改后内容为准 |
| `reject` | HUMAN Node 输出 | 医生拒绝当前草稿，展示应标记为未进入下一阶段 |

## 六、连续照护闭环数据

Presentation Layer 必须显式展示以下闭环链路：

```text
诊前摘要
-> 诊中辅助建议
-> 医生确认后的管理计划
-> 诊后任务与反馈
-> Memory变化
-> 下一次诊前上下文
```

关键闭环字段：

| 闭环节点 | 关键字段 |
| --- | --- |
| 诊前 | `continuous_care_clues` |
| 诊中 | `confirmed_order` |
| 诊后 | `execution_summary`、`abnormal_events` |
| 回流 | `next_pre_visit_context`、`next_previsit_summary` |

## 七、展示层约束

- 不新增 Runtime 中不存在的数据。
- 不把 AI 草稿显示为最终诊断或最终处方。
- 不把工具结果显示为自动医疗决策。
- 不用聊天机器人会话流承载主展示。
- 必须让观众看见“AI辅助”和“医生确认”是两层不同状态。
