/**
 * Mock Engine —— 与 08_API_Service（runtime_adapter.py）行为对齐的有状态模拟层。
 *
 * 数据来源：fixtures/ 下为真实 Runtime MVP 输出的裁剪副本（契约字段保持一致），
 * 患者为虚构模拟患者 SIM-HTN-001（王某），不包含任何真实患者数据。
 *
 * 与真实服务一致的行为：
 *  - runWorkflow 返回完整 Workflow State（Runtime 以模拟决策预跑全部节点）
 *  - submitHumanReview 校验 decision / modified_content，生成 doctor_confirmation_id，
 *    并把医生真实确认结果写回内存中的 workflow state（reject 时状态置为 rejected）
 */

import patientProfile from './fixtures/patient_profile.json'
import patientMemory from './fixtures/patient_memory.json'
import workflowPreVisit from './fixtures/workflow_pre_visit.json'
import workflowDuringVisit from './fixtures/workflow_during_visit.json'
import workflowPostVisit from './fixtures/workflow_post_visit.json'
import auditPreVisit from './fixtures/audit_pre_visit.json'
import auditDuringVisit from './fixtures/audit_during_visit.json'
import auditPostVisit from './fixtures/audit_post_visit.json'

const PATIENT_ID = 'SIM-HTN-001'

const WORKFLOW_FIXTURES = {
  pre_visit: workflowPreVisit,
  during_visit: workflowDuringVisit,
  post_visit: workflowPostVisit,
}

const AUDIT_FIXTURES = {
  pre_visit: auditPreVisit,
  during_visit: auditDuringVisit,
  post_visit: auditPostVisit,
}

const HUMAN_NODE_NAMES = {
  pre_visit: 'doctor_review_pre_visit_summary',
  during_visit: 'doctor_review_during_visit_output',
  post_visit: 'doctor_review_post_visit_status',
}

const CONFIRMATION_BASE_IDS = {
  pre_visit: 'HITL-PRE-001',
  during_visit: 'HITL-DURING-001',
  post_visit: 'HITL-POST-001',
}

const VALID_DECISIONS = ['approve', 'modify', 'reject']

/** workflow_id -> state（医生确认后会原地更新） */
const stateStore = new Map()
/** workflow_id -> review record */
const reviewStore = new Map()

const clone = (obj) => JSON.parse(JSON.stringify(obj))

function workflowResponse(state) {
  // 与 runtime_adapter._workflow_response 同构
  return {
    workflow_id: state.workflow_id,
    workflow_name: state.workflow_name,
    workflow_status: state.workflow_status,
    patient_id: state.patient_id,
    current_node: state.current_node,
    node_outputs: state.node_outputs,
    doctor_confirmation: state.doctor_confirmation,
    human_review_required: Boolean(state.doctor_confirmation),
    memory_context: state.memory_context,
    audit_log: state.audit_log || [],
    started_at: state.started_at,
    updated_at: state.updated_at,
  }
}

export async function runWorkflow(name, payload = {}) {
  const fixture = WORKFLOW_FIXTURES[name]
  if (!fixture) {
    throw httpError(400, `Unsupported workflow: ${name}`)
  }
  const patientId = payload.patient_id || PATIENT_ID
  if (patientId !== PATIENT_ID) {
    throw httpError(400, `Unknown patient_id: ${patientId}`)
  }
  const state = clone(fixture)
  stateStore.set(state.workflow_id, state)
  return workflowResponse(clone(state))
}

export async function getWorkflowState(workflowId) {
  const state = findState(workflowId)
  if (!state) throw httpError(404, `Workflow state not found: ${workflowId}`)
  return clone(state)
}

export async function getWorkflowAudit(workflowId) {
  const state = findState(workflowId)
  if (!state) throw httpError(404, `Workflow state not found: ${workflowId}`)
  const fixtureAudit = AUDIT_FIXTURES[state.workflow_name] || {}
  return clone({
    workflow_id: workflowId,
    workflow_name: state.workflow_name,
    workflow_status: state.workflow_status,
    audit_log: fixtureAudit.audit_log || state.audit_log || [],
    execution_log: fixtureAudit.execution_log || [],
  })
}

export async function getPatientProfile(patientId) {
  if (patientId !== PATIENT_ID) throw httpError(404, `Unknown patient_id: ${patientId}`)
  return clone(patientProfile)
}

export async function getPatientMemory(patientId, section = 'all') {
  if (patientId !== PATIENT_ID) throw httpError(404, `Unknown patient_id: ${patientId}`)
  if (section === 'all') return clone(patientMemory)
  if (!(section in patientMemory)) throw httpError(404, `Unknown memory section: ${section}`)
  return clone({
    patient_id: patientId,
    [section]: patientMemory[section],
    last_confirmation_id: patientMemory.last_confirmation_id,
  })
}

export async function submitHumanReview(workflowId, payload = {}) {
  const { decision, doctor_id, modified_content, review_comment } = payload
  if (!VALID_DECISIONS.includes(decision)) {
    throw httpError(400, `Invalid human decision: ${decision}`)
  }
  if (decision === 'modify' && !modified_content) {
    throw httpError(400, 'modified_content is required when decision is modify')
  }
  const state = findState(workflowId)
  if (!state) throw httpError(404, `Workflow state not found: ${workflowId}`)

  const workflowName = state.workflow_name
  const baseId = CONFIRMATION_BASE_IDS[workflowName]
  const confirmationId = decision === 'reject' ? `${baseId}-REJECT` : baseId
  const memoryWriteAllowed = decision === 'approve' || decision === 'modify'
  const nextAction = memoryWriteAllowed ? 'continue_workflow' : 'stop_workflow'

  const record = {
    workflow_id: workflowId,
    workflow_name: workflowName,
    node_name: HUMAN_NODE_NAMES[workflowName],
    decision,
    doctor_id: doctor_id || 'DOCTOR-DEMO-001',
    modified_content: modified_content || null,
    review_comment: review_comment || null,
    doctor_confirmation_id: confirmationId,
    memory_write_allowed: memoryWriteAllowed,
    next_action: nextAction,
    safety_note: '医生确认仅打开可信写回门禁，不自动诊断、不自动处方、不自动改药。',
  }
  reviewStore.set(workflowId, record)

  // 把医生真实确认写回内存中的 workflow state（与真实服务语义一致）
  state.doctor_confirmation = {
    human_decision: decision,
    confirmed_content: modified_content || state.doctor_confirmation?.confirmed_content || {},
    doctor_confirmation_id: confirmationId,
  }
  if (decision === 'reject') {
    state.workflow_status = 'rejected'
  }
  state.updated_at = new Date().toISOString().slice(0, 19)
  stateStore.set(workflowId, state)

  return clone(record)
}

/** 供 UI 查询某 workflow 已提交的医生确认记录 */
export function getLocalReview(workflowId) {
  return reviewStore.get(workflowId) || null
}

function findState(workflowId) {
  if (stateStore.has(workflowId)) return stateStore.get(workflowId)
  // 允许直接按 fixture 中的 workflow_id 查询（页面刷新后 stateStore 为空）
  for (const fixture of Object.values(WORKFLOW_FIXTURES)) {
    if (fixture.workflow_id === workflowId) {
      const state = clone(fixture)
      stateStore.set(workflowId, state)
      return state
    }
  }
  return null
}

function httpError(status, message) {
  const err = new Error(message)
  err.status = status
  return err
}
