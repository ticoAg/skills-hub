# Cloudflare Workers Paid：$5/月包含量与超额计费

> 数字最后核对 2026-10-12。**$5 是最低订阅费，不是账单总上限**；产品独立免费量不是 $5 再赠一份。报数前核查 [sources.md](./sources.md)。

## 二、Free vs Workers Paid（$5/月）：逐项含用量

Workers 定价页（2026-10-02）开篇写明：最低 **$5/月**包含的是 **Workers、Pages Functions、Workers KV、Hyperdrive、Durable Objects**。同一页还用 “included” 给 D1、Queues、Workflows、Vectorize、Containers、Workers Logs、Logpush 写了 Paid 月度含用量。Containers 明确写这些含用量是 $5 的一部分。

下面每行一个计量项。「$5 含用量」列只写文档给出的 included 数字；没有月度赠送时写「无」，不要脑补成无限或和 Free 相同。计划上限（个数、subrequest、单次 CPU）放在最后一列，它们不计费，也不是能“用完再买”的含用量。

月度含用量按订阅账期重置，不是自然月（D1 定价页）。Free 日限 UTC 0 点重置。调用 Durable Object 的那次 Worker 请求另计；DO 定价示例不含它。Pages Functions 的请求和 CPU **共用** Workers 那一笔，不是再送一份。Workflows 的请求和 CPU 也是同一笔。

DO 时长：对象活跃且不能休眠时按墙钟计，多个并发请求共享；按分配的 128 MB 计，同一 isolate 里的多个对象仍各自按 128 MB。13,000 GB-s ÷ 0.128 GB ≈ 101,563 秒（约 28.2 小时），这是换算。单个对象全天不休眠约 11,059 GB-s，还在每天 13,000 以内；第二个全天不休眠会超。Paid 超出含用量后，计费量向上取整到下一个计费单位（例：50 万 GB-s 的超出部分会按 100 万 GB-s 计）。

