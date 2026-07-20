<template>
  <main class="page">
    <div class="page-head">
      <h1><span class="stage-badge">诊后阶段</span>诊后工作台 · 医嘱执行与连续照护回流</h1>
      <p class="desc">让医生看到随访任务、患者反馈、Memory 变化与下一次诊前上下文 —— 对应 <b>诊后医嘱执行 Workflow</b>（POST /workflow/post_visit）。</p>
      <div style="margin:10px 0 12px"><CareLoopBar current="post_visit" :highlight-backflow="true" /></div>
      <StatusTagRow :confirm-status="confirmStatus" :memory-status="memoryStatus" />
    </div>

    <div v-if="view.stage.error" class="error-box" style="margin-bottom:16px">加载失败：{{ view.stage.error }}</div>
    <PatientJourneyTimeline current="next_previsit" style="margin-bottom:16px" />

    <!-- 连续照护闭环核心展示点：下一次诊前上下文（高优先级位置） -->
    <section class="card" style="border:1.5px solid #ddd6fe; margin-bottom:16px">
      <div class="card-head" style="background:linear-gradient(90deg,#f6f1ff,#fbf8ff)">
        <h2>下一次诊前上下文 · 连续照护回流</h2>
        <span class="tag trace">闭环核心</span>
        <div class="spacer"></div>
        <span v-if="view.confirmed" class="tag ok">已写回可信 Memory</span>
        <span v-else class="tag warn">待医生确认后写回</span>
      </div>
      <div class="card-body">
        <div class="ai-draft" style="border-color:#ddd6fe;background:linear-gradient(180deg,#fbf8ff,#f6f1ff)">
          <span class="draft-mark" style="background:#7c3aed">AI 汇总 · 医生确认后回流</span>
          <p class="draft-text">{{ displayNextContext || '加载中…' }}</p>
        </div>
        <dl class="kv" style="grid-template-columns: 140px 1fr; margin-top:12px">
          <dt>回流路径</dt>
          <dd class="mono" style="font-size:12px">
            诊后反馈事件 → AI 异常汇总 → 医生确认（{{ view.confirmationId || '待确认' }}）→ post_visit_memory.next_previsit_summary → 下一次诊前摘要顶部
          </dd>
          <dt>最后确认 ID</dt>
          <dd class="mono">{{ session.memory?.last_confirmation_id || '—' }}</dd>
        </dl>
        <p class="note-text" style="margin:10px 0 0">
          这是连续照护闭环的核心：本次诊后的漏服、异常血压与症状变化，经医生确认后成为医生下次接诊时最先看到的上下文 —— 医生不再从零开始接诊。
        </p>
      </div>
    </section>

    <div class="workbench-grid">
      <!-- 左列：随访任务与反馈 -->
      <div class="col">
        <div class="col-title">随访任务与患者反馈</div>

        <section class="card">
          <div class="card-head">
            <h2>随访任务</h2>
            <span class="tag neutral">{{ followupTasks.length }} 项 · 任务管理</span>
          </div>
          <div class="card-body tight">
            <div class="clean-list" v-if="followupTasks.length" style="padding: 4px 0">
              <div v-for="t in followupTasks" :key="t.task_id" class="tl-card">
                <div class="tl-head">
                  <b>{{ t.title }}</b>
                  <span class="tag neutral">{{ typeLabel(t.type) }}</span>
                </div>
                <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center; font-size:12px">
                  <span class="note-text">频率：{{ t.schedule }}</span>
                  <span class="tag warn">{{ statusLabel(t.status) }}</span>
                </div>
                <div class="note-text" style="margin-top:2px">来源：{{ t.source }}</div>
              </div>
            </div>
            <div v-else class="loading-box"><span class="spinner"></span>加载随访任务…</div>
            <p class="note-text" style="margin:8px 0 4px">任务来自医生确认后的医嘱拆解（decompose_orders_into_tasks），是任务管理，不是自动医疗行为。</p>
          </div>
        </section>

        <section class="card">
          <div class="card-head">
            <h2>患者反馈事件 · 7 天时间线</h2>
            <span class="tag danger" v-if="reviewRequiredCount">{{ reviewRequiredCount }} 条需医生复核</span>
          </div>
          <div class="card-body">
            <div class="timeline" v-if="feedbackEvents.length">
              <div v-for="e in feedbackEvents" :key="e.event_id" class="tl-item" :class="flagClass(e)">
                <div class="tl-card" :class="{ 'need-review': e.doctor_review_required }">
                  <div class="tl-head">
                    <span class="tl-date">第 {{ e.day }} 天 · {{ e.date }}</span>
                    <span class="tag neutral">{{ eventTypeLabel(e.type) }}</span>
                    <span class="tag" :class="flagTagClass(e)">{{ e.agent_flag }}</span>
                    <span v-if="e.doctor_review_required" class="tag danger">需医生复核</span>
                  </div>
                  <div>{{ eventText(e) }}</div>
                </div>
              </div>
            </div>
            <div v-else class="loading-box"><span class="spinner"></span>加载反馈事件…</div>
          </div>
        </section>
      </div>

      <!-- 中列：AI 输出区 -->
      <div class="col">
        <div class="col-title">AI 输出区（汇总草稿，待确认）</div>

        <section class="card">
          <div class="card-head">
            <h2>AI 诊后执行摘要</h2>
            <span class="tag ai">AI 汇总草稿 · 待医生确认</span>
          </div>
          <div class="card-body" v-if="execSummary">
            <div class="tag-row" style="margin-bottom:10px">
              <span class="tag neutral">反馈事件 {{ execSummary.event_count }} 条</span>
              <span class="tag danger">异常事件 {{ execSummary.abnormal_event_count }} 条</span>
            </div>
            <div class="section-label">异常事件（需医生复核）</div>
            <ul class="clean-list">
              <li v-for="e in execSummary.abnormal_events || []" :key="e.event_id">
                <b>{{ e.date }}</b> · {{ eventText(e) }}
                <span class="tag danger" style="margin-left:6px">{{ e.agent_flag }}</span>
              </li>
            </ul>
            <div class="section-label">风险更新草稿</div>
            <ul class="clean-list">
              <li v-for="(r, i) in riskUpdateDraft" :key="i">{{ r }}</li>
            </ul>
            <div class="safety-note">{{ summaryNote || '仅供医生审核，不自动调整医嘱。' }}异常摘要写入 Memory 前必须经医生确认。</div>
          </div>
          <div v-else class="loading-box"><span class="spinner"></span>汇总诊后执行情况…</div>
        </section>

        <MemoryDiff
          v-if="memoryWriteback"
          :before="memoryWriteback.before"
          :after="memoryWriteback.after"
          section="post_visit_memory"
          :confirmation-id="view.confirmationId || 'HITL-POST-001'"
        />
      </div>

      <!-- 右列：医生确认区 -->
      <div class="col right">
        <div class="col-title">医生确认区</div>
        <HumanReviewPanel
          v-if="view.state"
          node-name="doctor_review_post_visit_status"
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
            <dl class="kv" style="grid-template-columns: 130px 1fr">
              <dt>诊后确认结果</dt>
              <dd>
                <span v-if="view.review" class="tag" :class="view.rejected ? 'danger' : 'ok'">{{ view.review.decision }}</span>
                <span v-else class="tag warn">待医生确认</span>
              </dd>
              <dt>医生确认 ID</dt>
              <dd class="mono">{{ view.confirmationId || '—' }}</dd>
              <dt>是否已写回 Memory</dt>
              <dd>
                <span v-if="view.confirmed" class="tag ok">已写回（post_visit_memory）</span>
                <span v-else-if="view.rejected" class="tag danger">已阻断写回</span>
                <span v-else class="tag warn">未写回 · 待确认门禁</span>
              </dd>
            </dl>
            <div style="margin-top:12px; padding-top:10px; border-top:1px dashed var(--line)">
              <div class="section-label" style="margin-top:0">闭环验证</div>
              <router-link to="/pre-visit" custom v-slot="{ navigate }">
                <button class="btn modify sm" @click="navigate">↩ 回到诊前，查看回流后的患者摘要</button>
              </router-link>
              <p class="note-text" style="margin:8px 0 0">诊前工作台的患者摘要卡顶部即展示本次写回的「上一次诊后回流线索」。</p>
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
import HumanReviewPanel from '../components/HumanReviewPanel.vue'
import MemoryDiff from '../components/MemoryDiff.vue'
import WorkflowTracePanel from '../components/WorkflowTracePanel.vue'
import AuditTrail from '../components/AuditTrail.vue'
import { session, bootstrap, ensureStage, submitReview, stageView } from '../store/sessionStore.js'

