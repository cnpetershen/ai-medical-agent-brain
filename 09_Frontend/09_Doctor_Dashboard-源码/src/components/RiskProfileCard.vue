<template>
  <section class="card">
    <div class="card-head">
      <h2>风险画像</h2>
      <div class="spacer"></div>
      <span class="tag warn">{{ riskProfile?.overall_demo_risk_level || '—' }}</span>
    </div>
    <div class="card-body" v-if="dimensions.length">
      <div class="clean-list">
        <div
          v-for="d in dimensions"
          :key="d.dimension"
          class="risk-item"
          :class="levelClass(d.level)"
        >
          <div class="risk-head">
            {{ d.dimension }}
            <span class="tag" :class="levelTagClass(d.level)">{{ d.level }}</span>
          </div>
          <div class="risk-evidence">依据：{{ d.evidence }}</div>
          <div class="risk-action">
            <span aria-hidden="true">→</span>
            <span><b>医生关注动作：</b>{{ d.doctor_action }}</span>
          </div>
        </div>
      </div>
      <div class="safety-note">{{ riskProfile.guardrail }}</div>
    </div>
    <div v-else class="loading-box"><span class="spinner"></span>加载风险画像…</div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  riskProfile: { type: Object, default: null },
})

const dimensions = computed(() => props.riskProfile?.risk_dimensions || [])

const levelClass = (lv) =>
  lv === '高' ? 'lv-high' : lv.includes('高') ? 'lv-midhigh' : 'lv-mid'
const levelTagClass = (lv) =>
  lv === '高' ? 'danger' : lv.includes('高') ? 'warn' : 'neutral'
</script>
