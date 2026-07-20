<template>
  <!-- 连续照护闭环链路：诊前 → 诊中 → 诊后 → 回流下一次诊前 -->
  <div class="loop-bar">
    <span class="loop-node" :class="{ on: current === 'pre_visit' }">诊前 · 信息采集</span>
    <span class="loop-arrow">→</span>
    <span class="loop-node" :class="{ on: current === 'during_visit' }">诊中 · 辅助决策</span>
    <span class="loop-arrow">→</span>
    <span class="loop-node" :class="{ on: current === 'post_visit' }">诊后 · 医嘱执行</span>
    <span class="loop-arrow back">↩</span>
    <span class="loop-node backflow" :class="{ on: highlightBackflow }">回流 · 下一次诊前上下文</span>
  </div>
</template>

<script setup>
defineProps({
  current: { type: String, required: true }, // pre_visit | during_visit | post_visit
  highlightBackflow: { type: Boolean, default: false },
})
</script>
