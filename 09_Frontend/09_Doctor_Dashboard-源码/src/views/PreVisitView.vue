<template>
  <main class="page">
    <div class="page-head">
      <h1><span class="stage-badge">诊前阶段</span>诊前工作台 · 信息采集与接诊准备</h1>
      <p class="desc">让医生在接诊前快速理解患者背景、近期风险、AI 整理结果与待确认信息 —— 对应 <b>诊前信息采集 Workflow</b>（POST /workflow/pre_visit）。</p>
      <div style="margin:10px 0 12px"><CareLoopBar current="pre_visit" /></div>
      <StatusTagRow :confirm-status="confirmStatus" :memory-status="memoryStatus" />
    </div>

    <div v-if="view.stage.error" class="error-box" style="margin-bottom:16px">加载失败：{{ view.stage.error }}</div>
    <PatientJourneyTimeline current="pre_visit" style="margin-bottom:16px" />

    <div class="workbench-grid">
      <!-- 左列：患者上下文区 -->
      <div class="col">
        <div class="col-title">患者上下文区</div>
        <PatientCard :profile="session.profile" :memory="session.memory" />
        <BpTrendChart :vitals="session.profile?.recent_vitals || []" />
        <RiskProfileCard :risk-profile="session.profile?.risk_profile" />
      </div>

      <!-- 中列：AI 输出区 -->
      <div class="col">
        <div class="col-title">AI 输出区（辅助草稿，非诊断结论）</div>

        <section class="card">
          <div class="card-head">
            <h2>AI 整理结果</h2>
            <span class="tag ai">AI整理结果 · 辅助草稿</span>
            <div class="spacer"></div>
            <span class="tag neutral mono" v-if="view.state">pre_visit</span>
          </div>
          <div class="card-body" v-if="summary">
            <div class="ai-draft">
              <span class="draft-mark">AI 诊前摘要草稿</span>
              <p class="draft-text">{{ displayDraftText }}</p>
            </div>

            <div class="section-label">关键事实</div>
            <ul class="clean-list">
              <li v-for="(f, i) in keyFacts" :key="i">{{ f }}</li>
            </ul>

            <div class="section-label">风险线索</div>
            <div class="tag-row">
              <span v-for="(s, i) in riskSignals" :key="i" class="tag warn">{{ s }}</span>
            </div>

            <template v-if="clues">
              <div class="section-label">连续照护线索（承接上一次诊后回流）</div>
              <dl class="kv" style="grid-template-columns: 110px 1fr">
                <dt>血压模式</dt>
                <dd>{{ clues.bp_pattern }}</dd>
                <dt>依从性信号</dt>
                <dd>{{ clues.adherence_signal }}</dd>
                <dt>生活方式信号</dt>
                <dd>{{ clues.lifestyle_signal }}</dd>
              </dl>
            </template>

            <div class="safety-note">本卡内容为 AI 辅助整理结果，不得视为最终诊断或治疗结论；采纳前需医生逐项核对。</div>
          </div>
          <div v-else class="loading-box"><span class="spinner"></span>正在运行诊前 Workflow…</div>
        </section>

        <section class="card">
          <div class="card-head">
            <h2>待确认信息</h2>
            <span class="tag neutral">{{ missingQuestions.length }} 项</span>
          </div>
          <div class="card-body">
            <ul class="clean-list" v-if="missingQuestions.length">
              <li v-for="(q, i) in missingQuestions" :key="i" style="display:flex; align-items:center; gap:10px">
                <span style="flex:1">{{ q }}</span>
                <span v-if="view.confirmed" class="tag ok">已确认</span>
                <span v-else class="tag warn">待确认</span>
              </li>
            </ul>
            <p v-else class="note-text">加载中…</p>
            <p class="note-text" style="margin:10px 0 0">
              以上问题来自 AI 对缺失信息的识别（identify_key_and_missing_information），供医生在接诊时当面核实，不构成 AI 判断。
            </p>
          </div>
        </section>
      </div>

      <!-- 右列：医生确认区 -->
      <div class="col right">
        <div class="col-title">医生确认区</div>
        <HumanReviewPanel
          v-if="view.state"
          node-name="doctor_review_pre_visit_summary"
          :draft-fields="draftFields"
          :review="view.review"
          :reviewing="view.stage.reviewing"
          :error="view.stage.error || ''"
          @submit="onSubmitReview"
          @reset="onResetReview"
        />
        <div v-else class="card"><div class="loading-box"><span class="spinner"></span>等待 Workflow 加载…</div></div>

        <section class="card">
          <div class="card-head"><h2>确认状态</h2></div>
          <div class="card-body">
            <dl class="kv" style="grid-template-columns: 120px 1fr">
              <dt>当前确认状态</dt>
              <dd>
                <span v-if="view.review" class="tag" :class="view.rejected ? 'danger' : 'ok'">{{ view.review.decision }}</span>
                <span v-else class="tag warn">待医生确认</span>
              </dd>
              <dt>医生确认 ID</dt>
              <dd class="mono">{{ view.confirmationId || '—' }}</dd>
              <dt>是否已写入 Memory</dt>
              <dd>
                <span v-if="view.confirmed" class="tag ok">已写入（pre_visit_memory）</span>
                <span v-else-if="view.rejected" class="tag danger">已阻断写入</span>
                <span v-else class="tag warn">未写入 · 待确认门禁</span>
              </dd>
            </dl>
            <p class="note-text" style="margin:10px 0 0">
              写回节点 write_confirmed_pre_visit_context 仅在 approve / modify 后执行；确认后的诊前上下文将作为诊中 Workflow 的输入。
            </p>
            <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap">
              <router-link to="/during-visit" custom v-slot="{ navigate }">
                <button class="btn primary sm" :disabled="!view.confirmed" @click="navigate">
                  进入诊中工作台 →
                </button>
              </router-link>
              <span v-if="!view.confirmed" class="note-text" style="align-self:center">需先完成医生确认</span>
            </div>
          </div>
        </section>
      </div>
    </div>

    <div style="margin-top:16px">
      <WorkflowTracePanel :state="view.state" :audit="view.stage.audit" style="margin-bottom:16px" />
      <AuditTrail :state="view.state" :audit="view.stage.audit" />
    </div>
  </main>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import CareLoopBar from '../components/CareLoopBar.vue'
