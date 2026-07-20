<template>
  <section class="card">
    <div class="card-head">
      <h2>患者摘要</h2>
      <div class="spacer"></div>
      <span class="tag neutral">模拟数据</span>
    </div>
    <div class="card-body" v-if="profile">
      <dl class="kv">
        <dt>患者别名</dt>
        <dd>{{ p.name_alias }}（{{ p.sex }} · {{ p.age }} 岁）</dd>
        <dt>就诊类型</dt>
        <dd>{{ p.visit_type }}</dd>
        <dt>本次主诉</dt>
        <dd>{{ p.chief_complaint }}</dd>
        <dt>高血压病史</dt>
        <dd>{{ history.hypertension_history }}</dd>
        <dt>当前用药</dt>
        <dd>
          <div v-for="m in medications" :key="m.name">
            {{ m.name }} {{ m.dose }} {{ m.frequency }}
            <span class="note-text">（{{ m.adherence }}；{{ m.note }}）</span>
          </div>
        </dd>
        <dt>上次就诊</dt>
        <dd v-if="previous.date">
          {{ previous.date }}：{{ previous.summary }}
          <span v-if="previous.confirmed_by_doctor" class="tag ok" style="margin-left:4px">医生已确认</span>
        </dd>
      </dl>

      <!-- 连续照护回流线索：上一次诊后 -> 本次诊前 -->
      <template v-if="backflowSummary">
        <div class="section-label">上一次诊后回流线索</div>
        <div class="ai-draft" style="border-color:#ddd6fe;background:linear-gradient(180deg,#fbf8ff,#f6f1ff)">
          <span class="draft-mark" style="background:#7c3aed">连续照护回流</span>
          <p class="draft-text">{{ backflowSummary }}</p>
        </div>
      </template>

      <p class="note-text" style="margin:10px 0 0">{{ profile.privacy_note }}</p>
    </div>
    <div v-else class="loading-box"><span class="spinner"></span>加载患者档案…</div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  profile: { type: Object, default: null }, // GET /patient/{id}/profile 响应
  memory: { type: Object, default: null }, // GET /patient/{id}/memory 响应
})

const p = computed(() => props.profile?.profile || {})
const history = computed(() => props.profile?.history || {})
const medications = computed(() => props.profile?.current_medications || [])
const previous = computed(() => props.profile?.previous_visit_summary || {})
// 闭环：上一次诊后写回的 next_previsit_summary 作为本次诊前上下文
const backflowSummary = computed(
  () => props.memory?.post_visit_memory?.next_previsit_summary || '',
)
</script>
