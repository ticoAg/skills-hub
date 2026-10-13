# 推荐 MVP 栈最小示例（Vite + React + Hono + D1 + R2）

只在要写 `wrangler.jsonc`、Hono 路由或部署命令时读取本文件。配额与选型以 `../SKILL.md` 为准，数字报给用户前重新抓取官方文档。

本示例不绑定 Durable Objects、Queues、Vectorize、KV 或 Hyperdrive。这些产品在 Workers Free 上各有硬顶（DO 还有每天的请求、GB-s 时长、行读/行写和 5 GB 存储），不要从「这里没写」推断成没有免费额度，也不要推断成无限。需要绑定时先读 `free-limits.md` 和 `paid-5-pricing.md`。

字段名以当前 wrangler config schema 为准（`node_modules/wrangler/config-schema.json`，或文档 https://developers.cloudflare.com/workers/wrangler/configuration/ ）。

## wrangler.jsonc

`run_worker_first` 只用路径数组。设成 `true` 会让每个静态文件都进入 Worker，免费计划每天 10 万请求会被静态流量吃掉。

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "my-app",
  "main": "worker/index.ts",
  "compatibility_date": "2026-10-12",
  "compatibility_flags": ["nodejs_compat"],
  "assets": {
    "directory": "./dist",
    "not_found_handling": "single-page-application",
    "run_worker_first": ["/api/*"]
  },
  "d1_databases": [
    { "binding": "DB", "database_name": "my-app", "database_id": "<id>" }
  ],
  "r2_buckets": [{ "binding": "BUCKET", "bucket_name": "my-app-files" }],
  // Paid 之后再打开，避免单次调用把 CPU 打满
  // "limits": { "cpu_ms": 30, "subrequests": 50 },
  "observability": { "enabled": true }
}
```

## worker/index.ts（Hono，一次取一批）

`Env` 用 `wrangler types` 生成，不要手写绑定类型。

```ts
import { Hono } from "hono";
import { drizzle } from "drizzle-orm/d1";
import { inArray } from "drizzle-orm";
import { icons } from "./schema";

const app = new Hono<{ Bindings: Env }>();

// 一次查询拿这批 id，而不是每个 id 一次 D1 query
app.get("/api/icons", async (c) => {
  const ids = (c.req.query("ids") ?? "").split(",").filter(Boolean).slice(0, 100);
  const db = drizzle(c.env.DB);
  const rows = await db.select().from(icons).where(inArray(icons.id, ids));
  return c.json(rows);
});

// 一次 list 代替 N 次 get。免费计划对 Cloudflare 服务约 1,000 次/调用，逐文件 get 仍会打满
app.get("/api/files", async (c) => {
  const listed = await c.env.BUCKET.list({
    prefix: c.req.query("prefix"),
    limit: 1000,
  });
  return c.json(listed.objects.map((object) => ({ key: object.key, size: object.size })));
});

// 多条写入走 batch。每条语句仍计入「每次调用 query 数」（免费 50 / Paid 1,000）
app.post("/api/icons/import", async (c) => {
  let body: unknown;
  try {
    body = await c.req.json();
  } catch {
    return c.json({ error: "Invalid JSON" }, 400);
  }
  // 不要 slice(0, 20)：大于 20 条时直接报错，避免静默丢数据。
  if (!Array.isArray(body) || body.length === 0 || body.length > 20) {
    return c.json({ error: "Send 1-20 items per request; split larger imports" }, 400);
  }
  const isIcon = (x: unknown): x is { id: string; name: string } =>
    typeof x === "object" && x !== null &&
    "id" in x && typeof x.id === "string" && x.id.length > 0 &&
    "name" in x && typeof x.name === "string" && x.name.length > 0;
  if (!body.every(isIcon)) {
    return c.json({ error: "Each item needs a nonempty string id and name" }, 400);
  }
  const db = drizzle(c.env.DB);
  await db.batch(body.map((row) => db.insert(icons).values(row)));
  return c.json({ inserted: body.length });
});

export default app;
```

大文件不要经这个 Worker 转发。上传应走 R2 预签名 URL 或 multipart，浏览器直传。

## 常用命令

```bash
npm create cloudflare@latest my-app   # 选 React + Worker 模板
npx wrangler d1 create my-app
npx wrangler r2 bucket create my-app-files
npx wrangler types                    # 生成 Env，不要手写
npx drizzle-kit generate && npx wrangler d1 migrations apply my-app --remote
npx wrangler deploy
```
