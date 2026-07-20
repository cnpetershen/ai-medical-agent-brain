# Runtime API Spec

本文定义 Doctor Dashboard 调用 Runtime 的接口规格。本文只描述 API 契约，不开发前端，不修改 Runtime，不创建真实 API 服务。

## 设计原则

- API 面向医生工作台，而不是聊天机器人。
- Runtime 只执行 Agentic Workflow：信息整理、知识检索、草稿生成、随访任务与反馈回流。
- AI 输出默认是辅助草稿，不是诊断、处方或治疗方案。
- 医生确认是可信状态写入的前置条件。
- Memory 写回必须依赖 `doctor_confirmation_id`，不得由 AI 草稿直接触发。

## 通用对象

### Workflow State

```json
{
  "workflow_id": "pre_visit-SIM-HTN-001-20260720084830",
  "workflow_name": "pre_visit",
  "workflow_status": "running | completed | failed | rejected",
  "current_node": "doctor_review_pre_visit_summary",
  "patient_id": "SIM-HTN-001",
  "node_outputs": {},
  "doctor_confirmation": {},
  "memory_context": {},
  "audit_log": [],
  "started_at": "2026-07-20T08:48:30",
  "updated_at": "2026-07-20T08:48:30"
}
```

### Human Review Decision

`decision` 只能为：

- `approve`：医生采纳当前辅助草稿，允许后续可信状态写入。
- `modify`：医生修改 AI 草稿后采纳，后续只能使用医生修改后的内容。
- `reject`：医生拒绝当前辅助草稿，Workflow 不得写入可信 Memory。

### 通用安全限制

- 禁止自动诊断。
- 禁止自动处方。
- 禁止自动改药。
- 禁止自动修改治疗方案。
- 所有 Tool 调用、AI 输出、医生确认、Memory 写回必须进入 Audit。

## Workflow API

### POST /workflow/pre_visit

**用途**

启动诊前 Workflow，读取患者档案、风险画像、近期生命体征和连续照护 Memory，生成医生可审核的诊前摘要草稿与待确认问题。

**输入**

```json
{
  "patient_id": "SIM-HTN-001",
  "source": "patient_wang_001.json",
  "human_review_mode": "pending | simulated",
  "initial_decision": "approve | modify | reject"
}
```

`human_review_mode` 为 `pending` 时，Workflow 应在 HUMAN Node 等待医生确认；Demo Runtime 可使用 `simulated` 生成模拟确认。

**输出**

```json
{
  "workflow_id": "pre_visit-SIM-HTN-001-20260720084830",
  "workflow_name": "pre_visit",
  "workflow_status": "running | completed | failed | rejected",
  "patient_id": "SIM-HTN-001",
  "current_node": "doctor_review_pre_visit_summary",
  "outputs": {
    "structured_pre_visit_summary": {},
    "key_visit_questions": [],
    "missing_information_questions": [],
    "recent_health_overview": {},
    "confirmed_patient_context_for_during_visit": {}
  },
  "human_review_required": true
}
```

**调用 Workflow 节点**

- `load_pre_visit_context`
- `load_continuity_memory`
- `identify_key_and_missing_information`
- `generate_structured_pre_visit_summary`
- `doctor_review_pre_visit_summary`
- `write_confirmed_pre_visit_context`

**安全限制**

- 诊前摘要必须标记为 AI 辅助整理结果。
- `write_confirmed_pre_visit_context` 只能在 `doctor_review_pre_visit_summary` 返回 `approve` 或 `modify` 后执行。
- `reject` 时不得写入 Patient Memory。

### POST /workflow/during_visit

**用途**

启动诊中 Workflow，接收诊前 Workflow 的确认输出，执行 RAG 检索和 LLM 辅助整理，生成医生可审核的知识依据、诊中辅助结果与医嘱草稿。

**输入**

```json
{
  "patient_id": "SIM-HTN-001",
  "pre_visit_workflow_id": "pre_visit-SIM-HTN-001-20260720084830",
  "confirmed_pre_visit_context": {},
  "doctor_question_or_instruction": "请整理高血压复诊管理关注点",
  "human_review_mode": "pending | simulated",
  "initial_decision": "approve | modify | reject"
}
```

