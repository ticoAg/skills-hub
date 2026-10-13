# 提示词与历史记录

## 完整提示词骨架

填写后删除占位符与不适用项；给每张作品一个自足提示词。

```text
用途：具有明确主视觉与标题层级的东方封面海报，9:16 竖幅。
诗意依据：<确切原句与最小完整诗意；不是要求全文印进画面>。
必须可见：<2–4 项锚点，至少一个动作／物象关系>。
主体与场景：<身份、数量、动作、相对位置、方向；标明艺术隐喻>。
关键瞬间：<时间、事件阶段、时辰一致的光线>。
主构图机制：<视角、尺度、密度、主次、空间层级及对应情绪>。
色彩与材质：<原诗支持的色彩，清透光线、清晰边缘、轻纸纹>。
标题区：<位置与留白，安全边距>。
只允许印出以下文字，逐字准确：
主句：“<原句>”；分行：<说明>；位置：<说明>。
次文字：“<篇名>”“<确认的作者>”；位置与大小：<说明>。
排版：<清晰宋体、横排或明确竖排顺序>。
合理补充：<少量且服务核心关系的细节>。
禁止：<本诗特有矛盾、无依据剧情>；额外伪文字、错字、水印、全图灰雾、过度水墨化。
本次区别：<相较可见历史的三个维度变化；无历史可省略>。
```

只把“允许印出”的文案放进画面，不印技术字段、证据编号、模型说明或数据库路径。语义锚点是画面要求，不能靠在角落写出对应文字算作“已呈现”。

## 稳定分类

每个维度选一个主要标签；新增标签前检查已有同义项。记录空间机制，不以诗名或颜色作为标签。语义相同而写法不同不算创新。

| 维度 | 推荐标签 |
| --- | --- |
| layout | vertical-axis, diagonal-flow, horizontal-bands, corner-anchor, frame-within-frame, radial-reveal |
| viewpoint | eye-level, bird-eye, low-angle, water-level, close-crop |
| subject_relation | isolated-in-vastness, crossing-space, touching-boundary, seen-through-frame, emerging-from-cover, reflection-pair |
| scale | tiny-in-landscape, balanced-midshot, monumental-object, macro-detail |
| medium | paper-stage, restrained-illustration, editorial-photo, sculptural-relief |
| lighting | diffuse-day, crisp-dawn, soft-dusk, moonlit, interior-glow |
| typography | top-horizontal, side-vertical, bottom-horizontal, central-negative-space |

## 方案 JSON

必需字段：`poem` 为本次原文，`anchors` 为 2–4 个语义锚点，`axes` 为七个分类值。可选 `title/author/locked_axes/prompt`。锁定维度写在 `locked_axes` 数组。不确定作者就省略。

```json
{
  "poem": "千山鸟飞绝，万径人踪灭。孤舟蓑笠翁，独钓寒江雪。",
  "title": "江雪",
  "author": "柳宗元",
  "anchors": ["群山与路径无人无鸟", "一舟一翁独钓", "寒江雪"],
  "axes": {
    "layout": "corner-anchor",
    "viewpoint": "bird-eye",
    "subject_relation": "isolated-in-vastness",
    "scale": "tiny-in-landscape",
    "medium": "restrained-illustration",
    "lighting": "diffuse-day",
    "typography": "top-horizontal"
  },
  "locked_axes": []
}
```

## 使用历史工具

将方案写入当前项目输出目录，用本 skill 的绝对路径调用：

```bash
python <skill目录>/scripts/poster_history.py list --db output/poetry-posters/history.sqlite3 --limit 20
python <skill目录>/scripts/poster_history.py check --db output/poetry-posters/history.sqlite3 --plan output/poetry-posters/plan.json
python <skill目录>/scripts/poster_history.py record --db output/poetry-posters/history.sqlite3 --plan output/poetry-posters/plan.json --artifact <已验收成品路径或工具作品标识>
```

替换所有 `<...>` 占位符。`list/check` 只读，数据库不存在时返回空历史且不创建文件。通过退出 0；重复／差异不足退出 2；输入或文件错误退出 1。`record` 用 SQLite 写事务重新检查后追加，拒绝的作品不写入；必须先目视验收，脚本不能证明图片真实或诗意正确。

比较同诗最近三条加全项目最近二十条。诗文用 Unicode 规范化并忽略空白、标点生成同诗标识，不更改排版底稿。每条历史要求至少三项未锁定轴不同，至少一项空间轴不同；自由轴不足三项且有历史就拒绝。不能任意锁轴绕过检查。

数据库保存原文、锚点、提示词、分类与作品标识，只放当前授权项目，不自动提交或上传。后续只有数据库仍可访问或被用户提供时才能用于跨会话去重。无历史图时分类相似度仍不能代替实际画面比较。
