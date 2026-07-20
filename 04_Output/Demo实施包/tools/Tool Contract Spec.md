# Tool Contract Spec

本文基于 `04_Output/Demo实施包/dify/tool_schemas.json` 与已完成的 Workflow Definition，定义 Demo 阶段的工具契约。本文只描述工具使用边界，不创建 API，不开发 Runtime，不改变工具数量。

## 一、工具清单

现有工具共 9 个：

- `get_patient_profile`
- `get_patient_memory`
- `update_patient_memory`
- `get_risk_profile`
- `get_recent_vitals`
- `search_medical_knowledge`
- `create_followup_tasks`
- `record_patient_feedback`
- `get_followup_status`

## 二、每个工具定义

### get_patient_profile

`tool_name`：`get_patient_profile`

`purpose`：查询模拟患者档案、病史、当前用药和上次就诊摘要。

`workflow_usage`：诊前 Workflow 读取患者基础上下文；诊中 Workflow 可读取已确认患者资料作为辅助背景。

`used_by_nodes`：`load_pre_visit_context`、`load_during_visit_context`

`input_schema`：

```yaml
type: object
required:
  - patient_id
properties:
  patient_id:
    type: string
    example: SIM-HTN-001
```

`output_schema`：

```yaml
type: object
source_ref: ../data/patient_wang_001.json
contains:
  - patient_id
  - profile
  - history
  - current_medications
  - recent_vitals
  - previous_visit_summary
```

`permission`：read_only

`human_confirmation_required`：false

`audit_requirement`：记录输入、输出、调用时间、Workflow 阶段、调用节点。

`failure_handling`：若患者档案不可读取，返回 `data_not_found`；Workflow 应停止依赖患者档案的摘要生成，并提示数据缺失。

### get_patient_memory

`tool_name`：`get_patient_memory`

`purpose`：读取医生确认后的 Patient Memory，用于维持诊前、诊中、诊后的连续上下文。

`workflow_usage`：三大 Workflow 均可读取可信 Memory；读取结果只能作为上下文，不等同于新的医疗决定。

`used_by_nodes`：`load_continuity_memory`、`load_confirmed_patient_memory`、`load_confirmed_post_visit_memory`

`input_schema`：

```yaml
type: object
required:
  - patient_id
properties:
  patient_id:
    type: string
    example: SIM-HTN-001
```

`output_schema`：

```yaml
type: object
source_ref: ../data/patient_memory_wang_001.json
contains:
  - baseline_memory
  - pre_visit_memory
  - in_visit_memory
  - post_visit_memory
  - memory_update_rules
```

`permission`：read_only

`human_confirmation_required`：false

`audit_requirement`：记录输入、输出、调用时间、Workflow 阶段、调用节点。

`failure_handling`：若 Memory 读取失败，返回 `memory_read_failed`；允许继续生成辅助草稿，但必须提示连续上下文不完整。

### update_patient_memory

`tool_name`：`update_patient_memory`

`purpose`：在医生确认后写回 Patient Memory。未经医生确认的 AI 草稿不得调用该工具。

`workflow_usage`：用于写入医生确认后的诊前上下文、诊中管理计划或诊后反馈回流内容。

`used_by_nodes`：`write_confirmed_pre_visit_context`、`write_confirmed_during_visit_decisions`、`write_confirmed_post_visit_feedback`

`input_schema`：

```yaml
type: object
required:
  - patient_id
  - confirmed_memory_patch
  - doctor_confirmation_id
properties:
  patient_id:
    type: string
    example: SIM-HTN-001
  confirmed_memory_patch:
    type: object
    description: 医生确认后允许写回的记忆增量。
  doctor_confirmation_id:
    type: string
    example: HITL-POST-001
```

`output_schema`：

```yaml
type: object
properties:
  updated:
    type: boolean
  requires_doctor_confirmation:
    type: boolean
```

`permission`：write_confirmed_memory_only

`human_confirmation_required`：true

`audit_requirement`：必须记录输入、输出、调用时间、Workflow 阶段、调用节点、医生确认 ID、写回前后 Memory patch。

`failure_handling`：若缺少 `doctor_confirmation_id`，返回 `confirmation_required` 并禁止写入；若写入失败，返回 `memory_write_failed`，不得假定 Memory 已更新。

### get_risk_profile

`tool_name`：`get_risk_profile`

`purpose`：读取 Demo 风险画像，用于提示医生关注优先级；风险画像不代表真实临床风险分层。

