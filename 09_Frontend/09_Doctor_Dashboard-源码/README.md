# 09_Doctor_Dashboard —— 医生工作台前端原型

「医生AI Copilot Agentic Workflow」项目的展示层（Presentation Layer）实现，对应 `06_Demo_Interface/Doctor Dashboard Spec.md` 的规格定义。

技术栈：**Vue 3 + Vite + Vue Router**（无后端依赖即可运行，内置与 API 契约一致的 Mock 数据层）。

## 设计定位

Doctor Dashboard 不是聊天 UI，而是**三阶段医生工作台**，把 Runtime 的节点执行结果、知识依据、医生确认状态和 Memory 回流组织成连续照护视图。三条叙事主线贯穿所有页面：

- **AI 辅助**：所有 AI 输出均标记「AI整理结果 / 辅助草稿」，附 `safety_note`，不显示为诊断/处方结论；
- **医生确认**：每页设医生确认区（approve / modify / reject 三态），确认状态与 Memory 写入门禁流转全程可见；
- **连续照护闭环**：诊前展示「上一次诊后回流线索」，诊后置顶展示「下一次诊前上下文」回流路径。

页面与 Workflow 的对应关系：

| 页面 | 路由 | 对应 Workflow | 主要 API |
| --- | --- | --- | --- |
| 诊前工作台 | `/#/pre-visit` | 诊前信息采集 | `POST /workflow/pre_visit`、`GET /patient/{id}/profile`、`GET /patient/{id}/memory` |
| 诊中工作台 | `/#/during-visit` | 诊中辅助决策 | `POST /workflow/during_visit` |
| 诊后工作台 | `/#/post-visit` | 诊后医嘱执行 | `POST /workflow/post_visit` |
| 医生确认（每页） | — | HUMAN Node | `POST /human-review/{workflow_id}` |

每页均包含 Doctor Dashboard Spec 要求的四类区域：**患者上下文区 / AI 输出区 / 医生确认区 / 追溯与状态区**（页面底部可折叠的 Workflow State + 审计日志）。

## 启动方式

```bash
cd 09_Doctor_Dashboard
npm install
npm run dev        # 默认 Mock 模式，打开 http://localhost:5173
npm run build      # 生产构建（输出 dist/）
npm run preview    # 预览生产构建
```

### 两种 API 模式

复制 `.env.example` 为 `.env` 并修改：

```bash
# Mock 模式（默认）：内置数据层，开箱即用，无需任何后端
VITE_API_MODE=mock

# Real 模式：连接 08_API_Service（Runtime API Service）
VITE_API_MODE=real
VITE_API_TARGET=http://127.0.0.1:8000   # Runtime API Service 地址
```

Real 模式下需先启动后端（在仓库根目录）：

```bash
cd 08_API_Service
pip install fastapi uvicorn pyyaml
uvicorn main:app --host 127.0.0.1 --port 8000
```

前端 dev server 会把 `/api/*` 代理到 `VITE_API_TARGET`（见 `vite.config.js`），浏览器侧无跨域问题。**Real 模式下若后端不可达，前端自动降级到 Mock 数据层**，顶栏会显示「真实后端不可达 · 已降级 Mock」。

## 目录结构

```
09_Doctor_Dashboard/
├── index.html
├── package.json
├── vite.config.js              # dev 代理：/api → VITE_API_TARGET
├── .env.example
├── src/
│   ├── main.js
│   ├── App.vue                 # 顶栏（患者卡/API模式徽标）+ 安全横幅 + 三阶段导航
│   ├── router/index.js         # 三个页面路由
│   ├── store/sessionStore.js   # 跨页会话状态：患者档案/Memory/三阶段 Workflow State/确认记录
│   ├── api/
│   │   ├── client.js           # 统一 API Client（real/mock 切换 + 自动降级），与 07_API_Spec 对齐
│   │   └── mock/
│   │       ├── engine.js       # 有状态 Mock 引擎：复刻 08_API_Service 行为（含 review 写回、reject→rejected）
│   │       └── fixtures/       # 真实 Runtime MVP 输出的裁剪副本（契约字段一致，虚构患者数据）
│   ├── components/
│   │   ├── PatientCard.vue         # 患者摘要卡（含「上一次诊后回流线索」）
│   │   ├── BpTrendChart.vue        # 近期家庭血压趋势（纯 SVG，无图表库依赖）
│   │   ├── RiskProfileCard.vue     # 风险画像（五维风险 + 医生关注动作）
│   │   ├── HumanReviewPanel.vue    # 医生确认面板（approve/modify/reject + 草稿编辑 + 状态流转）
│   │   ├── MemoryDiff.vue          # Memory before/after 差异对照（仅高亮变化字段）
│   │   ├── CareLoopBar.vue         # 连续照护闭环链路指示
│   │   ├── StatusTagRow.vue        # 共通状态标签（AI辅助/确认/Memory/可追溯）
│   │   └── AuditTrail.vue          # 追溯与状态区（Workflow State + 审计日志，可折叠）
│   ├── views/
│   │   ├── PreVisitView.vue        # 诊前工作台
│   │   ├── DuringVisitView.vue     # 诊中工作台
│   │   └── PostVisitView.vue       # 诊后工作台
│   └── styles/main.css         # 设计系统（医疗工作台风格，无 UI 框架依赖）
└── README.md
```

