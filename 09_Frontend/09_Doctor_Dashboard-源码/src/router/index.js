import { createRouter, createWebHashHistory } from 'vue-router'
import PreVisitView from '../views/PreVisitView.vue'
import DuringVisitView from '../views/DuringVisitView.vue'
import PostVisitView from '../views/PostVisitView.vue'

// 三阶段工作台：对应三大 Workflow 的连续照护闭环
const routes = [
  { path: '/', redirect: '/pre-visit' },
  {
    path: '/pre-visit',
    name: 'pre-visit',
    component: PreVisitView,
    meta: { stage: 'pre_visit', title: '诊前工作台' },
  },
  {
    path: '/during-visit',
    name: 'during-visit',
    component: DuringVisitView,
    meta: { stage: 'during_visit', title: '诊中工作台' },
  },
  {
    path: '/post-visit',
    name: 'post-visit',
    component: PostVisitView,
    meta: { stage: 'post_visit', title: '诊后工作台' },
  },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
})
