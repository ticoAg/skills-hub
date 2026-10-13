# Cloudflare 官方来源与计费变更追踪

> 核对日期：2026-10-12。当前文档可能已经变化。AI/自动化在引用数值、制定配额预算或部署前，需打开对应官方定价/limits 页面核验。遇到产品页与总览页冲突，明确标记，不能推断为无限或承诺绝对免费。

## 重要时效提醒

- **2026-10-14** Artifacts 预计开始按量计费；日期接近时重新核实。
- **2026-11-01** AI Search 预计开始用量计费，查官方当前情况。
- **2026-12-01** Workers Logs 预计转用 Observability 定价。
- **Basin Pipelines（原 Pipelines）**：2026-05 官方公告给出 Free 各 1 GB/月，但 2026-10 产品定价页面只显示 Paid 列。Free 实际可用性需查最新官方页面和账户状态。
- **Vectorize**：Workers 总览页与 Vectorize 产品页曾有 Paid-only 文字冲突，以产品页及账号实际可用性核实。
- **Paid $5**：是最低月费，不是超额支出的绝对上限。

## 原始参考链接

- Workers limits：https://developers.cloudflare.com/workers/platform/limits/
- Workers pricing（含 KV、Hyperdrive、Queues、Workflows、D1、Durable Objects、R2、Vectorize、Containers、Logs）：https://developers.cloudflare.com/workers/platform/pricing/
- Subrequest changelog（2026-02-11）：https://developers.cloudflare.com/changelog/post/2026-02-11-subrequests-limit/
- Pages limits：https://developers.cloudflare.com/pages/platform/limits/
- Pages Functions pricing：https://developers.cloudflare.com/pages/functions/pricing/
- D1 limits：https://developers.cloudflare.com/d1/platform/limits/
- Durable Objects pricing：https://developers.cloudflare.com/durable-objects/platform/pricing/
- Durable Objects limits（含 Free 单对象 1 GB）：https://developers.cloudflare.com/durable-objects/platform/limits/
- DO SQLite 存储计费 changelog（2025-12-12）：https://developers.cloudflare.com/changelog/post/2025-12-12-durable-objects-sqlite-storage-billing/
- KV limits：https://developers.cloudflare.com/kv/platform/limits/
- R2 pricing（免费档、A/B 类操作名单；不是 $5 含用量）：https://developers.cloudflare.com/r2/pricing/
- R2 limits：https://developers.cloudflare.com/r2/platform/limits/
- Queues limits：https://developers.cloudflare.com/queues/platform/limits/
- Workflows pricing：https://developers.cloudflare.com/workflows/reference/pricing/
- Hyperdrive limits：https://developers.cloudflare.com/hyperdrive/platform/limits/
- Workers AI pricing：https://developers.cloudflare.com/workers-ai/platform/pricing/
- Vectorize pricing：https://developers.cloudflare.com/vectorize/platform/pricing/
- Vectorize limits：https://developers.cloudflare.com/vectorize/platform/limits/
- Browser Run pricing：https://developers.cloudflare.com/browser-rendering/platform/pricing/
- Images pricing：https://developers.cloudflare.com/images/pricing/
- Stream pricing（无免费存储/分发分钟）：https://developers.cloudflare.com/stream/pricing/
- Zaraz pricing：https://developers.cloudflare.com/zaraz/pricing-info/
- Turnstile plans：https://developers.cloudflare.com/turnstile/plans/
- Email Service pricing：https://developers.cloudflare.com/email-service/platform/pricing/
- Email Routing limits：https://developers.cloudflare.com/email-routing/limits/
- AI Gateway pricing：https://developers.cloudflare.com/ai-gateway/reference/pricing/
- AI Search limits & pricing：https://developers.cloudflare.com/ai-search/platform/limits-pricing/
- Analytics Engine pricing：https://developers.cloudflare.com/analytics/analytics-engine/pricing/
- Workers VPC pricing：https://developers.cloudflare.com/workers-vpc/platform/pricing/
- Cache 可缓存大小与清除限额：https://developers.cloudflare.com/cache/concepts/default-cache-behavior/ 与 https://developers.cloudflare.com/cache/how-to/purge-cache/
- Cache Reserve（无免费额度）：https://developers.cloudflare.com/cache/advanced-configuration/cache-reserve/
- Tunnel 路由（视频与大文件）：https://developers.cloudflare.com/tunnel/concepts/routing/
- Quick Tunnels：https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/
- Web Analytics limits：https://developers.cloudflare.com/web-analytics/limits/

## 新增官方定价资料

- Workers Builds：https://developers.cloudflare.com/workers/ci-cd/builds/limits-and-pricing/
- Artifacts pricing：https://developers.cloudflare.com/artifacts/platform/pricing/
- Artifacts 计费开始时间：https://developers.cloudflare.com/changelog/post/2026-10-01-artifacts-open-beta/
- Basin 全线 pricing：https://developers.cloudflare.com/basin/platform/pricing/
- Basin Pipelines（原 Pipelines） 定价：https://developers.cloudflare.com/basin-pipelines/platform/pricing/
- Basin Pipelines（原 Pipelines） Free 额度历史公告：https://developers.cloudflare.com/changelog/post/2026-05-11-pipelines-pricing-announced/
- Basin Catalog（原 R2 Data Catalog） 定价：https://developers.cloudflare.com/basin-catalog/platform/pricing/
- Basin SQL（原 R2 SQL） 定价：https://developers.cloudflare.com/basin-sql/platform/pricing/
- AI Gateway limits：https://developers.cloudflare.com/ai-gateway/reference/limits/
