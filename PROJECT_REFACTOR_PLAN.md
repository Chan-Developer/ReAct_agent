# 项目改造建议

## 目标

把当前项目从“学习型 CLI Agent 项目”逐步改造成：

- 可持续迭代的 Agent Runtime
- 可服务化部署的多端访问系统
- 具备通用 Harness 能力的执行平台

当前不建议直接追求“大而全”。更合适的目标是：

1. 先把运行时做稳
2. 再把服务层做出来
3. 最后再考虑高并发和平台化

---

## 当前项目的核心优点

- 目录结构已经有分层：`agents / tools / workflows / memory / llm`
- `ReactAgent` 和 `PlanExecuteReflectAgent` 已有核心雏形
- `workflow` 已经能承载固定业务流程
- 代码体量还不大，适合重构和学习

---

## 当前项目的主要问题

### 1. 还是 CLI 项目，不是服务型项目

当前入口在 [main.py](/E:/pyWeb/ReAct_agent/main.py:147)，适合本地运行，不适合：

- 多用户
- 多端接入
- 会话持久化
- 任务排队
- 异步执行

### 2. Tool Calling 还不够稳

当前工具调用很大程度依赖文本解析：

- [agents/react_agent.py](/E:/pyWeb/ReAct_agent/agents/react_agent.py:183)
- [core/parser.py](/E:/pyWeb/ReAct_agent/core/parser.py:21)

主要问题：

- 依赖模型按格式输出 `Action: {...}`
- 参数校验能力弱
- 可恢复性差
- 不利于以后接不同模型或不同前端

### 3. Agent 状态没有显式建模

现在 conversation 在内存里维护，缺少统一的：

- `SessionState`
- `RunState`
- `Checkpoint`
- `FinishReason`

这会导致后续功能很难做稳：

- resume
- replay
- tracing
- 审计
- 人工接管

### 4. PER 结构化能力不足

`PlanExecuteReflectAgent` 已经有价值，但 plan 和 reflect 仍然依赖模型生成 JSON，再进行兜底解析：

- [agents/plan_execute_reflect_agent.py](/E:/pyWeb/ReAct_agent/agents/plan_execute_reflect_agent.py:113)
- [agents/plan_execute_reflect_agent.py](/E:/pyWeb/ReAct_agent/agents/plan_execute_reflect_agent.py:178)
- [agents/plan_execute_reflect_agent.py](/E:/pyWeb/ReAct_agent/agents/plan_execute_reflect_agent.py:244)

问题：

- 长任务容易漂
- 错误处理不够系统
- 不利于通用化 harness

### 5. multi-agent 还没有真正落地

当前 `multi` 还是占位：

- [main.py](/E:/pyWeb/ReAct_agent/main.py:226)

因此目前更适合定位为：

- 单 agent runtime
- 固定 workflow 系统

而不是成熟的 multi-agent 平台。

### 6. 缺少服务化和平台化能力

当前缺少：

- API Gateway
- WebSocket 流式输出
- Session Store
- Worker 执行层
- Trace 系统
- 权限与工具隔离

---

## 总体改造方向

建议把项目逐步演进为四层：

1. `gateway`
2. `runtime`
3. `worker`
4. `web`

对应职责：

### gateway

负责：

- HTTP / WebSocket 接入
- 用户鉴权
- 会话管理
- 请求转发

### runtime

负责：

- Harness 执行
- Agent 决策
- Tool Dispatch
- Trace
- Checkpoint

### worker

负责：

- 长任务执行
- 异步队列消费
- 沙箱工具执行

### web

负责：

- 桌面和手机响应式界面
- 会话展示
- 流式输出展示
- 历史记录查看

---

## 你最应该优先做的改动

按优先级排序：

### 第一优先级：重构 Tool Calling

目标：

- 不再依赖纯文本 `Action: {...}`
- 用统一 schema 描述工具
- 让模型返回结构化 tool calls

建议改动：

- 保留 `ToolRegistry`
- 扩展 `BaseTool.as_function_spec()`
- 在 LLM 层支持原生工具调用参数
- 在 runtime 层统一处理 tool dispatch 和错误包装

你会得到：

- 更稳的工具调用
- 更清晰的调试链路
- 更容易接后续 harness

### 第二优先级：建立统一状态模型

建议新增：

- `runtime/session.py`
- `runtime/state.py`

至少定义：

- `SessionState`
- `RunState`
- `ToolExecutionRecord`
- `Checkpoint`
- `FinishReason`

最少要记录：

- 当前消息
- 当前步骤
- 工具调用历史
- 最近一次模型输出
- 最终完成原因

### 第三优先级：把 ReactAgent 改造成 Harness

不是删除 `ReactAgent`，而是改变它的角色。

建议目标：

- `ReactAgent` 只保留“决策逻辑”
- `ReActHarness` 负责完整运行时执行

建议新增：

- `runtime/harnesses/base.py`
- `runtime/harnesses/react_harness.py`
- `runtime/harnesses/per_harness.py`

其中：

- `BaseHarness` 定义标准执行接口
- `ReActHarness` 封装当前单 agent 回合执行
- `PERHarness` 封装 plan-execute-reflect 控制流程

### 第四优先级：加入 Trace 和 Checkpoint

建议新增：

- `runtime/tracing.py`
- `runtime/checkpoint.py`

最少事件：

- `run_started`
- `llm_started`
- `llm_finished`
- `tool_started`
- `tool_finished`
- `checkpoint_saved`
- `run_finished`
- `run_failed`

