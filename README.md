# Skills Hub

可复用的 AI 助手技能集合。

| 技能 | 用途 |
| --- | --- |
| [cloudflare-free-tier](cloudflare-free-tier/SKILL.md) | Cloudflare 免费计划与 Workers Paid 低成本架构选择 |
| [poetry-poster](poetry-poster/SKILL.md) | 原文驱动的诗词意境海报与中文排版 |

## 诗词意境海报 · poetry-poster

将诗、词、曲或原创诗句转为有准确中文排版的封面海报。默认 9:16 现代东方极简风格；保留原文意境，让主体和空间服从诗意，避免每首诗都套用“古风女子＋长卷”。

**内容理解**：提取对象与动作、时空进程、观察者、情绪转折、感官节奏、对照修辞与主题留白。区分原文事实、推断和艺术隐喻。

**语义画面规格**：用原文证据连接必须保留的锚点、关系和具体视觉决定；明确不变量、可变构图与禁止项。

**视觉展示**：比较三种构图，使用可用图像工具出图，配上准确原句并检查最终画面。SQLite 历史工具检查至少三个构图维度变化，无额外 Python 依赖。

入口：[poetry-poster/SKILL.md](poetry-poster/SKILL.md)。支持 `gpt-image-2.5` 家族偏好，实际版本与调用能力以当前工具、官方文档和账号为准；不保证内置工具可选模型。

## 安装到 Codex

将 `poetry-poster` 整个目录复制到 Codex skills 目录，例如 `~/.codex/skills/poetry-poster`，保留 `agents`、`references` 与 `scripts`。重新加载后用 `$poetry-poster` 调用。其他支持 `SKILL.md` 的助手按其目录规范安装。

## 使用

```text
使用 $poetry-poster，把柳宗元《江雪》画成 9:16 东方极简封面：
千山鸟飞绝，万径人踪灭。孤舟蓑笠翁，独钓寒江雪。
留白处排“独钓寒江雪”，不要额外人物。
```

```text
使用 $poetry-poster，根据“兴尽晚回舟，误入藕花深处。
争渡，争渡，惊起一滩鸥鹭。”做一张有惊喜感的诗词海报，
保留文艺封面感，自行补充合理画面。
```

```text
使用 $poetry-poster，同一首诗再做一张，保留原句与配色，
与当前项目历史作品至少改变三个构图维度。
```

```text
使用 $poetry-poster，保留巨大空白垂卷和下方偏侧的米白古风女子，
她抬手轻触卷边。结合我提供的诗句，只输出完整生成提示词。
```

跨会话变化依赖可访问历史，构图分类不保证感知上的绝对不重复。无图像工具时只输出提示词，不声称已生成海报。

## 验证

运行 `python -m unittest discover -s tests -v` 检查历史工具行为。语义预演案例见 [evaluation-cases.md](poetry-poster/references/evaluation-cases.md)。这些检查不代表未经生成的图像已通过实际验收。
