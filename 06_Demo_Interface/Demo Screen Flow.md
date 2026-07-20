# Demo Screen Flow

本文定义 Demo Presentation Layer 的屏幕流转顺序，用于比赛演示或原型讲解。本文不描述前端实现，只定义演示页面和切换逻辑。

## 总体原则

演示应按“王某的一次完整医疗旅程”展开，而不是按功能模块列表展开。

屏幕流转顺序固定为：

1. 诊前
2. 诊中
3. 诊后
4. 下一次诊前回流

贯穿主线：

- AI 辅助
- 医生确认
- 连续照护闭环

## Screen 1：诊前总览

### 目标

让观众快速理解患者背景和本次复诊上下文。

### 屏幕内容

- 患者卡片
- 既往病史与当前用药
- 近期家庭血压趋势
- 上一次回流摘要
- 风险画像概览

### Runtime 对应来源

- `patient_wang_001.json`
- `pre_visit` Runtime State
- `patient_memory_wang_001.json`
- `risk_profile_wang_001.json`

### 演示说明

- 开场先显示患者是谁
- 再显示系统已掌握的连续上下文
- 强调医生不是从零开始接诊

## Screen 2：诊前 AI 整理与待确认信息

### 目标

展示 AI 已完成的信息整理，以及仍需要医生核对的问题。

### 屏幕内容

- AI 诊前摘要草稿
- 关键事实
- 风险线索
- 待确认问题
- 医生确认状态

### Runtime 对应来源

- `identify_key_and_missing_information`
- `generate_structured_pre_visit_summary`
- `doctor_review_pre_visit_summary`

### 演示说明

- 明确显示“AI整理结果”
- 明确显示“待医生确认”
- 不展示任何最终诊断用语

## Screen 3：诊中知识依据

### 目标

展示诊中 RAG 的作用，即给医生提供可追溯的参考依据。

### 屏幕内容

- 知识片段标题
- 来源
- 要点摘要
- 当前医生问题

### Runtime 对应来源

- `retrieve_medical_knowledge`
- `knowledge_hypertension_demo.md`

### 演示说明

- 强调这是“参考依据”
- 强调有来源，不是 AI 凭空生成

## Screen 4：诊中辅助建议与医嘱草稿

### 目标

展示 AI 如何把诊前上下文和知识依据组织成医生可审核的辅助结果。

### 屏幕内容

- 辅助建议
- 管理方向草稿
- 医嘱草稿
- 医生确认状态

### Runtime 对应来源

- `organize_clinical_context`
- `generate_order_draft`
- `doctor_review_during_visit_output`

### 演示说明

- 显示“供医生确认”
- 显示医生确认后才可进入诊后

## Screen 5：诊后任务与事件

### 目标

展示医生确认后的管理计划如何转化为可跟踪的诊后任务与反馈事件。

### 屏幕内容

- 随访任务列表
- 7 天反馈事件时间线
- 需要医生复核的异常事件

### Runtime 对应来源

- `create_followup_tasks`
- `record_patient_feedback`
- `get_followup_status`
- `followup_tasks.jsonl`
- `followup_events.jsonl`

### 演示说明

- 明确显示这是任务管理与反馈跟踪
- 不显示“系统已自动改药”之类表达

## Screen 6：诊后 AI 摘要与医生确认

### 目标

展示诊后反馈如何被 AI 汇总，并再次经过医生确认。

### 屏幕内容

- 执行摘要
- 异常标记
- 风险更新草稿
- 医生确认状态

### Runtime 对应来源

- `summarize_execution_and_flag_risks`
- `doctor_review_post_visit_status`

### 演示说明

- 突出第 3 天头晕较前明显
- 突出第 4 天漏服
- 强调“异常摘要需医生确认后才能写回 Memory”

## Screen 7：Memory变化

### 目标

展示可信上下文是如何在医生确认后被更新的。

### 屏幕内容

- 写回前 Memory
- 写回后 Memory
- 新增字段高亮
- 确认 ID

### Runtime 对应来源

- `write_confirmed_post_visit_feedback`
- `patient_memory_wang_001.json`

### 演示说明

- 这里是“可信状态写入”的证据页
- 应明确 AI 草稿和医生确认后内容的区别

## Screen 8：下一次诊前回流

### 目标

展示连续照护闭环的最终价值。

### 屏幕内容

- 下一次诊前摘要顶部内容
- 回流后的重点关注事项
- 连续照护闭环标记

### Runtime 对应来源

- `post_visit_memory.next_previsit_summary`

### 演示说明

- 这是整场 Demo 的高潮页
- 要强调“诊后反馈改变下一次诊前”

## 屏幕切换逻辑

```text
诊前总览
-> 诊前AI整理与待确认信息
-> 诊中知识依据
-> 诊中辅助建议与医嘱草稿
-> 诊后任务与事件
-> 诊后AI摘要与医生确认
-> Memory变化
-> 下一次诊前回流
```

## 演示节奏建议

- Screen 1-2：建立患者上下文与医生确认机制
- Screen 3-4：建立诊中知识依据与辅助建议
- Screen 5-7：建立诊后执行、异常反馈与可信写回
- Screen 8：收束为连续照护闭环

## 设计边界

- 不以聊天机器人式交互串联屏幕
- 不展示“AI 自动决策”
- 不展示自动医疗执行动作
- 不新增未在 Runtime 中产生的数据
