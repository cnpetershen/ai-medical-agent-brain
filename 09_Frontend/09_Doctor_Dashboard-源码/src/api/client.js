/**
 * API Client —— 与 07_API_Spec / 08_API_Service 对齐的统一接口层。
 *
 * 两种模式：
 *  - real：经 vite dev proxy（/api -> VITE_API_TARGET）调用真实 Runtime API Service
 *  - mock：内置 mock engine，数据为真实 Runtime 输出的裁剪副本（契约一致）
 *
 * real 模式请求失败时自动降级到 mock，并在返回值上标记 __degraded，
 * UI 顶部会显示「已降级为 Mock 数据」。
 */

import * as mockEngine from './mock/engine.js'

const MODE = import.meta.env.VITE_API_MODE || 'mock'
const BASE = (import.meta.env.VITE_API_BASE || '/api').replace(/\/$/, '')
const TIMEOUT_MS = 30000

export const apiMode = MODE === 'real' ? 'real' : 'mock'

async function http(method, path, body) {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS)
  try {
    const resp = await fetch(BASE + path, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    })
    if (!resp.ok) {
      const detail = await resp.text().catch(() => '')
      const err = new Error(`HTTP ${resp.status}: ${detail || resp.statusText}`)
      err.status = resp.status
      throw err
    }
    return await resp.json()
  } finally {
    clearTimeout(timer)
  }
}

/** real 模式调用，失败时降级 mock */
async function call(method, path, body, mockFn) {
  if (apiMode === 'real') {
    try {
      return await http(method, path, body)
    } catch (e) {
      console.warn('[api] real backend unreachable, fallback to mock:', e.message)
      const data = await mockFn()
      return markDegraded(data)
    }
  }
  return mockFn()
}

function markDegraded(data) {
  if (data && typeof data === 'object' && !Array.isArray(data)) {
    Object.defineProperty(data, '__degraded', { value: true, enumerable: false })
  }
  return data
}

// ---------- Workflow API ----------

export function runWorkflow(name, payload = {}) {
  return call('POST', `/workflow/${name}`, payload, () => mockEngine.runWorkflow(name, payload))
}

export function getWorkflowState(workflowId) {
  return call('GET', `/workflow/${workflowId}/state`, null, () => mockEngine.getWorkflowState(workflowId))
}

export function getWorkflowAudit(workflowId) {
  return call('GET', `/workflow/${workflowId}/audit`, null, () => mockEngine.getWorkflowAudit(workflowId))
}

// ---------- Query API ----------

export function getPatientProfile(patientId) {
  return call('GET', `/patient/${patientId}/profile`, null, () => mockEngine.getPatientProfile(patientId))
}

export function getPatientMemory(patientId, section = 'all') {
  return call('GET', `/patient/${patientId}/memory?section=${section}`, null, () =>
    mockEngine.getPatientMemory(patientId, section),
  )
}

// ---------- Human Review API ----------

export function submitHumanReview(workflowId, payload) {
  return call('POST', `/human-review/${workflowId}`, payload, () =>
    mockEngine.submitHumanReview(workflowId, payload),
  )
}
