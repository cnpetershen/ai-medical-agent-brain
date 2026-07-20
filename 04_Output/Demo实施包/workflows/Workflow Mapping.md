# Workflow Mapping

本文说明 `02_Wiki` 中的三个 Markdown Workflow 如何映射为 `04_Output/Demo实施包/workflows/` 下的 YAML 机器可读定义。

## 映射原则

- 保持原有医疗业务逻辑，不新增新的诊疗动作。
- 保持医生主导，所有关键医疗输出都必须经过 HUMAN 节点确认。
- YAML 只表达流程结构，不表达自动诊断、自动处方或自动改药能力。
- 节点类型严格限定为：`LLM`、`RAG`、`TOOL`、`HUMAN`、`MEMORY`。

## 字段映射规则

Markdown 章节与 YAML 字段的对应关系如下：

| Markdown 章节 | YAML 字段 | 映射说明 |
| --- | --- | --- |
| 定义 | `workflow_name`、`business_goal` | 将 Workflow 名称和核心目标压缩为机器可读顶层定义。 |
| 输入数据 | `input_data` | 原文列出的输入项直接转为结构化输入列表。 |
| 工作流程 | `nodes` | 按步骤拆解为节点列表，每一步映射为一个或多个节点。 |
| Agent作用 | `nodes` 中的 `LLM` / `RAG` / `TOOL` / `MEMORY` | 按 Agent 实际承担的能力分配节点类型。 |
| 医生角色 | `HUMAN` 节点、`hitl_confirmation_points` | 医生审核、确认、修改、拒绝的位置显式标注。 |
| 输出结果 | `output_data` | 原文输出项转为结构化输出列表。 |
| 备注 / 边界 | `guardrails` | 将医生主导和安全边界写成约束。 |

## 节点类型解释

- `TOOL`：读取或写入外部结构化数据、任务状态、检查结果或业务对象。
- `MEMORY`：读取或写入经过医生确认的连续照护上下文。
- `LLM`：执行信息识别、结构化整理、摘要生成、任务拆解和风险标记等语言理解工作。
- `RAG`：检索医疗知识片段，为医生提供可追溯参考依据。
- `HUMAN`：医生审核、确认、修改、拒绝或决定是否进入下一阶段。

## Pre-visit 映射

来源：[诊前信息采集 Workflow.md](/D:/计算机运行笔记/AI-Medical-Agent-Brain/02_Wiki/诊前信息采集 Workflow.md)

Markdown 工作流程：

1. 接收患者基础信息、主诉、症状描述和历史资料。
2. 识别本次就诊相关的关键信息和缺失信息。
3. 将患者自由描述整理为结构化诊前摘要。
4. 关联既往病史、近期用药、检查记录和随访反馈。
5. 生成医生接诊前可查看的就诊准备材料。
6. 对需要医生关注或患者补充的信息进行标记。

YAML 节点映射：

- `load_pre_visit_context`：对应第 1 步和第 4 步的数据读取。
- `load_continuity_memory`：补足“连续照护上下文”的机器可读入口。
- `identify_key_and_missing_information`：对应第 2 步。
- `generate_structured_pre_visit_summary`：对应第 3、5、6 步。
- `doctor_review_pre_visit_summary`：对应“医生角色”中的确认职责。
- `write_confirmed_pre_visit_context`：将确认结果传递给诊中 Workflow。

## During-visit 映射

来源：[诊中辅助决策 Workflow.md](/D:/计算机运行笔记/AI-Medical-Agent-Brain/02_Wiki/诊中辅助决策 Workflow.md)

Markdown 工作流程：

1. 接收诊前信息采集 Workflow 生成的患者上下文。
2. 根据医生当前问题或诊疗阶段识别所需信息。
3. 整理历史病历、检查结果和患者近期状态。
4. 在需要时提供相关知识、指南或资料辅助。
5. 生成辅助性摘要、问题提示或医嘱草稿。
6. 将结果提交医生审核，由医生决定是否采纳。
7. 将医生确认后的医嘱或管理任务传递给诊后医嘱执行 Workflow。

YAML 节点映射：

- `load_during_visit_context`：对应第 1 步和第 3 步中的数据载入。
- `load_confirmed_patient_memory`：读取已确认的跨阶段上下文。
- `determine_information_need`：对应第 2 步。
- `retrieve_medical_knowledge`：对应第 4 步。
- `organize_clinical_context`：对应第 3 步和第 5 步中的摘要整理。
- `generate_order_draft`：对应第 5 步中的医嘱草稿生成。
- `doctor_review_during_visit_output`：对应第 6 步。
- `write_confirmed_during_visit_decisions`：对应第 7 步。

## Post-visit 映射

来源：[诊后医嘱执行 Workflow.md](/D:/计算机运行笔记/AI-Medical-Agent-Brain/02_Wiki/诊后医嘱执行 Workflow.md)

Markdown 工作流程：

1. 接收诊中辅助决策 Workflow 中由医生确认的医嘱和管理事项。
2. 将医嘱拆解为用药、康复、复查、复诊、随访等任务。
3. 为患者生成可理解的执行提醒和任务计划。
4. 持续记录患者执行状态和健康反馈。
5. 对未完成、异常或风险信号进行标记。
6. 必要时生成医生查看提醒或随访任务。
7. 将诊后反馈沉淀为下一次诊前信息采集的输入。

YAML 节点映射：

- `load_post_visit_inputs`：对应第 1 步。
- `load_confirmed_post_visit_memory`：读取诊后执行所需连续上下文。
- `decompose_orders_into_tasks`：对应第 2 步。
- `create_and_track_followup_tasks`：对应第 3 步和第 4 步。
- `summarize_execution_and_flag_risks`：对应第 5 步和第 6 步中的异常与风险整理。
- `doctor_review_post_visit_status`：对应“医生角色”中的风险确认和后续决策。
- `write_confirmed_post_visit_feedback`：对应第 7 步。

## HITL 位置说明

三个 Workflow 的 HITL 确认位置都放在关键医疗输出之后、Memory 写回之前：

- `pre_visit.yaml`：医生确认诊前摘要后，才允许写入可信 Memory。
- `during_visit.yaml`：医生确认诊中辅助结果和医嘱草稿后，才允许进入诊后。
- `post_visit.yaml`：医生确认异常摘要和回流内容后，才允许写入可信 Memory 并作为下次诊前输入。

## 结果文件

- [pre_visit.yaml](/D:/计算机运行笔记/AI-Medical-Agent-Brain/04_Output/Demo实施包/workflows/pre_visit.yaml)
- [during_visit.yaml](/D:/计算机运行笔记/AI-Medical-Agent-Brain/04_Output/Demo实施包/workflows/during_visit.yaml)
- [post_visit.yaml](/D:/计算机运行笔记/AI-Medical-Agent-Brain/04_Output/Demo实施包/workflows/post_visit.yaml)
