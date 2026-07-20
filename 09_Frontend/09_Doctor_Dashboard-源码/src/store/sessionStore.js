import { reactive, computed } from 'vue'
import * as api from '../api/client.js'

export const PATIENT_ID = 'SIM-HTN-001'

const STAGE_NAMES = ['pre_visit', 'during_visit', 'post_visit']

function emptyStage() {
  return {
    state: null, // Workflow State（runtime_adapter._workflow_response 同构）
    audit: null, // 审计日志
    review: null, // 医生经 Dashboard 提交的 Human Review 记录
    loading: false,
    reviewing: false,
    error: null,
    degraded: false, // real 模式降级标记
  }
}

export const session = reactive({
  apiMode: api.apiMode, // 'mock' | 'real'
  patientId: PATIENT_ID,
  profile: null,
  memory: null,
  bootLoading: false,
  bootError: null,
  bootDegraded: false,
  stages: {
    pre_visit: emptyStage(),
    during_visit: emptyStage(),
    post_visit: emptyStage(),
  },
})

/** 启动：加载患者档案 + 连续照护 Memory（诊前页面的患者上下文区依赖） */
export async function bootstrap() {
  if (session.profile && session.memory) return
  session.bootLoading = true
  session.bootError = null
  try {
    const [profile, memory] = await Promise.all([
      api.getPatientProfile(session.patientId),
      api.getPatientMemory(session.patientId),
    ])
    session.profile = profile
    session.memory = memory
    session.bootDegraded = Boolean(profile.__degraded || memory.__degraded)
  } catch (e) {
    session.bootError = e.message
  } finally {
    session.bootLoading = false
  }
}

/** 运行某阶段 Workflow（幂等：已加载则不重复执行） */
export async function ensureStage(name, { force = false } = {}) {
  const stage = session.stages[name]
  if (!stage || (stage.state && !force)) return
  stage.loading = true
  stage.error = null
  try {
    const state = await api.runWorkflow(name, buildRunPayload(name))
    stage.state = state
    stage.degraded = Boolean(state.__degraded)
    stage.audit = await api.getWorkflowAudit(state.workflow_id)
  } catch (e) {
    stage.error = e.message
  } finally {
    stage.loading = false
  }
}

function buildRunPayload(name) {
  const payload = { patient_id: session.patientId }
  // 与 08_API_Service 契约对齐：串起上一阶段的 workflow_id，形成闭环链路
  if (name === 'during_visit' && session.stages.pre_visit.state) {
    payload.pre_visit_workflow_id = session.stages.pre_visit.state.workflow_id
  }
  if (name === 'post_visit' && session.stages.during_visit.state) {
    payload.during_visit_workflow_id = session.stages.during_visit.state.workflow_id
  }
  return payload
}

/** 提交医生确认（approve / modify / reject） */
export async function submitReview(name, { decision, modifiedContent, reviewComment }) {
  const stage = session.stages[name]
  if (!stage?.state) throw new Error('Workflow 尚未运行，无法确认')
  stage.reviewing = true
  stage.error = null
  try {
    const record = await api.submitHumanReview(stage.state.workflow_id, {
      node_name: stage.state.current_node,
      decision,
      doctor_id: 'DOCTOR-DEMO-001',
      modified_content: modifiedContent || undefined,
      review_comment: reviewComment || undefined,
    })
    stage.review = record
    // 重新拉取 state：真实服务 / mock 都会把确认结果写回
    stage.state = await api.getWorkflowState(stage.state.workflow_id)
    return record
  } catch (e) {
    stage.error = e.message
    throw e
  } finally {
    stage.reviewing = false
  }
}

// ---------- 派生展示状态 ----------

export function stageView(name) {
  const stage = session.stages[name]
  return computed(() => {
    const s = stage.state
    const review = stage.review
    const decision = review?.decision || null
    const simulated = s?.doctor_confirmation?.human_decision || null
    return {
      stage,
      state: s,
      nodeOutputs: s?.node_outputs || {},
      review,
      /** 医生经 Dashboard 的确认结果（优先）；否则为 Runtime 模拟确认 */
      effectiveDecision: decision,
      simulatedDecision: simulated,
      confirmationId: review?.doctor_confirmation_id || s?.doctor_confirmation?.doctor_confirmation_id || null,
      memoryWriteAllowed: review ? review.memory_write_allowed : null,
      confirmed: Boolean(review && (review.decision === 'approve' || review.decision === 'modify')),
      rejected: Boolean(review && review.decision === 'reject'),
    }
  })
}

export const stageNames = STAGE_NAMES
