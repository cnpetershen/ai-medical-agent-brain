<template>
  <header class="topbar">
    <div class="brand">
      医生AI Copilot 工作台
      <span class="sub">Doctor Dashboard · Agentic Workflow Demo</span>
    </div>
    <div class="spacer"></div>
    <div v-if="session.profile" class="patient-chip">
      <span>当前患者</span>
      <b>{{ session.profile.profile?.name_alias }}</b>
      <span>{{ session.profile.profile?.sex }} · {{ session.profile.profile?.age }} 岁 · {{ session.profile.profile?.visit_type }}</span>
      <span class="mono">{{ session.patientId }}</span>
    </div>
    <span :class="['mode-chip', modeClass]">{{ modeText }}</span>
  </header>

  <div class="safety-banner">
    <b>安全边界：</b>AI 不自动诊断 · 不自动开方 · 不自动改药 · 不自动修改治疗方案 —— 所有关键诊疗输出均为辅助草稿，必须经医生确认后才可写入可信 Memory。
  </div>

  <nav class="stage-nav">
    <router-link
      v-for="item in navItems"
      :key="item.to"
      :to="item.to"
      :class="{ active: isActive(item.to) }"
    >
      <span class="step">{{ item.step }}</span>
      {{ item.label }}
      <span :class="['stage-state', stateClass(item.stage)]">{{ stateText(item.stage) }}</span>
    </router-link>
    <span class="nav-note">虚构模拟患者数据 · 仅供 Demo 演示</span>
  </nav>

  <router-view />

  <footer class="footer">
    医生AI Copilot Agentic Workflow · Doctor Dashboard 原型 —— 展示「AI辅助 / 医生确认 / 连续照护闭环」三条主线 · 数据为完全虚构的模拟数据
  </footer>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { session, bootstrap } from './store/sessionStore.js'

const route = useRoute()

const navItems = [
  { to: '/pre-visit', step: 1, label: '诊前', stage: 'pre_visit' },
  { to: '/during-visit', step: 2, label: '诊中', stage: 'during_visit' },
  { to: '/post-visit', step: 3, label: '诊后', stage: 'post_visit' },
]

onMounted(bootstrap)

const isActive = (to) => route.path === to

const anyDegraded = computed(
  () =>
    session.bootDegraded ||
    Object.values(session.stages).some((s) => s.degraded),
)
const modeText = computed(() => {
  if (session.apiMode === 'mock') return 'Mock 数据层'
  return anyDegraded.value ? '真实后端不可达 · 已降级 Mock' : '已连接 Runtime API'
})
const modeClass = computed(() => {
  if (session.apiMode === 'mock') return 'mock'
  return anyDegraded.value ? 'degraded' : 'real'
})

function stageReview(stage) {
  return session.stages[stage]?.review || null
}
function stateText(stage) {
  const review = stageReview(stage)
  if (review) {
    if (review.decision === 'reject') return '已拒绝'
    return review.decision === 'modify' ? '已修改确认' : '已确认'
  }
  return session.stages[stage]?.state ? '待医生确认' : '未运行'
}
function stateClass(stage) {
  const review = stageReview(stage)
  if (!review) return ''
  return review.decision === 'reject' ? 'rejected' : 'done'
}
</script>
