# 快速开始参考

## 插件应用是什么

Node.js 本地原生能力 + Web 前端网页。（本地软件能做到的，理论上它也能做到）

ZTools 插件应用结合了 Web 前端技术的灵活性和 Node.js 的强大本地能力，让你可以：

- 使用 HTML、CSS、JavaScript 构建美观的用户界面
- 通过 Node.js 访问系统原生能力（文件系统、网络、进程等）
- 使用丰富的 ZTools API（通知、剪贴板、窗口管理等）
- 支持 Vue、React 等现代前端框架
- 跨平台运行（Windows、macOS、Linux）

## 环境要求

### 必需工具

| 工具 | 版本要求 | 说明 |
|------|---------|------|
| ZTools | 最新版 | 下载地址：https://ztoolscenter.github.io/ZTools-doc/ |
| Node.js | >= 16.0.0 | 下载地址：https://nodejs.org/ |
| 代码编辑器 | - | 推荐 VSCode 或 WebStorm |
| Git | - | 用于版本控制和插件发布 |

### 基础知识

- 熟悉 JavaScript - 基础开发语言
- 熟悉 HTML 和 CSS - 掌握基础的界面构建能力
- 了解 Node.js - 接入强大的本地原生能力

### 进阶

可借助 Vue 或者 React 等主流的 Web 前端开发框架，增强你的应用界面。

## 创建第一个插件

### 步骤 1: 安装 CLI 工具

```bash
npm install -g @ztools-center/plugin-cli
# 或
pnpm add -g @ztools-center/plugin-cli
```

### 步骤 2: 创建插件项目

```bash
ztools create my-first-plugin
```

这个命令会引导你完成以下步骤：
- 选择模板（Vue + TypeScript + Vite / React + TypeScript + Vite / Preload Only）
- 输入插件信息（Plugin name、Plugin title、Plugin description、Author）

### 步骤 3: 进入项目目录

```bash
cd my-first-plugin
```

### 步骤 4: 安装依赖

```bash
npm install
# 或
pnpm install
```

### 步骤 5: 开发插件

```bash
npm run dev
# 或
pnpm run dev
```

根据你选择的模板：
- **Vue/React 模板**：在 `src/` 目录下开发 UI 组件
- **Preload Only 模板**：在 `src/` 目录下编写 Preload 脚本

### 步骤 6: 构建插件

```bash
npm run build
# 或
pnpm run build
```

构建产物会输出到 `dist/` 目录。

## 发布插件

### 前置条件

- 项目包含 `plugin.json` 文件（CLI 会自动生成）
- 已初始化 Git 仓库（`git init`）
- 至少有一次提交记录
- 工作区干净（没有未提交的改动）

### 发布命令

```bash
ztools publish
```

首次执行 `ztools publish` 时，CLI 会自动完成：
1. GitHub OAuth 认证（通过 Device Flow 引导你在浏览器授权一次）
2. Fork 中心仓库（自动在你账号下 fork `ZToolsCenter/ZTools-plugins`）
3. 同步 fork main
4. 判定 Add / Update
5. 复制工作目录文件
6. 生成 commit + 推送分支
7. 创建 Draft Pull Request

### 发布成功后

CLI 会输出 PR 链接，你需要：

1. 上传截图 / 演示 GIF（直接拖图到 PR description 编辑框）
2. 勾选自检清单（PR description 里有 5 项 checkbox）
3. 把 PR 从 Draft 切到 "Ready for review"（右下角按钮）

## 下一步

- 了解插件应用目录结构
- 学习 plugin.json 配置
- 查看插件 API 文档
- 阅读 preload.js 说明
- 学习发布与协作流程