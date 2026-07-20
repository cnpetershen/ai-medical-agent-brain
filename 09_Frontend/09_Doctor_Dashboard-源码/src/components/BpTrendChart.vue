<template>
  <section class="card">
    <div class="card-head">
      <h2>近期家庭血压趋势</h2>
      <div class="spacer"></div>
      <span class="tag neutral">{{ vitals.length }} 次记录</span>
    </div>
    <div class="card-body">
      <svg v-if="vitals.length" :viewBox="`0 0 ${W} ${H}`" width="100%" role="img" aria-label="血压趋势图">
        <!-- 参考阈值带：家庭血压 135/85 -->
        <line :x1="padL" :y1="y(135)" :x2="W - padR" :y2="y(135)" stroke="#fca5a5" stroke-dasharray="5 4" stroke-width="1" />
        <line :x1="padL" :y1="y(85)" :x2="W - padR" :y2="y(85)" stroke="#fcd34d" stroke-dasharray="5 4" stroke-width="1" />
        <text :x="W - padR" :y="y(135) - 4" text-anchor="end" font-size="9" fill="#b91c1c">收缩压参考 135</text>
        <text :x="W - padR" :y="y(85) + 11" text-anchor="end" font-size="9" fill="#b45309">舒张压参考 85</text>

        <!-- 网格与刻度 -->
        <g v-for="t in yTicks" :key="t">
          <line :x1="padL" :y1="y(t)" :x2="W - padR" :y2="y(t)" stroke="#e8eef4" stroke-width="1" />
          <text :x="padL - 6" :y="y(t) + 3" text-anchor="end" font-size="9" fill="#7a8fa3">{{ t }}</text>
        </g>

        <!-- 收缩压 / 舒张压折线 -->
        <polyline :points="linePoints('sbp')" fill="none" stroke="#b91c1c" stroke-width="2" stroke-linejoin="round" />
        <polyline :points="linePoints('dbp')" fill="none" stroke="#0e7490" stroke-width="2" stroke-linejoin="round" />
        <g v-for="(v, i) in vitals" :key="v.date">
          <circle :cx="x(i)" :cy="y(v.sbp)" r="3" fill="#b91c1c" />
          <circle :cx="x(i)" :cy="y(v.dbp)" r="3" fill="#0e7490" />
          <text :x="x(i)" :y="y(v.sbp) - 7" text-anchor="middle" font-size="8.5" fill="#b91c1c">{{ v.sbp }}</text>
          <text :x="x(i)" :y="y(v.dbp) + 13" text-anchor="middle" font-size="8.5" fill="#0e7490">{{ v.dbp }}</text>
          <text :x="x(i)" :y="H - 6" text-anchor="middle" font-size="8.5" fill="#7a8fa3">{{ v.date.slice(5) }}</text>
        </g>
      </svg>
      <div class="tag-row" style="margin-top:6px">
        <span class="tag" style="background:#fee2e2;color:#b91c1c;border:1px solid #fca5a5">● 收缩压 mmHg</span>
        <span class="tag" style="background:#ecfeff;color:#0e7490;border:1px solid #a5f3fc">● 舒张压 mmHg</span>
        <span class="note-text" style="align-self:center">数据来源：家庭自测（home_bp），仅供医生参考趋势</span>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  vitals: { type: Array, default: () => [] }, // recent_vitals
})

const W = 560
const H = 190
const padL = 34
const padR = 10
const padT = 16
const padB = 22

const allValues = computed(() => props.vitals.flatMap((v) => [v.sbp, v.dbp]))
const minV = computed(() => Math.min(...allValues.value, 80) - 5)
const maxV = computed(() => Math.max(...allValues.value, 140) + 8)

const yTicks = computed(() => {
  const ticks = []
  const step = 20
  for (let t = Math.ceil(minV.value / step) * step; t <= maxV.value; t += step) ticks.push(t)
  return ticks
})

const x = (i) => padL + (i * (W - padL - padR)) / Math.max(props.vitals.length - 1, 1)
const y = (v) => padT + ((maxV.value - v) * (H - padT - padB)) / (maxV.value - minV.value)

const linePoints = (key) =>
  props.vitals.map((v, i) => `${x(i)},${y(v[key])}`).join(' ')
</script>
