<template>
  <section class="card">
    <div class="card-head">
      <h2>Memory 变化对照</h2>
      <div class="spacer"></div>
      <span class="tag neutral">仅高亮变化字段</span>
    </div>
    <div class="card-body">
      <div v-if="diffEntries.length === 0" class="note-text">before / after 无差异或数据缺失。</div>
      <div v-else style="display:flex; flex-direction:column; gap:12px">
        <div v-for="entry in diffEntries" :key="entry.key">
          <div class="section-label" style="margin:0 0 6px">
            {{ entry.label }}
            <span v-if="entry.added" class="diff-add">＋ 新增</span>
            <span v-else-if="entry.changed" class="tag warn">有变化</span>
            <span v-else class="tag neutral">无变化</span>
          </div>
          <div class="diff-row">
            <div class="diff-cell" :class="{ 'changed-before': entry.changed }">
              <div class="diff-key">写回前</div>
              <div>{{ entry.beforeText }}</div>
            </div>
            <div class="diff-cell" :class="{ 'changed-after': entry.changed || entry.added }">
              <div class="diff-key">写回后（医生确认 {{ confirmationId }}）</div>
              <div>{{ entry.afterText }}</div>
            </div>
          </div>
        </div>
      </div>
      <p class="note-text" style="margin:12px 0 0">
        Memory 写回必须经医生确认（doctor_confirmation_id）后执行；AI 草稿不得直接写入可信 Memory。
      </p>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  before: { type: Object, default: null }, // write_confirmed_* 节点 output.before
  after: { type: Object, default: null }, // write_confirmed_* 节点 output.after
  section: { type: String, default: 'post_visit_memory' }, // 对照的 memory 区
  confirmationId: { type: String, default: '' },
})

const LABELS = {
  task_adherence_summary: '诊后依从性摘要',
  abnormal_events: '异常事件（需医生复核）',
  next_previsit_summary: '下一次诊前回流摘要',
  doctor_confirmed: '医生确认标记',
  confirmed_at: '确认时间',
}

const diffEntries = computed(() => {
  const b = props.before?.[props.section] || {}
  const a = props.after?.[props.section] || {}
  const keys = Object.keys({ ...b, ...a })
  return keys.map((key) => {
    const bv = b[key]
    const av = a[key]
    const added = bv === undefined && av !== undefined
    const changed = !added && JSON.stringify(bv) !== JSON.stringify(av)
    return {
      key,
      label: LABELS[key] || key,
      added,
      changed,
      beforeText: fmt(bv),
      afterText: fmt(av),
    }
  })
})

function fmt(v) {
  if (v === undefined || v === null) return '—（无）'
  if (typeof v === 'string') return v
  if (typeof v === 'boolean') return v ? '已确认' : '未确认'
  if (Array.isArray(v)) return `${v.length} 条记录（详见反馈事件时间线）`
  if (typeof v === 'object') {
    if ('event_count' in v) {
      return `反馈事件 ${v.event_count} 条 · 异常 ${v.abnormal_event_count} 条`
    }
    return JSON.stringify(v, null, 1)
  }
  return String(v)
}
</script>
