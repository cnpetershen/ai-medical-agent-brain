<template>
  <main class="page">
    <div class="page-head">
      <h1><span class="stage-badge">诊中阶段</span>诊中工作台 · 知识依据与辅助决策</h1>
      <p class="desc">让医生在诊中看到可追溯的知识依据、AI 辅助建议、医嘱草稿与确认状态 —— 对应 <b>诊中辅助决策 Workflow</b>（POST /workflow/during_visit）。</p>
      <div style="margin:10px 0 12px"><CareLoopBar current="during_visit" /></div>
      <StatusTagRow :confirm-status="confirmStatus" :memory-status="memoryStatus" />
    </div>

    <div v-if="needPreVisit" class="error-box" style="margin-bottom:16px; background:var(--warn-soft); border-color:var(--warn-line); color:var(--warn)">
      诊前阶段尚未完成医生确认。建议先在<router-link to="/pre-visit" style="color:inherit">诊前工作台</router-link>完成确认，形成连续照护链路；当前展示的为 Runtime 独立运行的模拟输出。
    </div>
    <div v-if="view.stage.error" class="error-box" style="margin-bottom:16px">加载失败：{{ view.stage.error }}</div>

    <div class="workbench-grid">
      <!-- 左列：患者上下文区 -->
      <div class="col">
        <div class="col-title">患者上下文区</div>

        <section class="card">
          <div class="card-head">
            <h2>诊前已确认上下文</h2>
            <span class="tag ok" v-if="preVisitClues">已医生确认</span>
          </div>
          <div class="card-body" v-if="preVisitClues">
            <dl class="kv" style="grid-template-columns: 100px 1fr">
              <dt>主诉</dt>
              <dd>{{ preVisitClues.chief_complaint }}</dd>
              <dt>血压模式</dt>
              <dd>{{ preVisitClues.bp_pattern }}</dd>
              <dt>依从性信号</dt>
              <dd>{{ preVisitClues.adherence_signal }}</dd>
              <dt>生活方式</dt>
              <dd>{{ preVisitClues.lifestyle_signal }}</dd>
            </dl>
            <p class="note-text" style="margin:10px 0 0">来自 pre_visit_memory（医生确认后写入的可信 Memory），是诊中 Workflow 的输入。</p>
          </div>
          <div v-else class="loading-box"><span class="spinner"></span>加载中…</div>
        </section>

        <RagEvidenceCard :rag="rag" :assistance="assistance" />
      </div>

      <!-- 中列：AI 输出区 -->
      <div class="col">
        <div class="col-title">AI 输出区（辅助草稿，非最终判断）</div>

        <section class="card">
          <div class="card-head">
            <h2>辅助建议</h2>
            <span class="tag ai">辅助建议草稿</span>
          </div>
          <div class="card-body" v-if="assistance">
            <div class="section-label">诊中关键上下文</div>
            <div class="tag-row">
              <span v-for="(c, i) in assistance.key_context || []" :key="i" class="tag neutral">{{ c }}</span>
            </div>
            <div class="section-label">医生可核对的管理方向</div>
            <ul class="clean-list">
              <li v-for="(a, i) in assistance.clinical_assistance || []" :key="i">
                {{ a }}
                <div class="note-text" style="margin-top:2px">依据：{{ (assistance.knowledge_references || []).join('、') }}</div>
              </li>
            </ul>
            <div class="safety-note">{{ assistance.safety_note }}</div>
          </div>
          <div v-else class="loading-box"><span class="spinner"></span>整理诊中上下文…</div>
        </section>

        <section class="card">
          <div class="card-head">
            <h2>医嘱草稿</h2>
            <span class="tag ai">AI 草稿</span>
            <div class="spacer"></div>
            <span class="tag warn">{{ orderDraft?.medical_decision_status || '待医生确认' }}</span>
          </div>
          <div class="card-body" v-if="orderDraft">
            <div class="ai-draft">
              <span class="draft-mark">管理计划草稿 · 待医生确认</span>
              <p class="draft-text">{{ displayOrder }}</p>
            </div>
            <div class="section-label">医生辅助核对点</div>
            <ul class="clean-list">
              <li v-for="(d, i) in orderDraft.doctor_assistance || []" :key="i">{{ d }}</li>
            </ul>
            <div class="safety-note">{{ orderDraft.safety_note }} —— 本草稿不得直接成为「已生效医嘱」，确认前不进入诊后任务。</div>
          </div>
          <div v-else class="loading-box"><span class="spinner"></span>生成医嘱草稿…</div>
        </section>
      </div>

      <!-- 右列：医生确认区 -->
      <div class="col right">
        <div class="col-title">医生确认区</div>
        <HumanReviewPanel
          v-if="view.state"
          node-name="doctor_review_during_visit_output"
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
              <dt>确认结果</dt>
              <dd>
                <span v-if="view.review" class="tag" :class="view.rejected ? 'danger' : 'ok'">{{ view.review.decision }}</span>
                <span v-else class="tag warn">待医生确认</span>
              </dd>
              <dt>医生确认 ID</dt>
              <dd class="mono">{{ view.confirmationId || '—' }}</dd>
              <dt>写入诊中 Memory</dt>
              <dd>
                <span v-if="view.confirmed" class="tag ok">已写入（in_visit_memory）</span>
                <span v-else-if="view.rejected" class="tag danger">已阻断写入</span>
                <span v-else class="tag warn">未写入 · 待确认门禁</span>
              </dd>
              <dt>已确认管理计划</dt>
              <dd v-if="view.confirmed">{{ confirmedPlan }}</dd>
              <dd v-else class="note-text">确认后可见</dd>
            </dl>
            <div style="margin-top:10px; display:flex; gap:8px; flex-wrap:wrap">
              <router-link to="/post-visit" custom v-slot="{ navigate }">
                <button class="btn primary sm" :disabled="!view.confirmed" @click="navigate">
                  进入诊后工作台 →
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
import HumanReviewPanel from '../components/HumanReviewPanel.vue'
import RagEvidenceCard from '../components/RagEvidenceCard.vue'
import WorkflowTracePanel from '../components/WorkflowTracePanel.vue'
import AuditTrail from '../components/AuditTrail.vue'
import { session, bootstrap, ensureStage, submitReview, stageView } from '../store/sessionStore.js'

const STAGE = 'during_visit'
const view = stageView(STAGE)

onMounted(async () => {
  await bootstrap()
  await ensureStage(STAGE)
})

const nodeOutputs = computed(() => view.value.state?.node_outputs || {})
const rag = computed(() => nodeOutputs.value.retrieve_medical_knowledge?.output || {})
const assistance = computed(() => nodeOutputs.value.organize_clinical_context?.output || null)
const orderDraft = computed(() => nodeOutputs.value.generate_order_draft?.output || null)

const preVisitClues = computed(() => session.memory?.pre_visit_memory || null)
const needPreVisit = computed(() => !session.stages.pre_visit.review)

const displayOrder = computed(() => {
  if (view.value.review?.decision === 'modify' && view.value.review.modified_content?.confirmed_order) {
    return view.value.review.modified_content.confirmed_order
  }
  return orderDraft.value?.confirmed_order || ''
})

const draftFields = computed(() => [
  { key: 'confirmed_order', label: '管理计划草稿', value: orderDraft.value?.confirmed_order || '' },
])

const confirmedPlan = computed(
  () => session.memory?.in_visit_memory?.confirmed_management_plan || displayOrder.value,
)

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
