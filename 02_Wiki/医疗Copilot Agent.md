# 医疗Copilot Agent

## 定义

医疗Copilot Agent 是 [[医生AI Copilot]] 内部的智能调度中枢。

它负责根据医生工作场景、患者上下文和任务状态，调度 [[诊前信息采集 Workflow]]、[[诊中辅助决策 Workflow]] 和 [[诊后医嘱执行 Workflow]]，服务于 [[连续照护闭环]]。

## 在医疗Copilot中的作用

- 识别当前任务属于诊前、诊中还是诊后。
- 将医生指令路由到对应 [[Agentic Workflow]]。
- 协调 [[RAG]]、[[Memory]]、[[Tool Calling]] 和 [[Human-in-the-loop]]。
- 将外部医疗数据、知识库和患者反馈组织成医生可审核的输出。
- 保持医生作为最终决策者，不替代医生诊断。

## 为什么项目需要

本项目不是单点 AI 问答工具，而是围绕医生流程的连续照护系统。医疗Copilot Agent 用来统一调度三大 Workflow，避免诊前、诊中、诊后各自孤立。

## 支撑哪个Workflow

- [[诊前信息采集 Workflow]]：整理患者信息和就诊前上下文。
- [[诊中辅助决策 Workflow]]：组织知识检索、病历摘要和检查结果整理。
- [[诊后医嘱执行 Workflow]]：跟踪医嘱任务、随访反馈和复诊准备。

## 输入输出

输入：

- 医生任务指令。
- 患者基础信息和健康反馈。
- [[HIS]]、[[EMR]]、[[LIS]]、[[PACS]] 等接口数据。
- [[医疗知识库]] 检索结果。
- Workflow 状态和历史上下文。

输出：

- 被调度的 Workflow。
- 医生可审核的摘要、提示或任务草稿。
- 工具调用结果。
- 需要医生确认的关键节点。
- 写入 [[Memory]] 的流程状态和确认结果。

## 与其他知识节点关系

- [[医疗AI Agent]]：本节点是其项目命名版，二者指向同一智能调度中枢。
- [[医生AI Copilot]]：医疗Copilot Agent 是其内部核心。
- [[Agentic Workflow]]：医疗Copilot Agent 通过 Workflow 约束执行。
- [[Workflow Orchestration]]：描述其调度三大 Workflow 的工程方式。
- [[医疗隐私与最小必要原则]]：约束其使用患者数据的边界。

## 备注

后续项目叙述中优先使用“医疗Copilot Agent”作为产品化表达；已有 [[医疗AI Agent]] 节点保留为技术层表达。
