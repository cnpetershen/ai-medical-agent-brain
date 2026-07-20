<template>
  <section class="card rag-evidence-card">
    <div class="card-head">
      <h2>RAG Evidence Card · 知识依据</h2>
      <span class="tag trace">AI 输出来自检索，不是自由生成</span>
      <div class="spacer"></div>
      <span class="tag" :class="retrievalStatus === 'succeeded' ? 'ok' : 'danger'">
        {{ retrievalStatus === 'succeeded' ? '检索成功' : '未检索到充分来源' }}
      </span>
    </div>
    <div class="card-body" v-if="sections.length">
      <dl class="kv" style="grid-template-columns: 90px 1fr; margin-bottom:12px">
        <dt>知识来源</dt>
        <dd>《中国高血压防治指南（2024修订版）》</dd>
        <dt>检索结果</dt>
        <dd>{{ sections.length }} 个相关片段，已关联诊中辅助建议。</dd>
      </dl>

      <div class="evidence-list">
        <div v-for="(sec, i) in sections" :key="i" class="evidence-item">
          <div class="tl-head">
            <b>{{ sec.title }}</b>
            <span class="tag neutral">引用片段 {{ i + 1 }}</span>
          </div>
          <div class="evidence-source">{{ sec.source || '来源：中国高血压防治指南（2024修订版）' }}</div>
          <p>{{ sec.points }}</p>
        </div>
      </div>

      <div class="section-label">辅助建议关联关系</div>
      <ul class="clean-list">
        <li v-for="(item, i) in assistanceItems" :key="i">
          {{ item }}
          <div class="note-text">关联依据：{{ referenceText }}</div>
        </li>
      </ul>
      <div class="safety-note">
        RAG 证据只为医生提供可追溯依据；AI 不自动诊断、不自动处方、不自动改药，医生确认前不进入可信 Memory。
      </div>
    </div>
    <div v-else class="card-body">
      <div class="loading-box"><span class="spinner"></span>等待 RAG 检索结果…</div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  rag: { type: Object, default: null },
  assistance: { type: Object, default: null },
})

const retrievalStatus = computed(() => props.rag?.retrieval_status || '')
const sections = computed(() =>
  (props.rag?.sections || []).map((sec) => {
    const parts = String(sec.content || '').split(/\n\n+/)
    const sourceRaw = parts.find((p) => p.startsWith('来源：')) || ''
    const pointsRaw = parts.find((p) => p.startsWith('要点：')) || parts[parts.length - 1] || ''
    return {
      title: sec.title,
      source: sourceRaw.replace(/^来源：/, '来源：'),
      points: pointsRaw.replace(/^要点：/, ''),
    }
  }),
)
const assistanceItems = computed(() => props.assistance?.clinical_assistance || [])
const referenceText = computed(() =>
  (props.assistance?.knowledge_references || []).join('、') || 'RAG 检索片段',
)
</script>