**输出**

```json
{
  "workflow_id": "during_visit-SIM-HTN-001-20260720084830",
  "workflow_name": "during_visit",
  "workflow_status": "running | completed | failed | rejected",
  "patient_id": "SIM-HTN-001",
  "outputs": {
    "knowledge_assistance_with_sources": [],
    "during_visit_information_summary": {},
    "clinical_note_or_progress_note_draft": {},
    "order_or_management_task_draft": {},
    "confirmed_items_for_post_visit_workflow": {}
  },
  "human_review_required": true
}
```

**调用 Workflow 节点**

- `load_during_visit_context`
- `load_confirmed_patient_memory`
- `determine_information_need`
- `retrieve_medical_knowledge`
- `organize_clinical_context`
- `generate_order_draft`
- `doctor_review_during_visit_output`
- `write_confirmed_during_visit_decisions`

**安全限制**

- RAG 结果必须带来源；检索失败时不得编造依据。
- `generate_order_draft` 输出只能是医生审核草稿，不是已生效医嘱。
- `write_confirmed_during_visit_decisions` 只能写入医生确认后的管理计划或关键判断点。

### POST /workflow/post_visit

**用途**

启动诊后 Workflow，接收诊中医生确认结果与 `followup_events.jsonl` 反馈事件，生成随访任务、患者反馈摘要、风险提示和下一次诊前上下文。

**输入**

```json
{
  "patient_id": "SIM-HTN-001",
  "during_visit_workflow_id": "during_visit-SIM-HTN-001-20260720084830",
  "confirmed_doctor_orders": {},
  "followup_events_source": "followup_events.jsonl",
  "human_review_mode": "pending | simulated",
  "initial_decision": "approve | modify | reject"
}
```

**输出**

```json
{
  "workflow_id": "post_visit-SIM-HTN-001-20260720084830",
  "workflow_name": "post_visit",
  "workflow_status": "running | completed | failed | rejected",
  "patient_id": "SIM-HTN-001",
  "outputs": {
    "patient_followup_tasks": [],
    "task_status_records": [],
    "abnormal_or_risk_flags": [],
    "confirmed_post_visit_feedback_summary": {},
    "next_pre_visit_context": {}
  },
  "human_review_required": true
}
```

**调用 Workflow 节点**

- `load_post_visit_inputs`
- `load_confirmed_post_visit_memory`
- `decompose_orders_into_tasks`
- `create_and_track_followup_tasks`
- `summarize_execution_and_flag_risks`
- `doctor_review_post_visit_status`
- `write_confirmed_post_visit_feedback`

**安全限制**

- `create_followup_tasks` 只能创建随访任务，不执行医疗行为。
- 患者反馈可以进入待审核状态，但异常摘要写入 Memory 前必须医生确认。
- `write_confirmed_post_visit_feedback` 只能在 `doctor_review_post_visit_status` 返回 `approve` 或 `modify` 后执行。

## Query API

### GET /patient/{patient_id}/profile

**用途**

为 Doctor Dashboard 查询患者基础档案、病史、当前用药、近期生命体征和上次就诊摘要。

**输入**

Path 参数：

- `patient_id`: 患者 ID，例如 `SIM-HTN-001`

Query 参数：

- `include_recent_vitals`: 可选，默认 `true`
- `include_risk_profile`: 可选，默认 `true`

**输出**

```json
{
  "patient_id": "SIM-HTN-001",
  "profile": {},
  "history": {},
  "current_medications": [],
  "recent_vitals": [],
  "risk_profile": {},
  "previous_visit_summary": {}
}
```

**调用 Workflow 节点**

- 对应工具能力：`get_patient_profile`
- 可补充调用：`get_recent_vitals`、`get_risk_profile`
- 不直接执行 Workflow 节点；供 `load_pre_visit_context`、`load_during_visit_context`、`load_post_visit_inputs` 展示复用。

**安全限制**

- 风险画像只用于医生关注优先级提示，不代表真实临床风险分层。
- 不输出诊断结论，不输出治疗决策。

### GET /patient/{patient_id}/memory

**用途**

