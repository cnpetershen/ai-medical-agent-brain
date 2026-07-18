# Agent架构设计

## 定义

Agent架构设计是指本项目中 [[医疗AI Agent]] 内部模块如何组织，以支撑 [[医生AI Copilot]] 调度三大 Workflow。

该架构服务于医生工作流程，不用于构建完全自主的医疗 AI 系统。

## 在本项目中的作用

- 将医生需求转化为可执行的 Workflow 任务。
- 组织患者上下文、医疗知识、系统数据和任务状态。
- 协调 [[RAG]]、[[Memory]]、[[Tool Calling]] 和 [[Human-in-the-loop]]。
- 保证 AI 输出始终服务医生审核和临床工作流。

## 解决的问题

- 单一大模型对话无法稳定支撑诊前、诊中、诊后连续流程。
- 医疗任务需要上下文、工具、知识和医生审核协同。
- Agent 需要明确边界，不能自动诊断或替代医生。
- 不同 Workflow 需要统一的智能调度中枢。

## 设计思路

建议内部模块：

- 意图理解模块：识别医生需求、患者事件和当前任务目标。
- 上下文管理模块：读取和更新 [[Memory]] 中的患者、医生和 Workflow 状态。
- Workflow 调度模块：选择 [[诊前信息采集 Workflow]]、[[诊中辅助决策 Workflow]] 或 [[诊后医嘱执行 Workflow]]。
- 知识增强模块：通过 [[RAG]] 连接 [[医疗知识库]]。
- 工具调用模块：通过 [[Tool Calling]] 连接 [[HIS]]、[[EMR]]、[[LIS]]、[[PACS]] 或模拟接口。
- 安全审核模块：在关键节点触发 [[Human-in-the-loop]]。
- 输出组织模块：生成医生可审核的摘要、提示、任务草稿或状态更新。

## 与现有知识节点关系

- [[医疗AI Agent]]：本节点描述其内部模块。
- [[医生AI Copilot]]：Agent 架构支撑 Copilot 产品形态。
- [[Agentic Workflow]]：Agent 通过 Workflow 约束行为。
- [[Workflow Orchestration]]：Agent 架构中的调度能力。
- [[RAG]]：知识增强模块。
- [[Memory]]：上下文管理模块。
- [[Tool Calling]]：工具调用模块。
- [[Human-in-the-loop]]：安全审核模块。

## 备注

Agent 架构设计必须围绕“医生 AI Copilot + 多 Workflow + 连续照护闭环”，不扩展为泛医疗智能体平台。
