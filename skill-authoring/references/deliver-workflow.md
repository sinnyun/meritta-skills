# Deliver Skill Workflow

## 前置条件

- Static Validation PASS
- Review 已完成（至少 1 轮）
- 无 P0 问题（P1 已修复或有明确理由）
- 或已达到 MAX_REVIEW_ROUNDS 且无 P0 问题

## Step 1: Final Validation

运行最终校验：

```bash
python "$SKILL_ROOT/scripts/validate_skill.py" --skill-path "<目标Skill路径>"
```

如果 FAIL，返回 REVISE 修复。如果 PASS，继续。

## Step 2: 清理临时文件

删除以下内容（保留 `.review/` 目录，用于后续定位问题）：
- `__pycache__/` 目录
- `*.pyc` 文件
- `.DS_Store` 文件
- `*.tmp` 文件
- `node_modules/` 目录（如果有）

```bash
find "<目标Skill路径>" -type d -name "__pycache__" -exec rm -rf {} +
find "<目标Skill路径>" -name "*.pyc" -delete
find "<目标Skill路径>" -name ".DS_Store" -delete
find "<目标Skill路径>" -name "*.tmp" -delete
```

## Step 3: 检查 TODO 残留

搜索 Skill 目录中是否还有 TODO / 占位符：

```bash
grep -rn "TODO\|FIXME\|PLACEHOLDER\|<your-\|<TODO>" "<目标Skill路径>"
```

如果有残留，清理或替换为实际内容。

## Step 4: 删除空目录

删除没有实际内容的空目录：

```bash
find "<目标Skill路径>" -type d -empty -delete
```

但保留 Skill 根目录和必要的子目录结构。

## Step 5: 检查最终目录

确认最终目录结构合理：
- SKILL.md 存在且合法
- 只保留有实际内容的目录
- 没有临时文件和残留

## Step 6: 打包

运行打包脚本：

```bash
python "$SKILL_ROOT/scripts/package_skill.py" \
  --skill-path "<目标Skill路径>" \
  --skill-root "$SKILL_ROOT"
```

**ZIP 在当前工作目录下生成**，文件名为 `<skill-name>.zip`。

脚本会：
- 自动 Validation（FAIL 禁止打包）
- 排除临时文件和缓存
- 在 cwd 下输出 `<skill-name>.zip`

## Step 7: 安装 Skill

运行安装脚本，将 Skill 安装到 Agent 的全局 skills 目录：

```bash
python "$SKILL_ROOT/scripts/install_skill.py" \
  --skill-zip "./<skill-name>.zip" \
  --target "<Agent的skills目录>"
```

**`--target` 参数必填**，Agent 需要知道自己的全局 skills 目录位置并传入。安装完成后，Skill 就可以被 Agent 使用了。

## Step 8: 汇报结果

向用户报告：

```markdown
## Skill 交付报告

### 基本信息
- Skill 名称：<name>
- 目录路径：<path>
- 打包文件：<zip-path>
- 安装位置：<install-path>（如果已安装）

### 创建过程
- 创建轮次：<N>
- Review 轮次：<N>
- 最终评分：<score> / 100
- Verdict：<PASS / PASS_WITH_FIXES>

### 修改的文件
1. <file> — <修改摘要>
2. ...

### 评审发现的问题
- P0: <数量>（已修复 <数量>）
- P1: <数量>（已修复 <数量>）
- P2: <数量>（已修复 <数量>，未修复 <数量>）
- Suggestion: <数量>

### 剩余问题
1. <问题描述> — <不修复理由>
2. ...

### 限制说明
- <如果有已知限制>
```
