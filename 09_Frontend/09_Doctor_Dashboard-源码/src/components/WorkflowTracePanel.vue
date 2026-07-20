<template>
  <section class="card trace-panel">
    <div class="card-head">
      <h2>Workflow Trace · Runtime 执行链路</h2>
      <span class="tag trace">来自 Audit API</span>
      <div class="spacer"></div>
      <span v-if="state" class="tag neutral mono">{{ state.workflow_id }}</span>
      <span v-if="state" class="tag" :class="state.workflow_status === 'completed' ? 'ok' : 'warn'">
        {{ state.workflow_status }}
      </span>
    </div>
    <div class="card-body" v-if="state">
      <div class="trace-meta">
        <div>
          <span class="note-text">Workflow</span>
          <b class="mono">{{ state.workflow_name }}</b>
        </div>
        <div>
          <span class="note-text">当前节点</span>
          <b class="mono">{{ state.current_node }}</b>
        </div>
        <div>
          <span class="note-text">审计事件</span>
          <b>{{ auditEntries.length }} 条</b>
        </div>
      </div>

      <div class="trace-flow" aria-label="Workflow node execution order">
        <template v-for="(node, index) in nodes" :key="node.name">
          <div class="trace-node-card">
            <div class="trace-node-head">
              <span class="node-type" :class="typeClass(node.type)">{{ node.type }}</span>
              <b class="mono">{{ node.name }}</b>
              <span class="tag ok">{{ node.status }}</span>
            </div>
            <dl class="trace-node-detail">
              <dt>输入摘要</dt>
              <dd>{{ node.inputSummary }}</dd>
              <dt>输出摘要</dt>
              <dd>{{ node.outputSummary }}</dd>
            </dl>
          </div>
          <span v-if="index < nodes.length - 1" class="trace-down">↓</span>
        </template>
      </div>
    </div>
    <div v-else class="card-body">
      <div class="loading-box">Workflow 尚未运行</div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  state: { type: Object, default: null },
  audit: { type: Object, default: null },
})

const NODE_TYPES = {
  pre_visit: {
    load_pre_visit_context: 'TOOL',
    load_continuity_memory: 'MEMORY',
    identify_key_and_missing_information: 'LLM',
    generate_structured_pre_visit_summary: 'LLM',
    doctor_review_pre_visit_summary: 'HUMAN',
    write_confirmed_pre_visit_context: 'MEMORY',
  },
  during_visit: {
    load_during_visit_context: 'TOOL',
    load_confirmed_patient_memory: 'MEMORY',
    determine_information_need: 'LLM',
    retrieve_medical_knowledge: 'RAG',
    organize_clinical_context: 'LLM',
    generate_order_draft: 'LLM',
    doctor_review_during_visit_output: 'HUMAN',
    write_confirmed_during_visit_decisions: 'MEMORY',
  },
  post_visit: {
    load_post_visit_inputs: 'TOOL',
    load_confirmed_post_visit_memory: 'MEMORY',
    decompose_orders_into_tasks: 'LLM',
    create_and_track_followup_tasks: 'TOOL',
    summarize_execution_and_flag_risks: 'LLM',
    doctor_review_post_visit_status: 'HUMAN',
    write_confirmed_post_visit_feedback: 'MEMORY',
  },
}

const auditEntries = computed(() => props.audit?.audit_log || props.state?.audit_log || [])

const nodes = computed(() => {
  const outputs = props.state?.node_outputs || {}
  const typeMap = NODE_TYPES[props.state?.workflow_name] || {}
  return Object.entries(outputs).map(([name, record]) => ({
    name,
    type: typeMap[name] || inferType(name),
    status: record?.status || 'unknown',
    inputSummary: summarizeInput(name),
    outputSummary: summarizeOutput(record?.output),
  }))
})

function summarizeInput(nodeName) {
  const matched = auditEntries.value.filter((entry) => entry.workflow_node === nodeName)
  if (!matched.length) {
    if (nodeName.includes('doctor_review')) return '接收上一节点 AI 辅助草稿，等待医生 approve / modify / reject。'
    if (nodeName.startsWith('write_confirmed')) return '接收医生确认 ID 与确认后的内容，准备可信 Memory 写回。'
    return '读取 Workflow Context 中已有节点输出。'
  }
  const tools = matched.map((entry) => entry.tool_name || entry.memory_operation).filter(Boolean)
  const firstInput = matched.find((entry) => entry.input)?.input
  if (firstInput?.patient_id) return `patient_id=${firstInput.patient_id}；调用 ${tools.join('、')}`
  return `审计事件：${tools.join('、')}`
}

function summarizeOutput(output) {
  if (!output) return '无输出'
  if (output.human_decision) return `医生确认：${output.human_decision}；确认ID：${output.doctor_confirmation_id || '—'}`
  if (output.before && output.after) return 'Memory before / after 已记录，可信写回完成。'
  if (Array.isArray(output)) return `返回 ${output.length} 条记录。`
  const keys = Object.keys(output)
  if (keys.includes('retrieval_status')) return `RAG ${output.retrieval_status}；返回 ${(output.sections || []).length} 个知识片段。`
  if (keys.includes('mock')) return `AI 辅助草稿：${keys.filter((k) => k !== 'mock').slice(0, 4).join('、')}`
  return `输出字段：${keys.slice(0, 5).join('、')}`
}

function inferType(name) {
  if (name.includes('rag') || name.includes('knowledge')) return 'RAG'
  if (name.includes('doctor_review')) return 'HUMAN'
  if (name.includes('memory') || name.startsWith('write_confirmed')) return 'MEMORY'
  if (name.startsWith('load') || name.includes('task')) return 'TOOL'
  return 'LLM'
}

function typeClass(type) {
  return `type-${String(type).toLowerCase()}`
}
</script>