import StatusTagRow from '../components/StatusTagRow.vue'
import PatientJourneyTimeline from '../components/PatientJourneyTimeline.vue'
import PatientCard from '../components/PatientCard.vue'
import BpTrendChart from '../components/BpTrendChart.vue'
import RiskProfileCard from '../components/RiskProfileCard.vue'
import HumanReviewPanel from '../components/HumanReviewPanel.vue'
import WorkflowTracePanel from '../components/WorkflowTracePanel.vue'
import AuditTrail from '../components/AuditTrail.vue'
import { session, bootstrap, ensureStage, submitReview, stageView } from '../store/sessionStore.js'

const STAGE = 'pre_visit'
const view = stageView(STAGE)

onMounted(async () => {
  await bootstrap()
  await ensureStage(STAGE)
})

const nodeOutputs = computed(() => view.value.state?.node_outputs || {})
const identify = computed(() => nodeOutputs.value.identify_key_and_missing_information?.output || {})
const summary = computed(() => nodeOutputs.value.generate_structured_pre_visit_summary?.output || null)

const keyFacts = computed(() => identify.value.key_facts || [])
const riskSignals = computed(() => identify.value.risk_signals || [])
const missingQuestions = computed(() => identify.value.missing_questions || summary.value?.key_questions || [])
const clues = computed(() => summary.value?.continuous_care_clues || null)

// modify 后被医生修改的内容优先展示（后续只能使用医生修改后的内容）
const displayDraftText = computed(() => {
  if (view.value.review?.decision === 'modify' && view.value.review.modified_content?.draft_text) {
    return view.value.review.modified_content.draft_text
  }
  return summary.value?.draft_text || ''
})

const draftFields = computed(() => [
  { key: 'draft_text', label: 'AI 诊前摘要草稿', value: summary.value?.draft_text || '' },
])

const confirmStatus = computed(() => view.value.review?.decision || 'pending')
const memoryStatus = computed(() =>
  view.value.confirmed ? 'written' : view.value.rejected ? 'blocked' : 'pending',
)

async function onSubmitReview(payload) {
  try {
    await submitReview(STAGE, payload)
  } catch {
    /* error 已写入 stage.error */
  }
}
function onResetReview() {
  session.stages[STAGE].review = null
  ensureStage(STAGE, { force: true })
}
</script>