const STAGE = 'post_visit'
const view = stageView(STAGE)

onMounted(async () => {
  await bootstrap()
  await ensureStage(STAGE)
})

const nodeOutputs = computed(() => view.value.state?.node_outputs || {})
const trackOutput = computed(() => nodeOutputs.value.create_and_track_followup_tasks?.output || {})
const summaryOutput = computed(() => nodeOutputs.value.summarize_execution_and_flag_risks?.output || {})
const memoryWriteback = computed(
  () => nodeOutputs.value.write_confirmed_post_visit_feedback?.output || null,
)

const followupTasks = computed(() => trackOutput.value.create_followup_tasks || [])
const feedbackEvents = computed(() =>
  (trackOutput.value.record_patient_feedback || []).map((r) => r.feedback).filter(Boolean),
)
const execSummary = computed(() => summaryOutput.value.execution_summary || null)
const riskUpdateDraft = computed(() => summaryOutput.value.risk_update_draft || [])
const summaryNote = computed(() => summaryOutput.value.safety_note || '')
const reviewRequiredCount = computed(
  () => feedbackEvents.value.filter((e) => e.doctor_review_required).length,
)

const displayNextContext = computed(() => {
  if (view.value.review?.decision === 'modify' && view.value.review.modified_content?.next_pre_visit_context) {
    return view.value.review.modified_content.next_pre_visit_context
  }
  return (
    summaryOutput.value.next_pre_visit_context ||
    session.memory?.post_visit_memory?.next_previsit_summary ||
    ''
  )
})

