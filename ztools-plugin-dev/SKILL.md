---
name: ztools-plugin-dev
description: "Comprehensive guide for developing ZTools desktop software plugins. Use when creating, configuring, building, or publishing ZTools plugins. Covers plugin.json configuration, preload.js setup, Node.js integration, plugin API usage, and the publish workflow. Triggers on: ZTools plugin development, ztools plugin creation, plugin.json config, preload.js, ztools API, ztools publish, ZTools插件开发."
---

# ZTools 插件开发指南

## 概述

ZTools 插件应用结合了 Web 前端技术（HTML/CSS/JS）和 Node.js 本地原生能力，支持跨平台运行（Windows、macOS、Linux）。本指南覆盖从环境准备到发布的完整流程。

## 快速开始

### 环境要求

| 工具 | 版本 | 用途 |
|------|------|------|
| ZTools | 最新版 | 运行插件 |
| Node.js | >= 16.0.0 | 本地原生能力 |
| Git | - | 版本控制和发布 |
| VSCode/WebStorm | - | 代码编辑 |

### 基础知识

- JavaScript、HTML、CSS
- Node.js 基础
- 可选：Vue、React 等前端框架

## 插件创建流程

### 1. 安装 CLI 工具

```bash
npm install -g @ztools-center/plugin-cli
```

### 2. 创建项目

```bash
ztools create my-plugin
```

选择模板：
- `Vue + TypeScript + Vite` - Vue 3 开发插件 UI
- `React + TypeScript + Vite` - React 开发插件 UI
- `Preload Only (TypeScript)` - 仅使用 Preload API，无 UI

### 3. 开发与构建

```bash
cd my-plugin
npm install
npm run dev    # 开发模式
npm run build  # 构建到 dist/
```

## 核心概念

### plugin.json 配置

必填字段：
- `name` - 插件唯一标识（ID）
- `title` - 显示名称
- `main` - 入口文件（.html 或在线地址）
- `logo` - Logo 文件（png/jpg）
- `preload` - 预加载 JS 文件

功能定义（features）：
```json
{
  "features": [{
    "code": "功能标识",
    "explain": "功能说明",
    "cmds": ["文本指令", {"type": "regex", "match": "/正则/"}]
  }]
}
```

指令类型：文本(String)、正则(RegexCmd)、全局(OverCmd)、图片(ImgCmd)、文件(FilesCmd)

详细配置说明：参阅 `references/plugin-json.md`

### preload.js

preload.js 是连接前端和 Node.js 的桥梁，遵循 CommonJS 规范：

```javascript
const fs = require("node:fs");
window.myApi = {
  readFile: (path) => fs.readFileSync(path, "utf8"),
};
```

关键规则：
- 代码不能打包/压缩/混淆，必须清晰可读
- 第三方模块源码需一同提交
- 在 `window` 上挂载属性供前端访问

详细使用说明：参阅 `references/preload.md`

### Node.js 集成

在 preload.js 中可引入：
- Node.js 原生模块（fs, path, os 等）
- 自己编写的模块（相对路径 require）
- 第三方 npm 模块（需在 preload 同级目录有 package.json，type 设为 commonjs）
- Electron 渲染进程 API

详细说明：参阅 `references/preload.md`

## 插件 API

通过 `window.ztools` 全局对象访问。完整 API 列表：参阅 `references/api.md`

### 常用 API 分类

| 类别 | 主要方法 |
|------|---------|
| 基础 | `getAppName()`, `isMacOs()`, `isWindows()`, `showNotification()`, `hideMainWindow()` |
| 事件 | `onPluginEnter()`, `onPluginOut()`, `onMainPush()` |
| 搜索框 | `setSubInput()`, `setSubInputValue()`, `removeSubInput()` |
| 数据库 | `db.put()`, `db.get()`, `db.remove()`, `db.allDocs()` |
| 存储 | `dbStorage.setItem()`, `dbStorage.getItem()` |
| 剪贴板 | `clipboard.getHistory()`, `clipboard.write()`, `copyText()` |
| 文件 | `getPath()`, `showSaveDialog()`, `showOpenDialog()`, `screenCapture()` |
| 窗口 | `createBrowserWindow()`, `sendToParent()` |
| AI | `ai()`, `allAiModels()` |

## 发布流程

### 前置条件

1. 项目包含 `plugin.json`
2. 已 `git init` 并至少一次 commit
3. 工作区干净

### 发布命令

```bash
ztools publish
```

首次发布会自动：
- GitHub OAuth 认证
- Fork 中心仓库
- 创建 PR

后续发布：增量追加 commit，复用同一个 PR。

### 发布后操作

1. 上传截图/GIF 到 PR
2. 勾选自检清单
3. 将 PR 从 Draft 切到 Ready for review

### 协作流程

审核者修改后，执行 `ztools pull-contributions` 拉取改动。

详细发布流程：参阅 `references/publishing.md`

## 目录结构

```
plugin/
├── plugin.json      # 插件配置（必填）
├── preload.js       # 预加载脚本（必填）
├── index.html       # 入口页面
├── logo.png         # 插件 Logo（必填）
├── src/             # 源码目录
├── dist/            # 构建输出（打包此目录）
└── package.json     # Node.js 依赖（如有）
```

详细说明：参阅 `references/directory-structure.md`

## 常见问题

**Q: 如何添加插件功能？**
在 `plugin.json` 的 `features` 数组中添加功能配置。

**Q: 发布失败怎么办？**
检查：在项目根目录执行、已 git init、plugin.json 存在且格式正确、网络正常。

**Q: 如何更新已发布的插件？**
修改代码、git commit、再次 `ztools publish`。

**Q: 审核者改了代码怎么办？**
执行 `ztools pull-contributions` 三方合并回本地。