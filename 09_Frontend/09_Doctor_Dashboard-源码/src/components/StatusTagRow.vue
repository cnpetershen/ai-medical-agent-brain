<template>
  <!-- 跨阶段共通状态标签：AI辅助 / 医生确认 / Memory 写入 / 来源可追溯 -->
  <div class="tag-row">
    <span class="tag ai"><span class="dot"></span>AI辅助 · 草稿非结论</span>
    <span v-if="confirmStatus === 'pending'" class="tag warn"><span class="dot"></span>待医生确认</span>
    <span v-else-if="confirmStatus === 'approve'" class="tag ok"><span class="dot"></span>已医生确认</span>
    <span v-else-if="confirmStatus === 'modify'" class="tag ok"><span class="dot"></span>医生修改后确认</span>
    <span v-else-if="confirmStatus === 'reject'" class="tag danger"><span class="dot"></span>医生已拒绝</span>
    <span v-else class="tag neutral"><span class="dot"></span>确认状态未知</span>

    <span v-if="memoryStatus === 'written'" class="tag ok"><span class="dot"></span>已写入Memory</span>
    <span v-else-if="memoryStatus === 'blocked'" class="tag danger"><span class="dot"></span>Memory写入已关闭</span>
    <span v-else class="tag warn"><span class="dot"></span>未写入Memory</span>

    <span class="tag trace"><span class="dot"></span>来源可追溯</span>
  </div>
</template>

<script setup>
defineProps({
  // pending | approve | modify | reject | null
  confirmStatus: { type: String, default: 'pending' },
  // written | pending | blocked
  memoryStatus: { type: String, default: 'pending' },
})
</script>