## 与后端 API 的对接说明

前端只通过 `src/api/client.js` 访问后端，接口与 `07_API_Spec/Runtime API Spec.md` 及 `08_API_Service` 的实现一一对应：

| client.js 方法 | HTTP | 说明 |
| --- | --- | --- |
| `runWorkflow(name, payload)` | `POST /workflow/{pre_visit\|during_visit\|post_visit}` | 启动某阶段 Workflow；`during_visit`/`post_visit` 会自动携带上一阶段 `workflow_id` 串起闭环链路 |
| `getWorkflowState(wid)` | `GET /workflow/{wid}/state` | 查询 Workflow 运行状态与节点输出 |
| `getWorkflowAudit(wid)` | `GET /workflow/{wid}/audit` | 查询审计日志（Tool 调用 / Memory 读写 / 确认事件） |
| `getPatientProfile(pid)` | `GET /patient/{pid}/profile` | 患者档案 + 近期血压 + 风险画像 |
| `getPatientMemory(pid)` | `GET /patient/{pid}/memory` | 可信 Patient Memory（仅医生确认后内容） |
| `submitHumanReview(wid, payload)` | `POST /human-review/{wid}` | 提交医生确认（approve / modify / reject），modify 必带 `modified_content` |

切换真实后端只需设置 `VITE_API_MODE=real` 与 `VITE_API_TARGET`，**业务代码零改动**。

### Human Review 交互语义（与后端一致）

- **approve**：医生采纳当前草稿，`memory_write_allowed=true`，Runtime 继续执行可信写回节点；
- **modify**：医生在面板内直接编辑草稿内容（诊前=摘要 `draft_text`，诊中=管理计划 `confirmed_order`，诊后=回流摘要 `next_pre_visit_context`）后提交，页面与后续写回**只使用医生修改后的内容**；
- **reject**：`memory_write_allowed=false`，Workflow 状态置为 `rejected`，确认 ID 带 `-REJECT` 后缀，页面标记「Memory 写入已阻断」。

注意：当前 `08_API_Service` 的 `POST /workflow/*` 会以模拟决策预跑全部节点（state 中带 `Runtime 模拟确认` 标记），页面上的医生确认面板是医生的**真实确认入口**，提交后以其结果为准刷新确认状态。

## 安全边界（UI 层强制呈现）

- 顶部常驻安全横幅：AI 不自动诊断 / 不自动开方 / 不自动改药 / 不自动修改治疗方案；
- AI 输出卡一律带「AI 草稿」标与 `safety_note`；医嘱草稿恒为「待医生确认」，确认前不进入诊后任务；
- RAG 依据每条带「来源可追溯」标；检索失败须显示「未检索到充分来源」，不得编造；
- 全站为虚构模拟患者（SIM-HTN-001 王某）数据，顶栏与页脚均有标识。

## 已验证

- `npm run build` 通过（Vite 5，gzip 后 JS 约 72 KB）；
- Playwright 端到端检查 27 项全部通过：三页渲染、approve / modify / reject 三态交互、确认 ID 展示、Memory 门禁流转、异常事件高亮、闭环导航；
- Real 模式已与 `08_API_Service` 实际联调通过（dev 代理 → `uvicorn main:app --port 8010`）。
