# V2 架构设计

## 目标

把当前项目从学习型 CLI Agent，升级成具备以下能力的工程化 Agent Runtime：

- 全链路可观测
- 分层记忆
- 反思评估与幻觉检测
- 异步执行
- ETL 文档入库
- Docker Compose 部署

当前阶段建议优先采用：

- Redis 做短期记忆
- Milvus 做长期记忆
- PostgreSQL 做会话、轨迹、评估结果持久化
- FastAPI 做 API / WebSocket Gateway
- Worker 做异步任务执行

---

## 总体架构

```text
Client(Web/Mobile)
        |
        v
   API Gateway
        |
        v
  Session / Run API
        |
        v
     Harness Runtime
        |
        +-------------------> Tool Service
        |
        +-------------------> Memory Service
        |                       |- Redis (short-term)
        |                       |- Summary Store
        |                       `- Milvus (long-term)
        |
        +-------------------> Reflection Service
        |
        +-------------------> Trace Service
        |
        `-------------------> Worker / ETL Pipeline
```

---

## 核心设计原则

### 1. Agent 不直接拥有所有职责

`Agent` 只负责决策：

- 该不该调用工具
- 当前该回答什么
- 当前 step 是否完成

不要让 `Agent` 直接负责：

- 会话持久化
- trace 写入
- memory 路由
- 队列调度
- 反思评分

这些职责应下沉到 `Harness Runtime` 和外围子系统。

### 2. Trace ID 全链路贯通

每一次用户请求都生成一个 `trace_id`，并贯通：

- API 请求
- session
- run
- LLM 调用
- tool 调用
- memory read/write
- reflection
- worker 作业

建议层级：

- `trace_id`: 一次完整请求链路
- `run_id`: 一次 agent 运行
- `step_id`: 单个 reasoning / tool / reflection step
- `tool_call_id`: 单次工具调用

### 3. 记忆必须分层，不要只做一个“大记忆池”

记忆分层建议：

- `Short-term Memory`
  - Redis
  - 当前会话上下文
  - 最近消息窗口
  - TTL 自动过期

- `Summary Memory`
  - PostgreSQL 或 Redis + 持久化表
  - 历史摘要
  - 跨轮压缩后的上下文

- `Long-term Memory`
  - Milvus
  - 语义召回
  - 用户偏好、经验、知识、历史任务

### 4. Reflection 是单独子系统

不要把“反思”只当成 prompt 里的一段文本。  
要把它做成明确的评估组件：

- 输出质量评分
- 幻觉风险评分
- 工具使用合理性
- 证据覆盖率
- 是否建议重试

---

## 子系统设计

## 1. Gateway

职责：

- 接入浏览器 / 手机 / 未来 App
- 提供 HTTP / WebSocket
- 创建 session
- 下发 run 请求
- 回推流式结果

建议目录：

```text
gateway/
├─ app.py
├─ routes/
│  ├─ sessions.py
│  ├─ chat.py
│  └─ health.py
└─ ws.py
```

建议接口：

- `POST /api/sessions`
- `GET /api/sessions/{session_id}`
- `POST /api/runs`
- `GET /api/runs/{run_id}`
- `WS /api/ws/{session_id}`

---

## 2. Harness Runtime

职责：

- 加载 session state
- 组织消息
- 调用 LLM
- 分发工具
- 写 trace
- 读写 memory
- 调用 reflection
- 保存 checkpoint

建议目录：

```text
runtime/
├─ harnesses/
│  ├─ base.py
│  ├─ react_harness.py
│  └─ per_harness.py
├─ session.py
├─ state.py
├─ checkpoint.py
├─ tracing.py
└─ executor.py
```

建议状态模型：

- `SessionState`
- `RunState`
- `ToolExecutionRecord`
- `MemoryReadRecord`
- `MemoryWriteRecord`
- `ReflectionRecord`
- `FinishReason`

---

## 3. Memory Service

### 3.1 短期记忆

建议使用 Redis。

用途：

- 存当前 session 最近消息
- 存工具结果缓存
- 存最近摘要
- 做快速读取

建议 Key 设计：

```text
agent:session:{session_id}:messages
agent:session:{session_id}:summary
agent:session:{session_id}:tool_cache
agent:session:{session_id}:state
```

推荐策略：

- 保留最近 N 轮原始消息
- 超过阈值后做摘要压缩
- 原始消息设置 TTL
- 摘要可比原始消息保留更久

### 3.2 摘要压缩层

目标：

- 降低 token 消耗
- 保留中长期上下文
- 为跨会话召回提供较轻量文本

建议做法：

- 当消息超过 `summary_trigger_tokens` 时，触发摘要
- 摘要写回 Redis 和 PostgreSQL
- 将旧消息从 prompt 注入中移除，只保留摘要 + 最近窗口

摘要分三级：

- `turn_summary`
- `session_summary`
- `topic_summary`

### 3.3 长期记忆

建议使用 Milvus。

用途：

- 用户偏好
- 经验总结
- 高价值任务结果
- 可复用知识片段
- 跨会话语义召回

建议写入条件：

- importance 高于阈值
- reflection 判定为高价值
- 用户显式确认需要记住

建议检索策略：

