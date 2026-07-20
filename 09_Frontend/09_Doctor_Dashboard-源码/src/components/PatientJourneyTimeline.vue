<template>
  <section class="card journey-panel">
    <div class="card-head">
      <h2>Patient Journey Timeline · 连续照护闭环</h2>
      <span class="tag trace">从本次诊前到下一次诊前</span>
    </div>
    <div class="card-body">
      <div class="journey-line">
        <div v-for="item in items" :key="item.key" class="journey-step" :class="{ active: item.key === current }">
          <div class="journey-dot">{{ item.index }}</div>
          <div class="journey-card">
            <b>{{ item.title }}</b>
            <p>{{ item.desc }}</p>
            <span class="tag" :class="item.tagClass">{{ item.tag }}</span>
          </div>
        </div>
      </div>
      <div class="safety-note">
        这条线展示 Agentic Workflow 的核心差异：AI 不与医生闲聊，而是在每个阶段执行可追踪节点，医生确认后才把结果回流到 Patient Memory。
      </div>
    </div>
  </section>
</template>

<script setup>
defineProps({
  current: { type: String, default: 'pre_visit' },
})

const items = [
  { index: 1, key: 'pre_visit', title: '诊前：患者信息整理', desc: '整合患者档案、近期血压、风险画像与缺失信息。', tag: 'AI辅助整理', tagClass: 'ai' },
  { index: 2, key: 'during_visit', title: '诊中：RAG辅助 + 医生确认', desc: '检索指南依据，生成辅助草稿，由医生确认。', tag: '医生主导', tagClass: 'ok' },
  { index: 3, key: 'post_visit', title: '诊后：随访任务', desc: '将医生确认后的管理要求拆解为任务，仅做执行跟踪。', tag: '任务管理', tagClass: 'neutral' },
  { index: 4, key: 'feedback', title: '患者反馈', desc: '记录血压、服药、症状与生活方式反馈事件。', tag: '反馈事件', tagClass: 'warn' },
  { index: 5, key: 'memory', title: 'Patient Memory 更新', desc: '医生确认后写回异常摘要、依从性与下次关注点。', tag: '可信写回', tagClass: 'ok' },
  { index: 6, key: 'next_previsit', title: '下一次诊前上下文', desc: '回流摘要进入下一次诊前，形成连续照护闭环。', tag: '闭环完成', tagClass: 'trace' },
]
</script>
