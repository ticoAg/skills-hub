---
name: cloudflare-free-tier
description: 为 Cloudflare 免费计划和 Workers Paid（$5/月起）选择低成本架构，判断 Workers、Pages、KV、D1、R2、Durable Objects、Vectorize、Queues、Workflows、Workers AI 等产品的免费硬顶、每月含量、超额价格和升级收益。用户问“Cloudflare 免费部署”“$5 包含什么”“Pages vs Workers”“错误 1102/1027”或 MVP 选型时使用。数字参考 references/free-limits.md 和 references/paid-5-pricing.md；报数前核实 references/sources.md；示例配置看 references/stack.md。
---

# Cloudflare 免费 / $5 Workers Paid 架构指南

> 额度核对日期：**2026-10-12**。定价易变：**引用具体数字前，必须核验** [官方来源](./references/sources.md)。

## 按需阅读

- **选择架构、判断是否升级**：先看本文。
- **Free 额度、限制、超额失败行为**：[references/free-limits.md](./references/free-limits.md)。
- **Workers Paid $5 月度包含量、超额价格**：[references/paid-5-pricing.md](./references/paid-5-pricing.md)。
- **Wrangler 与 Hono 代码示例**：[references/stack.md](./references/stack.md)。
- **官方价格、限制、更新日期及冲突**：[references/sources.md](./references/sources.md)。所有精确数字对外公布前重新抓取对应官方页面。

## 三种配额不要混

| 分类 | 典型情况 | 用量超额后 |
|---|---|---|
| Workers Free 免费硬顶 | 请求 10 万/天、KV 免费写 1,000/天 | 该类操作失败，不会自动产生账单 |
| Workers Paid **最低 $5/月** | Workers、KV、D1、DO 等账号共享的月度含量 | **额外按量计费，账单不封顶在 $5** |
| 产品独立免费量 | R2、AI、Images、Turnstile 等 | 由各产品决定失败、按量或需另行订阅；**不能和 $5 包内额度重复累加** |

**重要安全提示**：`limits.cpu_ms` 与 `limits.subrequests` 仅限制单次调用，不是账单硬上限。Paid 应使用 Billing 预算/用量提醒并定期检查实际计费；网站 CDN Pro 订阅也不是 Workers Paid。

## 额度速查

| 计量项 | Free | Workers Paid（$5/月起） |
|---|---|---|
| Workers 请求 | 10 万/天 | 1,000 万/月（超额收费） |
| Workers CPU | 10 ms/次 | 3,000 万 CPU-ms/月（超额收费） |
| KV 读 / 写 | 10 万/天 / 1,000/天 | 1,000 万/月 / 100 万/月 |
| D1 行读 / 行写 | 500 万/天 / 10 万/天 | 250 亿/月 / 5,000 万/月 |
| R2 Standard | 10 GB-月、A 类 100 万、B 类 1,000 万操作/月 | 同一份独立免费档，非 $5 加赠 |
| Workers AI | 10,000 Neurons/天 | 仍免费 10,000 Neurons/天，超额收费 |
| Workers Builds | 3,000 分钟/月，1 并发 | 6,000 分钟/月，6 并发 |
| Artifacts | 不可用 | 1 万次仓库操作/月、1 GB-月存储；2026-10-14 预计开始计费 |
| AI Gateway 数量 | 10 个/账号 | 20 个/账号 |

## 三、怎么用

| 需求 | 用什么 |
|---|---|
| 纯静态，需要 Git 构建 | **Pages**。静态请求无限；只有 Functions 进入 Workers 配额。构建次数看域名计划 |
| 纯静态，不想要 Pages 构建配额 | **Workers Static Assets**。默认资源不经 Worker。不要设 `run_worker_first: true` |
| 已有 Pages 项目，补少量 API | **Pages Functions**。按 Workers 计费，与 Worker 共享每天 10 万请求 |
| 新的 SPA + API | Vite 产物作为 Workers Static Assets，`run_worker_first` **只**匹配 `/api/*`，Hono 只处理 API |
| 关系数据 | D1 + Drizzle。先加索引再按筛选列查询 |
| 图片、SVG 包、上传、导出物 | R2。预签名或 multipart **直传**；公开读用自定义域，不要用 `r2.dev` 当生产 |
| 配置、feature flag（读多写极少） | KV。不要当计数器或会话库 |
| 实时协作、计数器、WebSocket、按实体协调 | Durable Objects（SQLite 后端）。Free 够用的前提是请求、时长、行写和单对象 1 GB 都守得住。WebSocket 用 Hibernation API |
| 语义检索原型 | Vectorize 的免费月度维度。嵌入调用另计 Workers AI Neurons |
| 异步 / 批处理 | Queues、Workflows 或 Cron。免费 Cron 全账号只有 5 个，且每次仍只有 10 ms CPU。按文档「一条消息通常 3 次操作」估算，10,000 次操作大约对应 3,300 条完整投递 |
| 转码、渲染、大文件解析 | 不要放进 Worker。放自有机器，用 Tunnel 做入口（公开主机名不要用来送视频或大文件）；或等 Paid 后再用 Containers |
| 入站邮件 | Email Routing，不占封数配额；Worker 处理逻辑仍受 10 ms CPU 限制 |

**推荐 MVP 栈**：Vite + React 的构建产物作静态资源 → Hono Worker 提供 `/api/*` → Drizzle + D1 → R2 存 blob → `wrangler.jsonc` 统一绑定。需要协调状态时再加 SQLite Durable Object，并单独盯 DO 的日请求和 GB-s。