SQLite 存储计费通知仍写「2026-01-07 起」（页面还是将来时）。[2025-12-12 changelog](https://developers.cloudflare.com/changelog/post/2025-12-12-durable-objects-sqlite-storage-billing/) 写明 Workers Free 不因此收费，Paid 超出含用量才收费。请求和时长从公测起就计费。

CPU：Workers limits 写明 DO 套用所在 Workers 计划，因此 Free 仍是每次 10 ms。DO limits 页把 CPU 写成默认 30 秒、可调到 5 分钟，与 Paid HTTP 默认一致。两页都打开再报 CPU。

请求怎么计：一次 RPC 方法调用 = 1 次请求；同一会话里对返回的 `RpcTarget` 再调用不计新请求。WebSocket 建连算 1 次。入站 WebSocket 消息计费时 20:1（100 条计 5 次请求），指标仍是实际条数。出站消息和协议 ping 不计。`setWebSocketAutoResponse()` 不增加墙钟。`setAlarm()` 计 1 行写入。`get` / `put` / `delete` / `list` 按隐藏表的行读/行写计。

### Workers、Pages Functions、账号上限

| 产品 | 计量 | Free | $5 含用量 | 含用量用完 | $5 的计划上限（不计费） |
|---|---|---|---|---|---|
| Workers | 请求 | 10 万/天，超限 1027 | 1,000 万/月 | $0.30/百万 | 无每日硬顶 |
| Pages Functions | 请求 | 与 Workers **共享**每天 10 万，不是另加 | 与 Workers **共享**那 1,000 万/月，不是另加 | 同 Workers | 同 Workers |
| Workers | CPU | 10 ms/次（HTTP 和 Cron 都是） | 3,000 万 CPU-ms/月 | $0.02/百万 CPU-ms | 单次 HTTP 默认 30 秒，最高 5 分钟。定价页写 Cron 与 Queue consumer 单次最高 15 分钟；limits 页把 Cron 拆成间隔短于 1 小时 30 秒、不少于 1 小时 15 分钟 |
| Pages Functions | CPU | 与 Workers 共享每次 10 ms | 与 Workers 共享那 3,000 万 CPU-ms | 同 Workers | 同 Workers |
| Workers | 墙钟时长 | 不计费 | 不计费（无月度含用量，也无月度上限） | 无 | HTTP 无硬顶（客户端保持连接）。Cron、Queue consumer、DO alarm 各 15 分钟。`waitUntil` 响应后最多约 30 秒 |
| Workers | Subrequests | 外部 50/次；对 Cloudflare 服务 1,000/次。不计费 | 无 | 不计费 | 默认 10,000/次，`limits.subrequests` 最高 1,000 万 |
| Workers | Worker 个数 | 100 | 无 | 无 | 500 |
| Workers | Cron | 5 个/账号 | 无 | 无 | 250 个/账号 |
| Workers | 环境变量 | 64/Worker，每个 ≤ 5 KB | 无 | 无 | 128/Worker，每个仍 ≤ 5 KB |
| Workers | 静态文件 | 每版本 20,000；单文件 25 MiB | 无 | 无 | 每版本 100,000；单文件仍 25 MiB。请求本身免费且无限 |
| Workers | 内存 | 128 MB/isolate | 无（与 Free 相同，不是赠送量） | 超限 1102 | 仍是 128 MB/isolate |
| Workers | Cache API | 50 次/请求（与 subrequest 共享）；对象 ≤ 512 MB | 无 | 不计费 | 1,000 次/请求；对象仍 ≤ 512 MB |
| Workers | 脚本体积 / 启动 | 64 MiB；全局作用域 1 秒 | 无 | 无 | 与 Free 相同 |
| Workers | 同时等待响应头的连接 | 6 | 无 | 无 | 6 |
| Workers Logs | 写入事件 | 20 万/天 | 2,000 万/月 | $0.60/百万 | 保留：Free 3 天，Paid 7 天。2026-12-01 起改 Observability 定价 |
| Logpush | Workers Trace Events | 无 | 1,000 万条/月 | $0.05/百万 | 仅 Paid |

静态资源请求不计请求费。Service Binding 调用同账号另一个 Worker 不另计请求费。Subrequest 不计费。打开 Workers Caching 后，缓存命中仍计请求（含静态资源和 Worker 间调用），CPU 只在 Worker 执行时计。

Pages 构建、每站文件数、请求体**不在 $5 里**，跟域名计划：Free 构建 500 次/月、1 并发、每站 20,000 文件、请求体 100 MB。Pro 才是 5,000 次构建和 100,000 文件。Business 请求体 200 MB（超限 413）。

### Durable Objects（写在 $5 包含列表里）

Free 只能用 SQLite 后端。任一项用尽，该类操作失败，不转成账单。

| 产品 | 计量 | Free | $5 含用量 | 含用量用完 | $5 的计划上限（不计费） |
|---|---|---|---|---|---|
| DO SQLite | 请求 | 10 万/天 | 100 万/月 | $0.15/百万 | 单个对象软限制 1,000 请求/秒（limits 页，未按计划拆开） |
| DO SQLite | 时长 | 13,000 GB-s/天 | 400,000 GB-s/月 | $12.50/百万 GB-s | 无月度时长硬顶 |
| DO SQLite | 行读 | 500 万/天 | 250 亿行/月 | $0.001/百万行 | 无 |
| DO SQLite | 行写 | 10 万/天 | 5,000 万行/月 | $1.00/百万行 | 无 |
| DO SQLite | 存储 | 账号合计 5 GB | 5 GB-月 | $0.20/GB-月 | 单对象：Free 1 GB，Paid 10 GB，写满 `SQLITE_FULL`。Paid 账号存储无硬顶 |
| DO | 类个数 | 100 | 无 | 无 | 500 |
| DO | CPU | 按 Workers Free：10 ms/次 | 无单独含用量；走 Workers 那 3,000 万 CPU-ms | 同 Workers | 见上文两页冲突说明 |
| DO key-value 后端 | 读请求单位 | 不可用 | 100 万/月 | $0.20/百万 | 仅限账号里已经存在的 KV 后端命名空间。1 单位 = 4 KB |
| DO key-value 后端 | 写请求单位 | 不可用 | 100 万/月 | $1.00/百万 | 同上。`setAlarm` 计 1 个写单位 |
| DO key-value 后端 | 删除 | 不可用 | 100 万/月 | $1.00/百万 | 删除按请求计，不按体积翻倍 |
| DO key-value 后端 | 存储 | 不可用 | 1 GB | $0.20/GB-月 | 单对象无「10 GB」那种 SQLite 上限（limits 页写 Unlimited） |

### KV、D1、Hyperdrive（KV 和 Hyperdrive 写在 $5 包含列表里；D1 的 included 在同一页）

| 产品 | 计量 | Free | $5 含用量 | 含用量用完 | $5 的计划上限（不计费） |
|---|---|---|---|---|---|
| KV | 读 | 10 万/天 | 1,000 万/月 | $0.50/百万 | limits 页写 Paid 读为 Unlimited，指没有硬顶 |
| KV | 写 | 1,000/天 | 100 万/月 | $5.00/百万 | 同一 key 仍是 1 次/秒 |
| KV | 删 | 1,000/天 | 100 万/月 | $5.00/百万 | 无硬顶 |
| KV | list | 1,000/天 | 100 万/月 | $5.00/百万 | 无硬顶 |
| KV | 存储 | 1 GB | 1 GB | $0.50/GB-月 | limits 页写 Paid 存储 Unlimited，指没有硬顶。每次调用最多 1,000 次 KV 操作（两计划相同）。命名空间 1,000 个（两计划相同） |
| D1 | 行读 | 500 万行/天 | 250 亿行/月 | $0.001/百万行 | 按扫描行数，不是返回行数 |
| D1 | 行写 | 10 万行/天 | 5,000 万行/月 | $1.00/百万行 | 无 |
| D1 | 存储 | 账号合计 5 GB | 5 GB | $0.75/GB-月 | 单库：Free 500 MB，Paid 10 GB。库个数：Free 10，Paid 5 万。账号存储硬顶：Free 5 GB，Paid 1 TB |
| D1 | 每次调用 query 数 | 50 | 无（这是上限，不是月度含用量） | 无 | 1,000。`db.batch()` 里每条语句单独计数 |
| D1 | Time Travel | 7 天 | 无 | 无 | 30 天 |
| Hyperdrive | 查询 | 10 万/天（SELECT、写入、DDL 都算） | 不限。没有「含 N 次」这种数字，也没有按量价 | 无 | 配置：Free 10，Paid 25。到源库连接：Free 约 20，Paid 约 100。单条查询最长 60 秒（两计划相同） |

### R2：有免费操作额度，但不是 $5 含用量

R2 定价页（2026-10-01）的免费档对所有账号按月给出，**不**因为买了 Workers Paid 而变多。只适用于 **Standard**。Infrequent Access 不享受这份免费档。超出后向上取整到下一个计费单位（操作按百万次，存储按 GB-月）。

| 产品 | 计量 | 免费档（不是 $5） | $5 含用量 | 免费档用完（Standard） | 备注 |
|---|---|---|---|---|---|
| R2 Standard | 存储 | 10 GB-月/月 | 无 | $0.015/GB-月 | |
| R2 Standard | A 类操作 | 100 万次/月 | 无 | $4.50/百万 | 见下方名单 |
| R2 Standard | B 类操作 | 1,000 万次/月 | 无 | $0.36/百万 | 见下方名单 |
| R2 | 出口 | 免费 | 免费（不是从 $5 里扣） | 仍免费 | |
| R2 | `DeleteObject`、`DeleteBucket`、`AbortMultipartUpload` | 免费 | 免费 | 仍免费 | 不算 A 类或 B 类 |
| R2 Infrequent Access | 存储 / 操作 / 取回 | 无免费档 | 无 | 存储 $0.01/GB-月；A 类 $9.00/百万；B 类 $0.90/百万；取回 $0.01/GB | 最短存储 30 天 |

A 类：`ListBuckets`、`PutBucket`、`ListObjects`、`PutObject`、`CopyObject`、`CompleteMultipartUpload`、`CreateMultipartUpload`、`LifecycleStorageTierTransition`、`ListMultipartUploads`、`UploadPart`、`UploadPartCopy`、`ListParts`、`PutBucketEncryption`、`PutBucketCors`、`PutBucketLifecycleConfiguration`。

B 类：`HeadBucket`、`HeadObject`、`GetObject`、`UsageSummary`、`GetBucketEncryption`、`GetBucketLocation`、`GetBucketCors`、`GetBucketLifecycleConfiguration`。

### Queues、Workflows、Vectorize、Workers AI、Containers、其它含用量

| 产品 | 计量 | Free | $5 含用量 | 含用量用完 | 上限或其它 |
|---|---|---|---|---|---|
| Queues | 操作 | 1 万次/天 | 100 万次/月 | $0.40/百万 | 一条消息通常是写 + 读 + 删共 3 次；超过 64 KB 按块翻倍。保留：Free 24 小时不可调；Paid 默认 4 天，最长 14 天。队列个数 10,000/账号（两计划相同） |
| Workflows | 请求 | 与 Workers 共享 10 万/天 | 与 Workers **共享**那 1,000 万/月，不是另加 | $0.30/百万 | |
| Workflows | CPU | 10 ms/次 | 与 Workers **共享**那 3,000 万 CPU-ms，不是另加 | $0.02/百万 CPU-ms | Paid 可用 `limits.cpu_ms` 把单次 Workflow 调到最高 5 分钟 |
| Workflows | 存储 | 1 GB-月 | 1 GB-月 | $0.20/GB-月 | 实例状态保留：Free 3 天，Paid 30 天。Free 存满再写会抛错。step 与存储的计费起始日文档写为 2026-08-10 |
| Workflows | step | 3,000/天 | 50 万/月 | 每多 10 万 step $0.80 | 回滚和重试不算 step |
| Vectorize | 查询维度 | 3,000 万/月 | 5,000 万/月 | $0.01/百万 | Workers 总定价页仍有一句 “paid plan only”，与产品页冲突，以 Vectorize 产品页为准 |
| Vectorize | 存储维度 | 500 万 | 1,000 万 | $0.05/1 亿维度 | 索引：Free 100，Paid 5 万。每索引命名空间：Free 1,000，Paid 5 万 |
| Workers AI | Neurons | 1 万/天，超出失败 | **无月度含用量**。Paid 上仍是每天先送这 1 万 | $0.011/千 Neurons | 这 1 万不是 $5 里的月度配额。部分前沿模型必须有 Workers Paid 或 AI Gateway 预付费 |
| Containers | 内存 | 无 | 25 GiB-小时/月 | $0.0000025/GiB-秒 | 文档写明这份含用量属于 $5 |
| Containers | vCPU | 无 | 375 vCPU-分钟/月 | $0.000020/vCPU-秒 | |
| Containers | 磁盘 | 无 | 200 GB-小时/月 | $0.00000007/GB-秒 | |
| Containers | 出口 | 无 | 北美与欧洲 1 TB；大洋洲、韩国、台湾 500 GB；其它地区 500 GB | 分别 $0.025 / $0.05 / $0.04 每 GB | 按实际运行的每 10 ms 计，空闲休眠后停止 |
| Browser Run | 浏览器时长 | 10 分钟/天 | 10 小时/月 | $0.09/小时 | Quick Actions 与 Sessions 共享时长 |
| Browser Run | 并发浏览器 | 3（仅 Sessions） | 无单独「含 N 个」以外的月度包；含的是月平均 10 个 | 超出每个 $2 | 月平均 = 每日峰值再对整月取平均 |
| Analytics Engine | 写入 | 10 万点/天 | 公布价：1,000 万/月 | 公布价 $0.25/百万 | 定价页写明**目前不收费** |
| Analytics Engine | 读查询 | 1 万次/天 | 公布价：100 万/月 | 公布价 $1.00/百万 | 同上 |
| AI Search | 摄入 token | 500 万/月（每账号，不是 Paid 加码） | 与 Free 相同的 500 万/月，不是另加 | $0.75/百万 token；图像处理再加 $0.50/百万 | 计费日 2026-11-01。实例：Free 100，Paid 5,000。爬取：Free 500 页/天，Paid 不限 |
| AI Search | 存储 | 10 GB-月 | 与 Free 相同的 10 GB-月 | $2.00/GB-月 | |
| AI Search | 语义查询 | 1,000/月 | 与 Free 相同的 1,000/月 | $0.75/千次（含向量和混合） | |
| AI Search | 全文查询 | 1,000/月 | 与 Free 相同的 1,000/月 | $0.10/千次 | |
| Email Sending | 任意收件人 | 不可用 | 3,000 封/月 | $0.35/千封 | 发给已验证目标地址在两个计划都免费，且不占这 3,000 |
| Email Routing | 入站封数 | 不限 | 无额外含用量（本来不限） | 无 | 规则 200/域，目标地址 200/账号，两计划相同 |
| AI Gateway | 核心功能 | 免费，无封顶数字 | 无额外含用量 | 无 | 分析、缓存、速率限制。Legacy Logs（2026-09-24 前创建）：Free 全账号 10 万条，Paid 每网关 1,000 万条。新网关走 Workers Logs。Logpush 仅 Paid：1,000 万条/月，超出 $0.05/百万 |
| Workers VPC | 服务费 | 开放测试期间免费 | 无额外含用量 | 测试期不另收费 | Worker 的请求和 CPU 仍走上面的 Workers 含用量。VPC Service 1,000/账号 |

Images 的 5,000 次唯一变换、Zaraz 的 100 万事件、Turnstile 的 Free 计划、Cache/CDN、Tunnel，都不在 Workers $5 里。买 Workers Paid 不会提高它们。Stream 存储分钟和分发分钟没有免费档，也没有 $5 含用量。

## 补充额度：Workers Builds、Artifacts、Basin、AI Gateway

区分 **Workers Paid 月度含量** 与 **产品自身独立含量**；不能将同一月度含量重复累计到 $5 套餐。

| 产品 | Free | Paid 或产品月度含量 | 超出价格及附加条件 |
|---|---|---|---|
| Workers Builds | 3,000 构建分钟/月、1 并发 | **6,000 分钟/月、6 并发** | 超出 $0.005/分钟；构建最长 20 分钟；与 Pages Builds 不同 |
| Artifacts 仓库操作 | 不可用 | **1 万次/月** | 超出 $0.15/每 1,000 次；2026-10-14 计划开始计费 |
| Artifacts 存储 | 不可用 | **1 GB-月** | 超出 $0.50/GB-月；起始日期同上 |
| Basin Pipelines（原 Pipelines） Stream 输入 | 2026-10 官方定价页未列 Free，需核查 | 不限输入量，免费 | R2 与 Catalog 另行计费 |
| Basin Pipelines（原 Pipelines） SQL 转换 | 2026-05 曾公告 1 GB/月；当前 Free 待复核 | **50 GB/月** | $0.04/GB |
| Basin Pipelines（原 Pipelines） Sink 输出 | 2026-05 曾公告 1 GB/月；当前 Free 待复核 | **50 GB/月，所有格式共享** | JSON $0.03/GB；Parquet / Iceberg $0.06/GB；每目的地按未压缩数据量计 |
| Basin Catalog（原 R2 Data Catalog） 操作 | 产品独立含量 | **100 万次/月**（不是 $5 额外赠量） | $9/百万次 |
| Basin Catalog（原 R2 Data Catalog） 压缩数据 | 产品独立含量 | **10 GB/月** | $0.005/GB；开启 compaction 才计费 |
| Basin Catalog（原 R2 Data Catalog） 压缩对象 | 产品独立含量 | **100 万个/月** | $2/百万个；开启 compaction 才计费 |
| Basin SQL（原 R2 SQL） 压缩数据扫描 | 产品独立含量，需满足开通条件 | **10 GB/月** | $0.0025/GB；每查询最少 10 MB，R2 Class B 和 Catalog 操作另计 |
| AI Gateway 网关数量 | **10 个/账号** | **20 个/账号** | 计划个数上限，不是额外模型免费调用次数 |

**$5 不是账单封顶**。Workers 请求和 CPU、存储、Durable Objects 时长、Basin 等可能按量收费；`limits.cpu_ms` 和 `limits.subrequests` 均不能代替月度账单限额或预算告警。