查询医生确认后的 Patient Memory，用于展示连续照护上下文、Memory before / after 对照和下一次诊前回流信息。

**输入**

Path 参数：

- `patient_id`: 患者 ID，例如 `SIM-HTN-001`

Query 参数：

- `section`: 可选，`baseline_memory | pre_visit_memory | in_visit_memory | post_visit_memory | all`

**输出**

```json
{
  "patient_id": "SIM-HTN-001",
  "baseline_memory": {},
  "pre_visit_memory": {},
  "in_visit_memory": {},
  "post_visit_memory": {},
  "last_confirmation_id": "HITL-POST-001",
  "memory_update_rules": []
}
```

**调用 Workflow 节点**

- 对应工具能力：`get_patient_memory`
- 展示复用节点：`load_continuity_memory`、`load_confirmed_patient_memory`、`load_confirmed_post_visit_memory`

**安全限制**

- 该接口只读。
- 未经医生确认的 AI 草稿不得出现在可信 Memory 字段中。

### GET /workflow/{workflow_id}/state

**用途**

查询某次 Workflow 实例的运行状态，用于 Doctor Dashboard 展示当前阶段、节点执行顺序、节点输出、医生确认状态和 Memory 变化状态。

**输入**

Path 参数：

- `workflow_id`: Workflow 实例 ID

Query 参数：

- `include_node_outputs`: 可选，默认 `true`
- `include_memory_context`: 可选，默认 `true`

**输出**

```json
{
  "workflow_id": "during_visit-SIM-HTN-001-20260720084830",
  "workflow_name": "during_visit",
  "workflow_status": "completed",
  "current_node": "write_confirmed_during_visit_decisions",
  "patient_id": "SIM-HTN-001",
  "node_outputs": {},
  "doctor_confirmation": {
    "human_decision": "approve",
    "doctor_confirmation_id": "HITL-DURING-001"
  },
  "memory_context": {},
  "started_at": "2026-07-20T08:48:30",
  "updated_at": "2026-07-20T08:48:30"
}
```

**调用 Workflow 节点**

- 不触发节点执行。
- 读取 State Manager 保存的 Workflow Context。

**安全限制**

- 返回的 AI 输出必须保留草稿状态和确认状态。
- 若 Workflow 状态为 `rejected`，Dashboard 不得将其展示为已写入可信 Memory。

### GET /workflow/{workflow_id}/audit

**用途**

查询某次 Workflow 的审计日志，用于展示 Tool 调用、Memory 读写、AI 输出、医生确认和失败事件的可追溯记录。

**输入**

Path 参数：

- `workflow_id`: Workflow 实例 ID

Query 参数：

- `event_type`: 可选，`tool | memory | llm | human | error | all`

**输出**

```json
{
  "workflow_id": "post_visit-SIM-HTN-001-20260720084830",
  "audit_log": [
    {
      "tool_name": "get_followup_status",
      "input": {},
      "output": {},
      "workflow_stage": "post_visit",
      "workflow_node": "create_and_track_followup_tasks",
      "logged_at": "2026-07-20T08:48:30"
    }
  ]
}
```

**调用 Workflow 节点**

- 不触发节点执行。
- 读取 State Manager 保存的 `audit_log` 与运行日志。

**安全限制**

- 审计日志必须保留输入、输出、调用时间、Workflow 阶段和 Workflow 节点。
- 医生确认 ID 与 Memory 写回事件必须可关联。

## Human Review API

### POST /human-review/{workflow_id}

**用途**

提交医生对当前 Workflow HUMAN Node 的确认结果。该接口是从 AI 辅助草稿进入可信状态写入的唯一门禁。

**输入**

Path 参数：

- `workflow_id`: Workflow 实例 ID

Body：

```json
{
  "node_name": "doctor_review_during_visit_output",
  "decision": "approve | modify | reject",
  "doctor_id": "DOCTOR-DEMO-001",
  "modified_content": {},
  "review_comment": "医生已核对，仅作为随访管理任务草稿使用。"
}
```

字段规则：

- `decision=approve`：`modified_content` 可为空，后续使用 HUMAN Node 待确认内容。
- `decision=modify`：`modified_content` 必填，后续只能使用医生修改后的内容。
- `decision=reject`：不得执行后续可信 Memory 写回节点。