const draftFields = computed(() => [
  {
    key: 'next_pre_visit_context',
    label: '下一次诊前上下文（回流摘要）',
    value: summaryOutput.value.next_pre_visit_context || '',
  },
])

const confirmStatus = computed(() => view.value.review?.decision || 'pending')
const memoryStatus = computed(() =>
  view.value.confirmed ? 'written' : view.value.rejected ? 'blocked' : 'pending',
)

const TYPE_LABELS = { medication: '用药', monitoring: '监测', lifestyle: '生活方式', review: '复查', followup: '随访' }
const EVENT_TYPE_LABELS = { bp_report: '血压上报', medication_report: '服药上报', lifestyle_report: '生活方式', followup_summary: '随访小结' }
const STATUS_LABELS = { pending: '待执行', in_progress: '进行中', completed: '已完成' }
const typeLabel = (t) => TYPE_LABELS[t] || t
const eventTypeLabel = (t) => EVENT_TYPE_LABELS[t] || t
const statusLabel = (s) => STATUS_LABELS[s] || s

function flagClass(e) {
  if (e.doctor_review_required) return 'flag-danger'
  if (e.agent_flag === 'observe' || e.agent_flag === 'partial_adherence') return 'flag-warn'
  return 'flag-normal'
}
function flagTagClass(e) {
  if (e.doctor_review_required) return 'danger'
  if (e.agent_flag === 'observe' || e.agent_flag === 'partial_adherence') return 'warn'
  return 'ok'
}
function eventText(e) {
  const p = e.payload || {}
  switch (e.type) {
    case 'bp_report':
      return `家庭血压 早 ${p.morning || '—'} / 晚 ${p.evening || '—'} mmHg；症状：${p.symptom || '无'}`
    case 'medication_report':
      return p.taken ? `已按时服药（${p.note || '按时服药'}）` : `漏服药物 —— 原因：${p.reason || '未说明'}`
    case 'lifestyle_report':
      return `低盐饮食：${p.salt_control || '—'}；睡眠：${p.sleep || '—'}；运动：${p.exercise || '—'}`
    case 'followup_summary':
      return `血压趋势：${p.bp_trend || '—'}；漏服 ${p.missed_medication_count ?? '—'} 次；症状：${p.symptom || '—'}`
    default:
      return JSON.stringify(p)
  }
}

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
