<template>
  <section
    class="card review-panel"
    :class="{ confirmed: review && review.decision !== 'reject', rejected: review && review.decision === 'reject' }"
  >
    <div class="card-head">
      <h2>医生确认</h2>
      <span class="tag neutral mono" v-if="nodeName">{{ nodeName }}</span>
      <div class="spacer"></div>
      <span v-if="!review" class="tag warn"><span class="dot"></span>待医生确认</span>
      <span v-else-if="review.decision === 'approve'" class="tag ok"><span class="dot"></span>已确认 approve</span>
      <span v-else-if="review.decision === 'modify'" class="tag ok"><span class="dot"></span>已修改采纳 modify</span>
      <span v-else class="tag danger"><span class="dot"></span>已拒绝 reject</span>
    </div>

    <div class="card-body">
      <!-- 状态流转可视化 -->
      <div class="review-flow">
        <span class="node" :class="{ on: true }">AI 草稿已生成</span>
        <span class="arrow">→</span>
        <span class="node" :class="flowDecisionClass">{{ flowDecisionText }}</span>
        <span class="arrow">→</span>
        <span class="node" :class="flowMemoryClass">{{ flowMemoryText }}</span>
      </div>

      <!-- 未确认：三个决策按钮 -->
      <template v-if="!review">
        <p class="note-text" style="margin:0 0 10px">
          以上 AI 输出均为辅助草稿。请核对后选择处理方式 —— 确认或修改采纳后才会打开可信 Memory 写入门禁；拒绝则本次草稿作废，不写入任何可信状态。
        </p>
        <div class="review-actions">
          <button class="btn approve" :disabled="reviewing" @click="doSubmit('approve')">✓ 确认采纳（approve）</button>
          <button class="btn modify" :class="{ active: mode === 'modify' }" :disabled="reviewing" @click="toggleModify">
            ✎ 修改后采纳（modify）
          </button>
          <button class="btn reject" :class="{ active: mode === 'reject' }" :disabled="reviewing" @click="toggleReject">
            ✕ 拒绝（reject）
          </button>
        </div>

        <!-- modify 编辑区 -->
        <div v-if="mode === 'modify'" style="margin-top:12px">
          <div v-for="f in editFields" :key="f.key" style="margin-bottom:10px">
            <div class="section-label">修改「{{ f.label }}」</div>
            <textarea v-model="f.value" rows="4"></textarea>
          </div>
          <div class="section-label">确认备注（可选）</div>
          <input type="text" v-model="comment" placeholder="例如：已核对，仅作为随访管理任务草稿使用。" />
          <div style="margin-top:10px; display:flex; gap:10px">
            <button class="btn primary" :disabled="reviewing || !modifyValid" @click="doSubmit('modify')">
              提交修改后采纳
            </button>
            <button class="btn ghost" :disabled="reviewing" @click="mode = null">取消</button>
          </div>
          <p v-if="!modifyValid" class="note-text" style="color:var(--danger)">decision=modify 时修改内容不能为空。</p>
        </div>

        <!-- reject 确认区 -->
        <div v-if="mode === 'reject'" style="margin-top:12px">
          <div class="section-label">拒绝原因（可选）</div>
          <input type="text" v-model="comment" placeholder="例如：草稿与患者实际情况不符，本次不予采纳。" />
          <div style="margin-top:10px; display:flex; gap:10px">
            <button class="btn reject active" :disabled="reviewing" @click="doSubmit('reject')">确认拒绝</button>
            <button class="btn ghost" :disabled="reviewing" @click="mode = null">取消</button>
          </div>
          <p class="note-text" style="color:var(--danger)">拒绝后 Runtime 不得执行可信 Memory 写回（memory_write_allowed=false）。</p>
        </div>

        <p v-if="reviewing" class="note-text" style="margin-top:10px"><span class="spinner"></span>正在提交医生确认…</p>
      </template>

      <!-- 已确认：结果回执 -->
      <template v-else>
        <dl class="kv" style="grid-template-columns: 120px 1fr">
          <dt>确认结果</dt>
          <dd><b>{{ review.decision }}</b></dd>
          <dt>医生确认 ID</dt>
          <dd class="mono">{{ review.doctor_confirmation_id }}</dd>
          <dt>确认医生</dt>
          <dd class="mono">{{ review.doctor_id }}</dd>
          <dt>Memory 写入门禁</dt>
          <dd>
            <span v-if="review.memory_write_allowed" class="tag ok">已开启 · 允许可信写回</span>
            <span v-else class="tag danger">已关闭 · 禁止写回</span>
          </dd>
          <dt>后续动作</dt>
          <dd class="mono">{{ review.next_action }}</dd>
          <dt v-if="review.review_comment">医生备注</dt>
          <dd v-if="review.review_comment">{{ review.review_comment }}</dd>
        </dl>
        <div v-if="review.decision === 'modify' && review.modified_content" style="margin-top:10px">
          <div class="section-label">医生修改后内容（以此为准写回）</div>
          <div class="ai-draft" style="border-color:var(--ok-line);background:var(--ok-soft)">
            <span class="draft-mark" style="background:var(--ok)">医生修改版</span>
            <p class="draft-text" v-for="(v, k) in review.modified_content" :key="k">{{ v }}</p>
          </div>
        </div>
        <div class="safety-note">{{ review.safety_note }}</div>
        <div style="margin-top:10px">
          <button class="btn ghost sm" @click="$emit('reset')">重新演示本阶段确认</button>
        </div>
      </template>

      <div v-if="error" class="error-box" style="margin-top:10px">{{ error }}</div>
    </div>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  nodeName: { type: String, default: '' },
  // modify 模式下可编辑的草稿字段：[{ key, label, value }]
  draftFields: { type: Array, default: () => [] },
  review: { type: Object, default: null },
  reviewing: { type: Boolean, default: false },
  error: { type: String, default: '' },
})
const emit = defineEmits(['submit', 'reset'])

const mode = ref(null) // 'modify' | 'reject' | null
const editFields = ref([])
const comment = ref('')

watch(
  () => props.draftFields,
  (fields) => {
    editFields.value = fields.map((f) => ({ ...f }))
  },
  { immediate: true, deep: true },
)

const modifyValid = computed(
  () => editFields.value.length > 0 && editFields.value.every((f) => String(f.value).trim().length > 0),
)

function toggleModify() {
  mode.value = mode.value === 'modify' ? null : 'modify'
}
function toggleReject() {
  mode.value = mode.value === 'reject' ? null : 'reject'
}

function doSubmit(decision) {
  const payload = { decision, reviewComment: comment.value || undefined }
  if (decision === 'modify') {
    const content = {}
    for (const f of editFields.value) content[f.key] = f.value
    payload.modifiedContent = content
  }
  emit('submit', payload)
  mode.value = null
  comment.value = ''
}

const flowDecisionClass = computed(() => {
  if (!props.review) return ''
  return props.review.decision === 'reject' ? 'on-reject' : 'on'
})
const flowDecisionText = computed(() => {
  if (!props.review) return '待医生确认'
  return { approve: '医生已确认', modify: '医生修改后采纳', reject: '医生已拒绝' }[props.review.decision]
})
const flowMemoryClass = computed(() => {
  if (!props.review) return ''
  return props.review.memory_write_allowed ? 'on' : 'on-reject'
})
const flowMemoryText = computed(() => {
  if (!props.review) return 'Memory 写入门禁'
  return props.review.memory_write_allowed ? '可信 Memory 已写回' : 'Memory 写入已阻断'
})
</script>