**输出**

```json
{
  "workflow_id": "during_visit-SIM-HTN-001-20260720084830",
  "node_name": "doctor_review_during_visit_output",
  "decision": "modify",
  "doctor_confirmation_id": "HITL-DURING-001",
  "next_action": "continue_workflow | stop_workflow",
  "memory_write_allowed": true
}
```

**调用 Workflow 节点**

- `doctor_review_pre_visit_summary`
- `doctor_review_during_visit_output`
- `doctor_review_post_visit_status`

确认通过或修改后，可继续触发对应写回节点：

- `write_confirmed_pre_visit_context`
- `write_confirmed_during_visit_decisions`
- `write_confirmed_post_visit_feedback`

**安全限制**

- `decision` 只能是 `approve`、`modify`、`reject`。
- `modify` 后写入 Memory 的内容必须来自 `modified_content`，不能来自原始 AI 草稿。
- `reject` 后 `memory_write_allowed=false`，不得调用 `update_patient_memory`。
- 该接口不得自动生成诊断、处方、改药或治疗方案修改。

## API 与 Dashboard 映射

| Dashboard 区域 | 主要 API | 展示内容 |
| --- | --- | --- |
| 诊前患者摘要 | `GET /patient/{patient_id}/profile` | 患者档案、病史、当前用药、近期血压 |
| 诊前 AI 整理结果 | `POST /workflow/pre_visit`、`GET /workflow/{workflow_id}/state` | 诊前摘要草稿、关键问题、缺失信息 |
| 诊中 RAG 参考依据 | `POST /workflow/during_visit`、`GET /workflow/{workflow_id}/state` | 知识片段、来源、辅助建议 |
| 诊中医嘱草稿 | `GET /workflow/{workflow_id}/state`、`POST /human-review/{workflow_id}` | 医生待确认草稿、确认状态 |
| 诊后随访与反馈 | `POST /workflow/post_visit`、`GET /workflow/{workflow_id}/state` | 随访任务、患者反馈事件、风险标记 |
| Memory 变化 | `GET /patient/{patient_id}/memory`、`GET /workflow/{workflow_id}/audit` | Memory before / after、写回确认 ID |
| 审计追溯 | `GET /workflow/{workflow_id}/audit` | Tool 调用、Memory 读写、医生确认 |

## Memory 写回门禁

可信 Memory 写回必须满足全部条件：

1. 当前 Workflow 已执行到对应 HUMAN Node。
2. 医生通过 `POST /human-review/{workflow_id}` 返回 `approve` 或 `modify`。
3. Runtime 生成 `doctor_confirmation_id`。
4. 写回节点调用 `update_patient_memory` 时带入 `doctor_confirmation_id`。
5. Audit 记录 Memory 写回的输入、输出、调用时间、Workflow 阶段和节点名称。

若任一条件不满足，API 必须返回拒绝写入状态：

```json
{
  "memory_write_allowed": false,
  "reason": "doctor_confirmation_required"
}
```

## 错误响应

```json
{
  "error_code": "workflow_not_found",
  "message": "Workflow instance not found.",
  "safe_to_continue": false
}
```

常见错误：

| error_code | 场景 | 处理方式 |
| --- | --- | --- |
| `patient_not_found` | 患者档案不存在 | 停止 Workflow，提示患者数据缺失 |
| `workflow_not_found` | Workflow ID 不存在 | 不返回伪造状态 |
| `invalid_human_decision` | decision 非法 | 拒绝确认请求 |
| `doctor_confirmation_required` | 缺少医生确认 | 禁止 Memory 写回 |
| `rag_result_missing` | RAG 未检索到来源 | 输出“未检索到充分来源”，不得编造 |
| `tool_failed` | 工具调用失败 | 写入 Audit，Dashboard 展示失败状态 |
| `memory_write_failed` | Memory 写回失败 | 不得假定写入成功 |

## 实施边界

本阶段只定义 API 规格。后续 Runtime API 实现时，应在现有 Runtime 之上增加适配层，不改变既有 Workflow Definition、Tool Contract、Node Runtime 和医生确认业务逻辑。