`workflow_usage`：诊前用于提示医生复诊关注点；诊中用于辅助排序管理要点；诊后用于对比反馈后的风险变化草稿。

`used_by_nodes`：`load_pre_visit_context`、`load_during_visit_context`、`load_post_visit_inputs`

`input_schema`：

```yaml
type: object
required:
  - patient_id
properties:
  patient_id:
    type: string
    example: SIM-HTN-001
```

`output_schema`：

```yaml
type: object
source_ref: ../data/risk_profile_wang_001.json
contains:
  - overall_demo_risk_level
  - risk_dimensions
  - guardrail
```

`permission`：read_only

`human_confirmation_required`：false

`audit_requirement`：记录输入、输出、调用时间、Workflow 阶段、调用节点。

`failure_handling`：若风险画像不可读取，返回 `data_not_found`；Workflow 可继续，但必须提示风险画像缺失，不得编造风险分层。

### get_recent_vitals

`tool_name`：`get_recent_vitals`

`purpose`：查询模拟患者近期家庭血压记录。

`workflow_usage`：诊前用于生成近期健康状态概览；诊中可作为辅助上下文；诊后可与反馈状态对照。

`used_by_nodes`：`load_pre_visit_context`、`load_during_visit_context`、`load_post_visit_inputs`

`input_schema`：

```yaml
type: object
required:
  - patient_id
  - days
properties:
  patient_id:
    type: string
    example: SIM-HTN-001
  days:
    type: integer
    example: 14
```

`output_schema`：

```yaml
type: array
source_path: $.recent_vitals
items:
  type: object
  contains:
    - date
    - time
    - sbp
    - dbp
    - heart_rate
    - source
```

`permission`：read_only

`human_confirmation_required`：false

`audit_requirement`：记录输入、输出、调用时间、Workflow 阶段、调用节点。

`failure_handling`：若近期生命体征缺失，返回 `data_missing`；LLM 只能生成补充问题，不得推断不存在的数据。

### search_medical_knowledge

`tool_name`：`search_medical_knowledge`

`purpose`：检索高血压指南和药品说明书 Demo 知识片段，返回带来源的内容。

`workflow_usage`：诊中 Workflow 的 RAG 节点检索知识依据；诊前和诊后如需安全边界说明也可读取，但不得形成医疗决定。

`used_by_nodes`：`retrieve_medical_knowledge`

`input_schema`：

```yaml
type: object
required:
  - query
properties:
  query:
    type: string
    example: 高血压复诊 家庭血压 连续偏高 用药原则
```

`output_schema`：

```yaml
type: array
knowledge_file: ../data/knowledge_hypertension_demo.md
items:
  type: object
  contains:
    - title
    - source
    - content
    - retrieval_status
```

`permission`：read_only_rag

`human_confirmation_required`：false

`audit_requirement`：记录输入 query、输出片段、调用时间、Workflow 阶段、调用节点、知识来源。

`failure_handling`：若检索失败，返回 `rag_failed`；若无结果，返回 `no_retrieval_result`；不得编造来源或引用。

### create_followup_tasks

`tool_name`：`create_followup_tasks`

`purpose`：根据医生确认后的医嘱生成随访任务。该工具只能生成任务，不执行医疗行为。

`workflow_usage`：诊后 Workflow 将医生确认后的管理计划拆成随访任务。

`used_by_nodes`：`create_and_track_followup_tasks`

`input_schema`：

```yaml
type: object
required:
  - patient_id
  - confirmed_order
properties:
  patient_id:
    type: string
    example: SIM-HTN-001
  confirmed_order:
    type: string
    description: 医生确认后的医嘱或管理计划文本。
```

`output_schema`：

```yaml
type: array
source_ref: ../data/followup_tasks.jsonl
items:
  type: object
  contains:
    - task_id
    - patient_id
    - type
    - title
    - schedule
    - status
    - source
    - requires_doctor_confirmation
```

`permission`：create_task_from_confirmed_order_only

`human_confirmation_required`：true

`audit_requirement`：必须记录输入、输出、调用时间、Workflow 阶段、调用节点、医生确认后的医嘱来源。

`failure_handling`：若输入不是医生确认后的医嘱，返回 `confirmation_required`；若任务生成失败，返回 `tool_failed`，不得假定任务已创建。

### record_patient_feedback

`tool_name`：`record_patient_feedback`

`purpose`：记录患者对随访任务的执行反馈。

`workflow_usage`：诊后 Workflow 记录患者任务执行、症状变化和健康反馈，供后续摘要与医生审核使用。

