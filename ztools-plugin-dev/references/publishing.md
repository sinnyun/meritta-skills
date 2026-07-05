# 发布与协作流程参考

## 整体模型

ZTools 插件中心采用 **fork + PR** 模式：

- 中心仓库：`ZToolsCenter/ZTools-plugins`
- 每位作者在自己 GitHub 账号下 fork 一份
- 每次发布走「复制工作目录 → 在 fork 的 `plugin/<插件 ID>` 分支上 commit → push → 开 PR」

`ztools-plugin-cli` 自动化了这套流程，并提供以下保障：

- **增量发布**：每次发布只 fast-forward 追加一个 commit，不 force-push
- **持久化缓存**：fork 在本地 clone 一次（`~/.config/ztools/ZTools-plugins/`），后续发布复用
- **正确的 Add/Update 判定**：基于上游 main 的实际状态而非分支存在性
- **协作友好**：审核者直推后通过 `pull-contributions` 三方合并回本地

## 发布命令详解

### ztools publish 完整流程

1. 校验 plugin.json + git 仓库 + 工作区干净
2. CHANGELOG 检查（缺失当前版本节时交互式录入）
3. GitHub OAuth 认证（首次会引导浏览器授权）
4. Fork 中心仓库（不存在则自动创建）
5. ensureForkClone：clone 或 fetch 本地 fork 缓存
6. syncForkMain：调用 merge-upstream API 同步 fork main
7. pluginExistsUpstream：探测上游 `plugins/<id>/` 目录决定 Add/Update
8. prepareBranch：在 fork 分支上 checkout（已存在则复用，否则基于 upstream/main 新建）
9. copyPluginFiles：把工作目录复制进 `plugins/<id>/`，自动忽略 node_modules、dist 等
10. commitPluginChanges：组装智能 commit message 并提交（无变更则跳过）
11. pushPluginBranch：普通 push，不 force（first push 用 -u）
12. createPullRequest：复用已有 open PR 或开 draft PR
13. tagLastPublishLocally：在你本地仓库 HEAD 打 `ztools-last-publish` 标签

### 智能 commit / PR 标题

CLI 会读取你本地 `ztools-last-publish..HEAD` 之间的 commit subjects：

| subjects 数量 | PR 标题 | fork 端 commit message |
|--------------|---------|----------------------|
| 0 | `Add/Update plugin <名称> v<版本>` | 同 PR 标题 |
| 1 | `Add/Update plugin <名称> v<版本>` | 直接用你的 commit subject 原文 |
| ≥2 | `Add/Update plugin <名称> v<版本>` | fallback 标题 + bullet list 列出所有 subject |

### Add vs Update 自动判定

基于上游 main 的实际状态：`plugins/<id>/` 目录存在 → Update，不存在 → Add。

### 增量发布

每次 `ztools publish` 都是增量追加：
- 远端分支保留旧 commit，只 fast-forward 追加一个新 commit
- 同一个 PR 自动复用，链接不变
- 不会 force-push，旧的 review 评论上下文不会丢失

## ztools pull-contributions

### 工作机制（三方合并）

把审核者的 commit 三方合并回你本地的 fork 仓库。

### 使用场景

审核者直接在 PR 分支上改了代码后，需要执行此命令拉取审核者的改动。

### 冲突时怎么办

如果出现冲突，需要手动解决冲突后再次执行。

## 故障排查

### 推送被拒：refusing to allow an OAuth App to ...

检查 GitHub OAuth token 的权限，确保包含 workflow scope。

### merge-upstream 422 错误

可能是 fork 与上游差异过大，尝试删除 fork 重新创建。

### 工作区有未提交改动

确保在执行 `ztools publish` 前，所有改动都已 commit。

### 想看 CLI 的本地缓存仓库

查看 `~/.config/ztools/ZTools-plugins/` 目录。

### 想完全重置

删除本地 fork 缓存目录，重新执行 publish。

## 快速发布流程

### 前置条件

1. 项目包含 `plugin.json` 文件
2. 已初始化 Git 仓库（`git init`）
3. 至少有一次提交记录
4. 工作区干净

### 发布命令

```bash
# 安装 CLI 工具
npm install -g @ztools-center/plugin-cli

# 初始化 Git 仓库（如果还没有）
git init
git add .
git commit -m "Initial commit"

# 发布
ztools publish
```

### 发布成功后

CLI 会输出 PR 链接，你需要：

1. 上传截图 / 演示 GIF
2. 勾选自检清单
3. 把 PR 从 Draft 切到 "Ready for review"

### 更新已发布的插件

修改代码、`git commit`，然后再次执行 `ztools publish`。CLI 会自动在同一个 PR 上 fast-forward 追加一个新 commit。