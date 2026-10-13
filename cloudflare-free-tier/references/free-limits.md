# Cloudflare Free 免费额度与免费硬上限

> 数字最后核对 2026-10-12。区分 Workers Free 的**硬顶**与产品自身的**免费包含量**，超限行为可能不同。向用户报具体数字时，请先核实 [sources.md](./sources.md) 官方页面。

## 一、免费资源总览

下表只列**文档写了免费用量或免费硬顶**的产品。没有写数字的，不要补。Workers Paid 的月度含用量不在这张表里，在第二节按计量项逐行写明。不要把「这张表没有」读成「$5 不含」。

| 资源 | 免费额度 | 性质 | 备注 |
|---|---|---|---|
| Pages 静态请求 | 免费且无限 | 产品自带 | 不调用 Functions 才算静态。单文件 ≤ 25 MiB |
| Pages 文件 / 构建 | Free 域名计划：每站 20,000 文件；构建 500 次/月、1 个并发、超时 20 分钟 | 域名计划，不是 Workers | Pro：100,000 文件需 `PAGES_WRANGLER_MAJOR_VERSION=4`，构建 5,000 次/月、5 并发。Business：20,000 次/月、20 并发。100 个 Pages 项目/账号；Free 每项目 100 个自定义域。升级 Workers Paid **不会**提高这些数字 |
| Pages Functions | 与 Workers **共享**每天 10 万请求 | $0 硬顶 | 按 Workers 计费。例：Functions 5 万 + Workers 5 万 = 当天用满 |
| Workers Static Assets | 请求免费且无限 | 产品自带 | 单文件 ≤ 25 MiB。Free 每版本 20,000 文件（Wrangler ≥ 4.34.0 才能用到更高的 Paid 文件数） |
| Workers 请求 | 100,000/天 | $0 硬顶 | 超限错误 1027。含 Pages Functions、Workflow 调用 |
| CPU 时间 | 10 ms/次调用 | $0 硬顶 | 等待 `fetch`、KV、D1、R2 等网络 I/O **不计** CPU。Cron 同样 10 ms。全局作用域启动 ≤ 1 秒 |
| 内存 | 128 MB/isolate | 计划限额 | Free 与 Paid 相同。超限同样是错误 1102 |
| Subrequests | 外部 `fetch` 50/次；对 Cloudflare 服务 1,000/次 | $0 硬顶 | 见下方说明。Cache API 的 `put` / `match` / `delete` 与 subrequest 共享（Free 50 次/请求） |
| Workers 数量 / Cron | 100 个 Worker；账号 5 个 Cron | $0 硬顶 | Cron 上限按账号，不是按 Worker |
| 环境变量 | 64/Worker，每个 ≤ 5 KB | 计划限额 | |
| KV | 读 100,000/天；写、删、list **各** 1,000/天；存储 1 GB | $0 硬顶 | 同一 key 写入 1 次/秒。每次 Worker 调用最多 1,000 次 KV 操作。命名空间 1,000 个/账号 |
| D1 | 读 500 万行/天，写 10 万行/天；账号存储 5 GB | $0 硬顶 | 单库 500 MB，最多 10 个库。每次调用 50 条 query。读按**扫描行数**计。Time Travel 7 天 |
| R2 | 存储 10 GB-月/月；A 类 100 万次/月；B 类 1,000 万次/月；出口免费 | 产品自带，然后按 R2 单价 | **不**随 Workers Paid 变多。A 类偏变更，B 类偏读取。单对象最大 5 TiB。`r2.dev` 公共域仅适合测试，有不固定的速率限制 |
| Durable Objects 计算 | 仅 SQLite 后端。请求 10 万/天；时长 13,000 GB-s/天 | $0 硬顶 | 请求含 HTTP、RPC 会话、WebSocket 消息、alarm。时长按活跃墙钟时间，并按分配的 128 MB 计，不论实际占用。详见 [Paid 详细配额](./paid-5-pricing.md) |
| Durable Objects SQLite 存储 | 行读 500 万/天；行写 10 万/天；存储合计 5 GB | $0 硬顶 | 单对象写满 **1 GB** 返回 `SQLITE_FULL`。类数量 100/账号。`setAlarm()` 计 1 行写入；删除也计行写入 |
| Queues | 10,000 次操作/天；保留 24 小时且不可调 | $0 硬顶 | 投递一条通常是写 + 读 + 删共 3 次操作；超过 64 KB 按块翻倍。消息最大 128 KB |
| Workflows | 3,000 step/天；存储 1 GB-月；实例状态默认保留 3 天 | $0 硬顶 | 请求与 CPU 与 Workers 共享（10 万请求/天、10 ms CPU）。存满再写会抛错 |
| Workers AI | 10,000 Neurons/天 | $0 硬顶（Paid 上这 1 万仍免费，超出才计费） | 超出在 Free 上失败，不能按量付。部分前沿模型必须有付费方式 |
| Hyperdrive | 10 万次查询/天；最多 10 个配置 | $0 硬顶 | 查询含 SELECT、写入和 DDL。到源库的连接大约 20 条/配置 |
| Vectorize | 查询维度 3,000 万/月；存储维度 500 万 | $0 硬顶 | 索引 100 个/账号；每索引命名空间 1,000。见下方与 Workers 定价页的冲突说明 |
| Browser Run | 10 分钟/天；Browser Sessions 并发 3 个 | $0 硬顶 | 浏览器时长在 Quick Actions 与 Sessions 之间共享 |
| Workers Logs | 20 万事件/天，保留 3 天 | $0 硬顶 | 官方定价页：2026-12-01 起改用 Observability 定价 |
| Workers Analytics Engine | 写入 10 万点/天；读查询 1 万次/天 | 已公布的 Free 配额 | 定价页写明**目前不收费**，数字是提前公布的。报「已经在计费」前重新抓取 |
| AI Gateway | 核心功能（分析、缓存、速率限制）免费，无限额数字 | 产品自带 | 2026-09-24 之前创建的网关：Legacy Logs 全账号合计 10 万条。当天及之后新建的走 Workers Logs。DLP 扫描免费（无 Zero Trust 时两个预定义配置）。Guardrails 按 Workers AI 计 Neurons |
| AI Search | 每账号每月含：摄入 500 万 token、存储 10 GB-月、语义查询 1,000、全文查询 1,000 | 含用量，2026-11-01 起计费 | Free 另有硬限制：实例 100、每实例 10 万文件、爬取 500 页/天。计费开始前重新抓取定价页 |
| Images | 每月 5,000 次**唯一**变换 | Images Free，超额不扣费 | 超出后新变换返回 `9422`，已缓存的继续可用。Images 存储和分发没有免费额度，要另买 Images Paid |
| Zaraz | 100 万事件/月 | 产品自带 | 不打开 Zaraz Paid 时，超出后禁用到下个账期。Zaraz Paid 是每多 100 万事件 $5，与 Workers $5 无关 |
| Turnstile | Free 计划：最多 20 个 widget；质询次数不限；每 widget 10 个主机名 | 独立 Free 计划 | 分析回看 7 天。不是 Workers 配额 |
| Email Routing（入站） | 入站不限封数 | 产品自带 | 每域 200 条路由规则；每账号 200 个已验证目标地址；入站邮件 ≤ 25 MiB；每 zone 路由/发送域合计 30 个。处理邮件的 Worker 仍占 Workers 的 CPU 和内存，Free 上复杂 handler 会 `EXCEEDED_CPU` |
| Email Sending（出站） | 发给**已验证目标地址**免费，不占月配额，任何计划都可以 | 产品自带 | 发给任意收件人没有 Free 额度，必须 Workers Paid |
| Cache / CDN | 免费网站计划包含缓存与 Tiered Cache，文档**没有**按请求或带宽给出的免费配额 | 域名计划 | 可缓存单文件上限 512 MB（Free/Pro/Business）。上传上限 Free/Pro 100 MB。按主机名/标签/前缀/全部清除：5 次/分钟、桶容量 25；单 URL 清除 800 URL/秒。Cache Reserve **没有**免费额度 |
| Cloudflare Tunnel | 文档没有连接器月费或流量配额 | 产品自带 | `cloudflared` 出站连到自己的域名。Free/Pro/Business 上，公开主机名路由的服务条款要求用指定付费产品提供视频或其它大文件；私网路由传大文件不受这条限制。Quick Tunnel（`trycloudflare.com`）无账号可用，最多 200 个进行中请求，超出 429，不支持 SSE，无可用性保证 |
| Workers VPC | 开放测试期间对所有 Workers 计划免费；每账号 1,000 个 VPC Service | 测试期免费，不是永久配额 | Worker 本身的请求和 CPU 仍按 Workers 计划计。测试结束前重新抓取 |
| Web Analytics | 已代理站点数量不限；未代理站点 10 个 | 产品自带 | Free 计划规则数为 0。文档没有按浏览量计费的配额 |