- 先按用户 / 租户隔离
- 再按 memory_type 过滤
- 最后做向量相似召回

---

## 4. Reflection Service

建议新增 `ReflectionAgent`，与主 Agent 解耦。

职责：

- 质量评分
- 幻觉检测
- 证据完整性检查
- 工具调用合理性检查
- 判断是否需要重试

建议输出结构：

```json
{
  "quality_score": 0.0,
  "hallucination_score": 0.0,
  "grounding_score": 0.0,
  "tool_use_score": 0.0,
  "should_retry": false,
  "problems": [],
  "feedback": ""
}
```

建议评分维度：

- `quality_score`
  - 答案完整性
  - 是否解决用户问题

- `hallucination_score`
  - 是否出现无依据断言
  - 是否与 tool / memory / reference 冲突

- `grounding_score`
  - 是否引用了实际观察结果
  - 是否建立在工具结果之上

- `tool_use_score`
  - 是否过度调用工具
  - 是否漏调用关键工具

---

## 5. Trace Service

### 目标

让你能回答下面的问题：

- 这次回答用了哪些工具？
- 为什么写入了长期记忆？
- 哪个步骤 token 消耗最高？
- 哪次 hallucination 分数最高？
- 哪个 session 总是失败？

### 事件模型

最少事件：

- `run_started`
- `llm_started`
- `llm_finished`
- `tool_started`
- `tool_finished`
- `memory_read`
- `memory_write`
- `reflection_finished`
- `checkpoint_saved`
- `run_finished`
- `run_failed`

### 存储建议

短期：

- 先写 PostgreSQL

后续需要更强观测时：

- PostgreSQL + ClickHouse
- 或 OpenTelemetry + Tempo / Jaeger

---

## 6. Worker / ETL

### Worker

职责：

- 长任务异步执行
- ETL 解析任务
- 文档切分任务
- 向量入库任务

建议目录：

```text
worker/
├─ queue.py
├─ jobs.py
├─ memory_jobs.py
└─ etl_jobs.py
```

### ETL 支持

第一阶段建议支持：

- PDF
- TXT
- Markdown

后续再扩：

- DOCX
- HTML
- Notion 导出

### 三种智能分块策略

建议：

1. `fixed_chunk`
   - 按长度切分
   - 简单稳定

2. `semantic_chunk`
   - 按语义边界切分
   - 适合知识问答

3. `hierarchical_chunk`
   - 先按章节，再按段落
   - 适合长文档和企业知识库

---

## 部署架构

## Docker Compose 组件建议

第一阶段 Compose：

- `gateway`
- `worker`
- `redis`
- `milvus`
- `etcd`
- `minio`

第二阶段再加：

- `postgres`
- `otel-collector`
- `jaeger`

说明：

- Milvus Standalone 通常依赖 `etcd + minio`
- 如果只是本地学习和单机验证，建议优先用 Milvus Standalone

---

## 推荐配置说明

建议配置优先级：

1. 环境变量
2. `configs/config.yaml`
3. 代码默认值

建议新增配置项说明如下。

### gateway

- `host`: Gateway 监听地址
- `port`: Gateway 监听端口
- `cors_origins`: 前端来源

### runtime

- `max_concurrent_runs`: 最大并发运行数
- `default_harness`: 默认 harness
- `checkpoint_enabled`: 是否启用 checkpoint

### tracing

- `enabled`: 是否启用 trace
- `exporter`: `postgres | otlp | stdout`
- `sample_rate`: 采样率

### reflection

- `enabled`: 是否启用反思
- `quality_threshold`: 质量阈值
- `hallucination_threshold`: 幻觉阈值
- `retry_on_bad_score`: 是否低分重试

### redis

- `host`
- `port`
- `db`
- `password`
- `ttl_seconds`

### milvus

- `host`
- `port`
- `collection_name`
- `top_k`
- `similarity_threshold`

### memory

- `enabled`
- `short_term_window_size`
- `summary_trigger_tokens`
- `summary_max_tokens`
- `long_term_threshold`
- `cross_session_recall`

### etl

- `enabled`
- `chunk_strategy`
- `chunk_size`
- `chunk_overlap`
- `semantic_chunk_min_size`

---

## 实施顺序

### Phase 1

- BaseHarness
- ReActHarness
- Trace ID
- 基础 tracing 事件

### Phase 2

- Redis 短期记忆
- 摘要压缩
- ReflectionAgent

### Phase 3

- Milvus 长期记忆
- 跨会话召回
- ETL 入库

### Phase 4

- FastAPI Gateway
- WebSocket
- Worker 队列
- Docker Compose

---

## 结论

如果你现在电脑上已经启动了 Docker，那么下一步最合适的技术路线就是：

- Redis：必须上，先做短期记忆和 session state
- Milvus：可以上，但建议放在第二阶段，先把 trace 和短期记忆跑稳
- Docker Compose：建议尽快做，但先从基础服务编排开始，不要一开始就塞太多组件

最推荐的落地顺序是：

1. `Trace + Harness`
2. `Redis Short-term Memory`
3. `ReflectionAgent`
4. `Milvus Long-term Memory`
5. `Gateway + Worker + Compose`
