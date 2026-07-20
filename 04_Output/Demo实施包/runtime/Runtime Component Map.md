# Runtime Component Map

本文建立 Specification 文件到 Runtime 组件的映射关系。本文不定义实现代码，只说明各规格资产在 Runtime 架构中的位置和职责。

## Specification到Runtime组件映射

| Specification 文件 | Runtime 组件 | 映射说明 |
| --- | --- | --- |
| `workflows/pre_visit.yaml` | Workflow Engine | 定义诊前 Workflow 的输入、节点、输出、HITL 位置和安全约束，由 Workflow Engine 加载并实例化。 |
| `workflows/during_visit.yaml` | Workflow Engine | 定义诊中 Workflow 的执行结构，尤其是 RAG 节点、医嘱草稿节点和医生确认节点。 |
| `workflows/post_visit.yaml` | Workflow Engine | 定义诊后 Workflow 的任务生成、反馈跟踪、异常摘要、医生确认和 Memory 回流结构。 |
| `orchestration/Agent Orchestration Spec.md` | Orchestrator | 定义 Workflow 执行模型、节点执行规范、Context 传递、HITL 和失败处理。 |
| `tools/tool_contracts.yaml` | Tool Adapter Layer | 定义 9 个工具的输入、输出、权限、医生确认要求、审计要求和失败处理。 |
| `tools/Tool Contract Spec.md` | Tool Governance Layer | 解释工具使用边界，强调工具调用不构成医疗决定。 |
| `dify/tool_schemas.json` | Tool Schema Source | 作为工具清单和基础 schema 的来源，Runtime 不得擅自增删工具。 |
| `data/patient_wang_001.json` | Patient Data Store | 提供 Demo 患者档案、病史、用药、近期血压和上次就诊摘要。 |
| `data/patient_memory_wang_001.json` | Memory Store | 提供 Patient Memory 的基线结构和写回规则。 |
| `data/risk_profile_wang_001.json` | Risk Context Store | 提供风险画像上下文，仅用于医生关注优先级提示。 |
| `data/knowledge_hypertension_demo.md` | Knowledge Store | 提供 RAG Node 的 Demo 知识片段。 |
| `data/followup_tasks.jsonl` | Follow-up Task Store | 提供诊后任务的演示数据结构。 |
| `data/followup_events.jsonl` | Feedback Event Store | 提供诊后反馈事件和下一次诊前回流依据。 |

## Runtime组件职责

| Runtime 组件 | 主要输入 | 主要输出 | 职责 |
| --- | --- | --- | --- |
| Workflow Definition Loader | Workflow YAML | workflow_definition | 加载并校验 Workflow 名称、输入、节点、输出和 HITL 位置。 |
| Workflow Engine | workflow_definition、Patient Context | workflow_instance | 创建 Workflow 实例，推进节点，保存状态，处理失败。 |
| Orchestrator | workflow_instance、Node Context | node_execution_plan | 按 Orchestration 规则调度 Node Runtime。 |
| LLM Node Runtime | Context、节点 purpose | AI 草稿 | 生成摘要、提示、草稿、任务拆解和异常标记。 |
| RAG Node Runtime | query、Knowledge Store | 检索片段 | 检索医疗知识，并返回来源和要点。 |
| TOOL Node Runtime | tool_name、tool_input、Tool Contract | tool_result | 调用工具适配层，执行 schema、权限和审计检查。 |
| HUMAN Node Runtime | AI 输出、工具结果、RAG 来源 | 医生确认结果 | 暂停自动推进并接收医生的 approve、modify、reject。 |
| MEMORY Node Runtime | confirmed_content、doctor_confirmation_id | Memory 更新结果 | 读取或写入可信 Memory，写入前必须校验医生确认。 |
| Tool Adapter Layer | Tool Contract、工具输入 | 工具输出 | 按 `tool_contracts.yaml` 调用固定 9 个工具。 |
| Memory Layer | Memory Context、confirmed_content | updated_memory_context | 管理 Patient Memory 的读取与确认后写回。 |
| Audit Layer | Workflow、Node、Tool、AI、Human、Memory 事件 | audit_record | 记录执行链路，支持追溯和演示说明。 |
| Application Layer | Runtime 状态 | 医生可审核界面或演示输出 | 展示输入、AI 输出、医生确认、Memory 回流，不替代医生决策。 |

## 关键映射关系

### Workflow YAML到Workflow Engine

`pre_visit.yaml`、`during_visit.yaml`、`post_visit.yaml` 是 Workflow Engine 的配置源。

Workflow Engine 不直接写死医疗流程，而是读取 YAML 中的：

- `workflow_name`
- `business_goal`
- `input_data`
- `nodes`
- `output_data`
- `hitl_confirmation_points`
- `guardrails`

### Node Type到Node Runtime

| YAML node_type | Runtime |
| --- | --- |
| `LLM` | LLM Node Runtime |
| `RAG` | RAG Node Runtime |
| `TOOL` | TOOL Node Runtime |
| `HUMAN` | HUMAN Node Runtime |
| `MEMORY` | MEMORY Node Runtime |

### tool_contracts.yaml到Tool Adapter Layer

`tool_contracts.yaml` 是 Tool Adapter Layer 的执行边界。

Tool Adapter Layer 必须读取：

- tool_name
- input_schema
- output_schema
- permission
- human_confirmation_required
- audit_requirement
- failure_handling

### HUMAN Node到可信状态写入

HUMAN Node 是可信状态写入的前置组件。

只有当医生确认结果为：

- `approve`
- `modify`

后续 MEMORY Node 才能写入可信 Memory。若结果为 `reject`，Runtime 必须停止当前输出写回，并禁止进入下一医疗阶段。

## 不在本阶段实现的内容

- 不实现 Runtime 代码。
- 不创建 API。
- 不创建前端。
- 不连接真实 HIS、EMR、LIS、PACS。
- 不新增工具。
- 不改变医疗业务逻辑。