`used_by_nodes`：`create_and_track_followup_tasks`

`input_schema`：

```yaml
type: object
required:
  - task_id
  - feedback
properties:
  task_id:
    type: string
    example: TASK-002
  feedback:
    type: object
```

`output_schema`：

```yaml
type: object
properties:
  recorded:
    type: boolean
```

`permission`：record_patient_reported_feedback

`human_confirmation_required`：false

`audit_requirement`：记录输入、输出、调用时间、Workflow 阶段、调用节点、反馈来源。

`failure_handling`：若记录失败，返回 `tool_failed`；不得假定反馈已保存，诊后摘要必须提示反馈记录不完整。

### get_followup_status

`tool_name`：`get_followup_status`

`purpose`：汇总 7 天随访执行状态、异常标记和可回流到下一次诊前的摘要。

`workflow_usage`：诊后 Workflow 读取任务执行状态和反馈事件，为异常标记、医生审核和 Memory 回流提供输入。

`used_by_nodes`：`load_post_visit_inputs`、`create_and_track_followup_tasks`

`input_schema`：

```yaml
type: object
required:
  - patient_id
properties:
  patient_id:
    type: string
    example: SIM-HTN-001
```

`output_schema`：

```yaml
type: array
source_ref: ../data/followup_events.jsonl
items:
  type: object
  contains:
    - event_id
    - patient_id
    - task_id
    - day
    - date
    - type
    - payload
    - agent_flag
    - doctor_review_required
```

`permission`：read_followup_status

`human_confirmation_required`：false

`audit_requirement`：记录输入、输出、调用时间、Workflow 阶段、调用节点。

`failure_handling`：若随访状态读取失败，返回 `tool_failed`；诊后 Workflow 不得生成完整执行结论，只能提示随访数据缺失。

## 三、Workflow与Tool映射

### 诊前 Workflow

| Workflow 节点 | Tool |
| --- | --- |
| `load_pre_visit_context` | `get_patient_profile` |
| `load_pre_visit_context` | `get_risk_profile` |
| `load_pre_visit_context` | `get_recent_vitals` |
| `load_continuity_memory` | `get_patient_memory` |
| `write_confirmed_pre_visit_context` | `update_patient_memory` |

### 诊中 Workflow

| Workflow 节点 | Tool |
| --- | --- |
| `load_during_visit_context` | `get_patient_profile` |
| `load_during_visit_context` | `get_risk_profile` |
| `load_during_visit_context` | `get_recent_vitals` |
| `load_confirmed_patient_memory` | `get_patient_memory` |
| `retrieve_medical_knowledge` | `search_medical_knowledge` |
| `write_confirmed_during_visit_decisions` | `update_patient_memory` |

### 诊后 Workflow

| Workflow 节点 | Tool |
| --- | --- |
| `load_post_visit_inputs` | `get_risk_profile` |
| `load_post_visit_inputs` | `get_recent_vitals` |
| `load_post_visit_inputs` | `get_followup_status` |
| `load_confirmed_post_visit_memory` | `get_patient_memory` |
| `create_and_track_followup_tasks` | `create_followup_tasks` |
| `create_and_track_followup_tasks` | `record_patient_feedback` |
| `create_and_track_followup_tasks` | `get_followup_status` |
| `write_confirmed_post_visit_feedback` | `update_patient_memory` |

## 四、医疗安全约束

1. `update_patient_memory` 必须经过医生确认。

该工具必须携带 `doctor_confirmation_id`。未经医生确认的 AI 草稿、患者自述、异常标记或医嘱草稿，不得写入可信 Patient Memory。

2. `create_followup_tasks` 只能生成任务，不执行医疗行为。

该工具只能基于医生确认后的医嘱或管理计划生成随访、提醒、记录类任务。它不得自动开方、自动改药、自动调整治疗方案，也不得向患者发出新的治疗决定。

3. 所有工具调用需要记录输入、输出、调用时间和 Workflow 阶段。

审计记录至少包含：

- tool_name
- input
- output
- called_at
- workflow_stage
- workflow_node
- patient_id 或 task_id
- doctor_confirmation_id，如果该工具需要医生确认

全局约束：

- 工具输出只作为 Workflow 上下文，不构成最终医疗结论。
- 风险画像只提示医生关注优先级，不代表真实临床风险分层。
- RAG 检索结果只作为参考依据，不替代医生判断。
- 任何写入可信 Memory 或进入诊后任务的内容，都必须来自医生确认结果。
