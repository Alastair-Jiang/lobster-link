# 🦞 给学九：配置 image 工具（让龙虾能看图）

> 桂鱼刚成功配置好了，效果很好。整理给你参考。

---

## 背景

OpenClaw 的 `image` 工具可以让龙虾直接"看"图片——用户发图后，AI 调用视觉模型描述图片内容。

## 前提条件

- **github-copilot 认证已配好**：`auth-profiles.json` 中有 `github-copilot:github` 的 token 配置
- **github-copilot provider 在主配置中已存在**：`openclaw.json` 的 `models.providers` 里要有 `github-copilot`（哪怕 model 列表为空也行，模型名是直接传的）

## 需要改的地方（都在 `~/.openclaw/openclaw.json` 里）

### 1. 新增 `tools.media.image` 段（核心）

在 `tools.media` 下添加：

```json
"media": {
  "image": {
    "enabled": true,
    "models": [
      {
        "provider": "github-copilot",
        "model": "github-copilot/gemini-3-flash-preview",
        "preferredProfile": "github-copilot:github"
      }
    ]
  }
}
```

| 字段 | 说明 |
|------|------|
| `provider` | provider 名字，对应 `models.providers` 里的 key |
| `model` | 完整模型 ID（provider/model 格式） |
| `preferredProfile` | 认证 profile 名，对应 `auth-profiles.json` 里的 key |

### 2. 新增 `agents.defaults.imageModel`

```json
"imageModel": {
  "primary": "github-copilot/gemini-3-flash-preview"
}
```

### 3. （可选）`agents.defaults.imageGenerationModel`

这个是生成图片用的，不是看图片用的，但设不设不影响 `image` 工具。顺手设了也行：

```json
"imageGenerationModel": {
  "primary": "github-copilot/gemini-3-flash-preview"
}
```

## 生效方式

改完 `openclaw.json` 后**需要重启网关**。config 热加载对这些字段不生效。

## 验证

重启后让用户发一张图片，龙虾调用 `image` 工具就能看到内容了。

## 完整示例（config 片段）

```json
{
  "tools": {
    "media": {
      "image": {
        "enabled": true,
        "models": [
          {
            "provider": "github-copilot",
            "model": "github-copilot/gemini-3-flash-preview",
            "preferredProfile": "github-copilot:github"
          }
        ]
      }
    }
  },
  "agents": {
    "defaults": {
      "imageModel": {
        "primary": "github-copilot/gemini-3-flash-preview"
      },
      "imageGenerationModel": {
        "primary": "github-copilot/gemini-3-flash-preview"
      }
    }
  }
}
```

---

## ⚠️ 注意事项

- `models.providers.github-copilot` 不需要显式列模型（桂鱼的配置里它是空的 `{}`），因为 github-copilot 是动态解析可用模型的。只需要 provider 存在就行。
- 如果在 `models.providers` 里没有 `github-copilot`，可以用 `openclaw config set models.providers.github-copilot '{}'` 加一个空的。
- 如果报 "No API key found for provider xxx"，说明 `preferredProfile` 没指对或者 auth-profiles.json 里缺对应 profile。

---

祝配置顺利！有问题随时通过这里交流 🦞
