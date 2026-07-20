<template>
  <details class="fold">
    <summary>
      <span class="caret">▶</span>
      追溯与状态 · Workflow State / 审计日志
      <span v-if="state" class="tag neutral mono" style="margin-left:6px">{{ state.workflow_id }}</span>
    </summary>
    <div class="fold-body" v-if="state">
      <dl class="kv" style="grid-template-columns: 130px 1fr; margin-bottom: 10px">
        <dt>Workflow</dt>
        <dd class="mono">{{ state.workflow_name }} · {{ state.workflow_status }}</dd>
        <dt>当前节点</dt>
        <dd class="mono">{{ state.current_node }}</dd>
        <dt>Runtime 模拟确认</dt>
        <dd>
          <span class="tag neutral">{{ state.doctor_confirmation?.human_decision || '—' }}</span>
          <span class="note-text" style="margin-left:6px">
            （Runtime 预跑用模拟决策；以医生在上方确认面板的提交为准）
          </span>
        </dd>
        <dt>节点执行顺序</dt>
        <dd class="mono" style="font-size:11.5px; word-break: break-all">{{ nodeOrder }}</dd>
      </dl>

      <div class="section-label">审计日志（Tool 调用 / Memory 读写 / 医生确认，{{ auditEntries.length }} 条）</div>
      <table class="data-table" v-if="auditEntries.length">
        <thead>
          <tr>
            <th>时间</th>
            <th>工具 / 事件</th>
            <th>Workflow 节点</th>
            <th>阶段</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(e, i) in auditEntries" :key="i">
            <td class="mono" style="white-space:nowrap">{{ (e.logged_at || '').slice(11, 19) || '—' }}</td>
            <td class="mono">{{ e.tool_name || e.event_type || '—' }}</td>
            <td class="mono">{{ e.workflow_node || '—' }}</td>
            <td class="mono">{{ e.workflow_stage || '—' }}</td>
          </tr>
        </tbody>
      </table>

      <div class="section-label">节点输出（原始 State 摘录）</div>
      <pre class="json-view">{{ nodeOutputsJson }}</pre>
    </div>
    <div v-else class="fold-body"><div class="loading-box">Workflow 尚未运行</div></div>
  </details>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  state: { type: Object, default: null },
  audit: { type: Object, default: null },
})

const nodeOrder = computed(() => Object.keys(props.state?.node_outputs || {}).join(' → '))
const auditEntries = computed(() => props.audit?.audit_log || props.state?.audit_log || [])
const nodeOutputsJson = computed(() => {
  const outputs = props.state?.node_outputs || {}
  // 只展示每个节点的 output 主体，控制长度
  const slim = {}
  for (const [node, record] of Object.entries(outputs)) {
    slim[node] = record?.output ?? record
  }
  const text = JSON.stringify(slim, null, 1)
  return text.length > 6000 ? text.slice(0, 6000) + '\n…（ truncated ）' : text
})
</script>