最小 `wrangler.jsonc`、Hono 批量查询和常用命令在 `references/stack.md`。只有要写配置、路由或部署命令时才读取该文件。

## 四、留在免费 / $5 的做法

1. **静态资源不要进 Worker**。让 assets 直接返回。`run_worker_first` 只用路径数组（例如 `["/api/*"]`），不要设为 `true`。
2. **消灭按文件 N+1**。
   - 列目录用一次 `R2.list({ prefix })`，不要循环 `R2.get`
   - 多 id 用一条 `SELECT ... WHERE id IN (...)`，不要每个 id 一次查询
   - 多条 D1 语句用 `db.batch([...])`。每条语句仍占 1 次 query（免费每次调用 50 条）
   - 几百个小 SVG 打成一个 sprite 或一份 JSON manifest，作为一个 R2 对象
   - 浏览器直接读 R2 自定义域，不要让 Worker 逐个代理
3. **大文件直传 R2**。Worker 只签发预签名 URL 或创建 multipart 上传。不要把整包读进 128 MB 内存，也不要在 Worker 里逐文件转存。
4. **CPU 保持轻**。免费只有 10 ms。不要在 Worker 里做大页面 SSR、图片处理、大 JSON 解析或高轮次口令哈希。重初始化不要放在全局作用域（启动上限 1 秒）。
5. **D1 先建索引**。计费按扫描行数。没索引的 `WHERE` 会扫全表，很快吃掉每天 500 万行。分页用游标，不用大 `OFFSET`。
6. **KV 只做读多写少**。免费写、删、list 各 1,000/天。计数器和会话用 D1 或 Durable Objects。
7. **能缓存的公开 GET 就缓存**。`Cache-Control` 或 Cache API 能减少重复的 Worker 与 D1 调用。Cache API 调用计入 subrequest（免费 50 次）。Workers Caching 打开后，缓存命中仍计 Workers 请求。
8. **响应返回后的工作用 `ctx.waitUntil()` 或 Queue**。`waitUntil` 最多再延长约 30 秒，不要拿它做长任务。
9. **日请求超限时选好失败模式**。非安全路由可 fail open（当没有 Worker，请求继续）；鉴权等安全路由用 fail closed（返回 1027）。
10. **Durable Object 用休眠，别空转**。`accept()` 之后整段连接都计时长。用 Hibernation API。`setWebSocketAutoResponse()` 不计额外墙钟。少调用 `setAlarm()`，每次都是一行写入，免费一天只有 10 万行写。单对象别超过 1 GB。
11. **升到 Paid 后立刻写上限**：`limits.cpu_ms`，必要时再加 `limits.subrequests`，避免失控账单。DO 时长单价高，Paid 也要先确认会休眠。

### 常见把额度烧光的写法

- `run_worker_first: true`，每个静态文件都扣一次请求和 CPU
- 循环里 `await fetch()`：免费 50 次外部 subrequest 就失败
- 循环里 `await env.DB.prepare(...).run()`：免费每次调用 50 条 D1 query
- 循环里 `await env.BUCKET.get(key)`：对 Cloudflare 服务的 1,000 次上限也会被逐文件打满
- 一个请求里把上百个文件写入 R2 或 D1
- 用 KV 做计数器或会话
- 无索引 `SELECT *`，再加很大的 `OFFSET`
- 每分钟 Cron 打外部 API，一次拉几十个 URL（账号只有 5 个 Cron，每次还只有 10 ms CPU 和 50 次外部 fetch）
- WebSocket 不用 Hibernation：一个全天不休眠的对象大约吃掉 11,059 GB-s，第二个就会超过每天 13,000 GB-s
- 把报警设得很密：`setAlarm()` 吃 DO 行写，免费一天 10 万行

## 五、什么时候升级到 $5

满足任一条再考虑：日请求稳定超过约 5 万（靠近 10 万硬顶）、正常请求 CPU 超过 10 ms、一次调用必须超过 50 条 D1 query 或 50 次外部 fetch、Cron 需要多于 5 个、单个 D1 库将超过 500 MB、Workers AI 需要超过每天 1 万 Neurons、Durable Object 请求靠近每天 10 万或时长靠近 13,000 GB-s、DO 行写靠近每天 10 万或单对象靠近 1 GB、或需要 Logpush / Containers / 向任意地址发信。升级后多数小项目仍是固定 $5；超额才按量加价。DO 时长是最容易让账单离开 $5 的一项。

升级**不会**提高：Pages 构建次数和每站文件数（那是域名计划）、R2 免费额度、每天 1 万 Neurons 的免费额度（只是超出后改为计费）、Turnstile / Zaraz / Images 各自的免费额度。

Pages 构建不够（500 次/月或 1 个并发）要升的是域名计划，不是 Workers Paid。

## 案例：fx-lab SVG 素材包

批量上传大型 SVG 素材包时，在 Worker 里逐文件拉取和转存，会打满 subrequest。把整包写进一张大表（sheet）还会撞上单表 / 单元格或单行大小。平台侧同类硬限制是：D1 单行最大 2 MB，单条 SQL 最大 100 KB。

修复：

- 浏览器直传 R2（预签名或 multipart），Worker 只签发，不转发文件体
- 大量小 SVG 合并成少量包，或一份 manifest，对应少数几个 R2 对象
- 元数据用 `db.batch` 分块写入；一批仍放不下时改走 Queue

## 数字来源

详见 [官方来源索引](./references/sources.md)。
