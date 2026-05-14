# 知到网课自动连播助手

> 装一次，永久生效。看知到网课时自动播放 + 自动跳下一集，你只管记笔记。

## 安装步骤（3 分钟搞定）

### 1. 装 Tampermonkey 插件
打开 Edge 或 Chrome 浏览器，进入扩展商店搜索 **Tampermonkey**（篡改猴），安装即可。

- Edge: https://microsoftedge.microsoft.com/addons/detail/tampermonkey/iikmkjmpaadaobahmlepeloendndfphd
- Chrome: https://chromewebstore.google.com/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo

### 2. 导入脚本
- 点击浏览器右上角 Tampermonkey 图标 → **管理面板**
- 点击 **实用工具** 标签
- 在「从 URL 安装」里粘贴下面的地址，点安装：

```
https://raw.githubusercontent.com/aB-iJ/lobster-link/main/zhidao-autoplay/zhidao-autoplay.user.js
```

> 或者直接把 `zhidao-autoplay.user.js` 文件拖到 Tampermonkey 管理页面。

### 3. 打开知到，开始记笔记
打开知到网课页面，右下角会出现 🎬 **知到助手** 控制面板。

## 功能说明

| 功能 | 说明 | 默认 |
|------|------|------|
| 自动播放 | 检测视频，自动点击播放 | ✅ 开 |
| 自动下一集 | 视频播完自动跳下一集 | ✅ 开 |
| 自动关弹窗 | 自动关闭"知道了"等弹窗 | ✅ 开 |
| 静音播放 | 后台静音（听课建议别开） | ❌ 关 |
| 倍速播放 | 1.25x ~ 2.0x 可调 | ❌ 关 |
| 手动跳集 | 点击面板按钮手动跳下一集 | - |

右下角面板可折叠，不影响看视频。

## 注意事项

- **只支持知到（zhihuishu.com）域名**，其他平台不会生效
- 如果知到改了页面结构导致失效，告诉我，我更新脚本
- 如果安装后没生效，刷新页面试试
- 脚本完全本地运行，不会上传任何数据

## 文件

```
zhidao-autoplay/
├── zhidao-autoplay.user.js   ← 主脚本（拖进 Tampermonkey 就能用）
└── README.md                 ← 本文件
```
