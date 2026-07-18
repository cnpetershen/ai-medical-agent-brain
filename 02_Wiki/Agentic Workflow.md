# Agentic Workflow

## 定义

Agentic Workflow 是本项目中用于组织 [[医生AI Copilot]] 行为的流程化智能体工作方式。

它不是让 AI 完全自主地替代医生，而是用明确的 Workflow 将 Agent 能力限制在诊前、诊中、诊后的具体医疗任务中。

## 核心价值

- 把 AI 能力嵌入可控医疗流程，而不是开放式自由执行。
- 将诊前信息采集、诊中辅助决策和诊后医嘱执行拆成清晰的任务链。
- 让医疗 Copilot Agent 能根据场景调度不同 Workflow。
- 支撑医生审核、人工接管、过程追溯和风险控制。

## 为什么本项目需要

医疗场景要求可控、可追溯和医生主导。完全自主 Agent 容易超出边界，而单点 AI 工具又难以覆盖 [[连续照护闭环]]。

因此，本项目需要 Agentic Workflow 作为中间形态：既保留 Agent 的任务理解、上下文组织和工具调用能力，又通过 Workflow 明确任务范围、执行步骤和医生确认节点。

## 在医生AI Copilot中的作用

在 [[医生AI Copilot]] 中，Agentic Workflow 是连接智能调度中枢和具体医疗任务的执行载体。

它主要负责：

- 将医生需求映射到具体 Workflow。
- 约束每个 Workflow 的输入、处理步骤和输出结果。
- 在关键节点保留医生审核和确认。
- 让诊前、诊中、诊后任务能够连续衔接。
- 避免 Copilot 偏离“辅助医生完成连续照护”的项目目标。

## 与其他知识节点关系

- [[医生AI Copilot]]：Agentic Workflow 服务的产品形态。
- [[连续照护闭环]]：Agentic Workflow 要实现的业务目标。
- [[诊前信息采集 Workflow]]：Agentic Workflow 在诊前阶段的具体形态。
- [[诊中辅助决策 Workflow]]：Agentic Workflow 在诊中阶段的具体形态。
- [[诊后医嘱执行 Workflow]]：Agentic Workflow 在诊后阶段的具体形态。
- [[Agent]]：Agentic Workflow 中的智能能力来源。
- [[Tool Calling]]：Agentic Workflow 调用外部工具和数据能力的方式。
- [[Memory]]：Agentic Workflow 维持跨阶段上下文的重要能力。

## 使用场景

本项目中的 Agentic Workflow 主要用于把医疗任务组织成可执行、可检查、可交接的流程。

典型场景包括：

- 诊前根据患者输入自动整理就诊摘要，并交给医生查看。
- 诊中根据医生问题检索相关知识或整理检查结果，并由医生判断是否采纳。
- 诊后根据医嘱生成执行任务和随访提醒，并持续记录患者反馈。

## 备注

本节点只讨论本项目中的 Agentic Workflow，不展开通用智能体框架比较。后续技术节点如 [[Agent]]、[[RAG]]、[[Tool Calling]]、[[Memory]] 应服务于本项目的 Workflow 设计。