Subrequest 以 limits 页（2026-10-12）和 [2026-02-11 changelog](https://developers.cloudflare.com/changelog/post/2026-02-11-subrequests-limit/) 为准：免费计划仍是 **50 次外部 subrequest** 和 **1,000 次对 Cloudflare 服务**。D1 另有自己的「每次调用 50 条 query」上限。重定向链上的每一跳都计数。

Vectorize：产品定价页（2026-04-21）和 changelog（2024-09-16）写明 Workers Free 可用，FAQ 写明免费档会一直保留。Workers 总定价页（2026-10-02）仍有一句 “currently only available on the Workers paid plan”，但同一页表格列出了 Free 列。两页冲突时以 Vectorize 产品页为准，并在回答前再抓一次。

**文档写明没有免费额度的，不要编成有：**

- Containers：Workers 定价页 Free 列是 N/A
- Workers Trace Events Logpush：仅 Workers Paid
- Images 的存储与分发、Stream 的存储分钟与分发分钟：没有免费额度。Stream 的入站和转码免费；按 URL 做的视频媒体变换与 Images 共用每月 5,000 次唯一变换。Workers binding 上的媒体变换在 beta 期间不计费
- Cache Reserve：需要付费计划；不用它时，普通 CDN 仍可用
- Durable Objects 的 key-value 存储后端：Workers Free 不能新建；只对已经拥有此类命名空间的 Paid 账号开放
- 发给任意收件人的 Email Sending

## 六、补充额度：Workers Builds、Basin、AI Gateway

| 产品 | Free 或产品独立含量 | 特别提醒 |
|---|---|---|
| Workers Builds | **3,000 构建分钟/月，1 个并发** | 单次构建最长 20 分钟。与 Pages 的“每月 500 次构建”分开计算 |
| AI Gateway | **10 个网关/账号** | Workers Paid 是 20 个；网关数量和调用模型的费用不是一回事 |
| Basin Pipelines（原 Pipelines） | 2026-05 官方公告曾写 **SQL 转换 1 GB/月、Sink 输出 1 GB/月** | 2026-10 定价页只列 Workers Paid；不要未经再次核对就承诺当前 Free 可用。Stream 输入本身不收费 |
| Basin Catalog（原 R2 Data Catalog） | 产品独立月度含量：**100 万次目录操作、10 GB 压缩处理、100 万个被压缩对象** | 启用 compaction 时才计相关量；R2 另收费，不是 $5 额外赠送 |
| Basin SQL（原 R2 SQL） | 产品独立月度包含 **10 GB 压缩数据扫描** | 每条查询最低计 10 MB；启用需要满足 R2 订阅 / 支付方式要求，不等于纯 $0 硬顶 |

有关超额价格和产品订阅前提，见 [Paid 详细配额](./paid-5-pricing.md) 与 [来源](./sources.md)。