这一步是后面做：

- 可视化调试
- 商业审计
- 故障恢复

的基础。

### 第五优先级：从 CLI 升级成服务

建议新增：

- `gateway/app.py`
- `gateway/routes/chat.py`
- `gateway/routes/sessions.py`
- `gateway/ws.py`

建议技术路线：

- FastAPI
- WebSocket
- SQLite 起步
- 后续再切 Redis / Postgres

第一版只做：

- 新建会话
- 发送消息
- 流式返回
- 获取历史记录

### 第六优先级：做响应式网页

目标不是先做 App，而是：

- 一个网页同时适配电脑和手机

建议：

- 单页聊天界面
- 左侧历史会话或抽屉
- 中间对话流
- 手机端自适应布局

原因：

- 开发成本最低
- 多端验证最快
- 后面可封装成 PWA 或桌面壳

---

## 推荐的目录重构方案

建议逐步往这个结构靠：

```text
ReAct_agent/
├─ agents/
├─ tools/
├─ workflows/
├─ llm/
├─ memory/
├─ runtime/
│  ├─ harnesses/
│  │  ├─ base.py
│  │  ├─ react_harness.py
│  │  └─ per_harness.py
│  ├─ session.py
│  ├─ state.py
│  ├─ tracing.py
│  ├─ checkpoint.py
│  └─ executor.py
├─ gateway/
│  ├─ app.py
│  ├─ ws.py
│  └─ routes/
├─ worker/
│  ├─ queue.py
│  ├─ jobs.py
│  └─ sandbox.py
├─ web/
│  ├─ index.html
│  ├─ src/
│  └─ public/
└─ tests/
```

不需要一次改完，可以逐步迁移。

---

## 商业化落地建议

更适合的商业定位不是：

- “万能 AI Agent”

更建议定位为：

- “可私有化部署的 Agent Runtime / Harness 平台”

可以强调的能力：

- 多端访问
- 工具接入
- 会话持久化
- 任务执行追踪
- 可恢复执行
- 可插拔 Harness

更适合落地的场景：

- 企业知识助手
- 文档生成助手
- 流程助手
- 代码助手
- 内部自动化助手

---

## 千万级并发的正确理解

当前项目不需要现在就以“千万级并发”作为第一目标。

要先区分几件事：

### 1. 高并发接入

这个靠：

- CDN
- API Gateway
- WebSocket Gateway
- 无状态接入层

### 2. 高并发会话管理

这个靠：

- Redis
- Postgres
- 会话分片
- 缓存与持久化分离

### 3. 高并发任务执行

这个靠：

- 队列
- worker 池
- 限流
- 优先级调度
- 超时和熔断

### 4. LLM 成本和吞吐控制

这个靠：

- 模型路由
- 配额
- 降级策略
- 结果缓存

结论：

真正能扛量的前提不是“单个 agent 很强”，而是：

- 网关无状态
- 执行异步化
- 状态独立存储
- 工具服务隔离

---

## Harness 设计建议

建议把 Harness 定义为：

“一次 Agent 运行的标准执行容器”

它不负责定义人格，不负责定义业务流程，而负责：

- 组织输入
- 驱动模型
- 调度工具
- 保存状态
- 记录轨迹
- 输出结果

### 一个好用的 Harness 至少要支持

1. 统一输入输出
2. 工具调用封装
3. 状态持久化
4. checkpoint / resume
5. tracing
6. 错误恢复
7. finish reason

### 建议接口

```python
class BaseHarness:
    def prepare(self, session_state, run_context): ...
    def step(self, session_state, run_context): ...
    def handle_tool_calls(self, tool_calls, session_state, run_context): ...
    def checkpoint(self, session_state): ...
    def finish(self, session_state): ...
```

### 建议运行时上下文

```python
class RunContext:
    session_id: str
    user_id: str
    tenant_id: str | None
    model: str
    tools: list
    timeout_seconds: int
    max_steps: int
    metadata: dict
```

---

## 推荐实施顺序

你可以按下面顺序学和改：

### 阶段 1：稳住核心运行时

1. 重构 tool calling
2. 加统一状态模型
3. 抽出 `BaseHarness`
4. 让 `ReactAgent` 跑在 `ReActHarness` 上

### 阶段 2：补平台基础能力

1. 加 tracing
2. 加 checkpoint
3. 加 session store
4. 加更稳的错误处理

### 阶段 3：服务化

1. FastAPI 接口
2. WebSocket 流式输出
3. 会话 API
4. 基础鉴权

### 阶段 4：多端访问

1. 响应式网页
2. 手机适配
3. PWA 或桌面封装

### 阶段 5：异步执行与扩展

1. 队列
2. worker
3. 沙箱
4. 工具服务隔离

### 阶段 6：真正的平台化

1. 多租户
2. 审计
3. 配额
4. 可观测性
5. 模型路由

---

## 不建议现在做的事

- 不要先做复杂 multi-agent 群聊
- 不要先做原生手机 App
- 不要先接太多外部工具
- 不要先引入太重的基础设施
- 不要一开始就为“千万级并发”做过度设计

先把：

- tool calling
- harness
- state
- tracing
- service 化

这五件事做好，项目就会明显上一个台阶。

---

## 最后建议

如果你准备边学边改，最佳起点不是前端，也不是并发，而是：

1. `Tool Calling`
2. `BaseHarness`
3. `SessionState / RunState`

这三件事一旦成型，后面的网页、手机、多端接入、worker、商业化都会自然很多。
