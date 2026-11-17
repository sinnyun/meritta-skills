# Skill 规范

## Skill 基本结构

```text
skill-name/
├── SKILL.md          # 必须，核心入口
├── scripts/          # 可选，确定性操作脚本
├── references/       # 可选，详细知识和规则
└── assets/           # 可选，模板和素材
```

supporting directories 应按实际需求创建，不应机械全部生成。

## SKILL.md

### Frontmatter

```yaml
---
name: example-name
description: |
  一句话说清楚 Skill 做什么。
  什么场景应该触发。
  触发词：关键词1、关键词2。
allowed-tools: Bash(node:*) Bash(npm:*)
---
```

### 字段要求

| 字段 | 必填 | 要求 |
|------|------|------|
| name | 是 | lowercase, kebab-case, 简短明确 |
| description | 是 | 同时描述"做什么"和"何时触发"，包含触发词 |
| allowed-tools | 否 | 列出需要的工具权限，不填则继承默认 |

### name 规则

- 全小写
- 单词间用连字符 `-` 分隔（kebab-case）
- 不含下划线、空格、大写字母
- 简短，通常 2-4 个单词
- 能准确表达 Skill 的功能

示例：
- `portrait-cutout` — 人像抠图
- `web-style-transfer` — 网页风格迁移
- `poster-generation` — 海报生成

### description 规则

必须包含：
1. **做什么**：Skill 的核心功能
2. **何时触发**：什么场景下应该使用
3. **触发词**：用户可能使用的关键词

示例：
```yaml
description: |
  分析参考网页的视觉设计语言，提取 Design Tokens 和组件视觉规则，将这些视觉语言迁移到用户当前前端项目。
  触发词：风格迁移、style transfer、参考网站风格、视觉风格迁移。
```

### Skill body 重点描述

- **Workflow**：核心步骤，每步有明确输入输出和转换条件
- **Tool 使用规则**：何时用脚本、何时用模型判断
- **Resource 导航**：指向 references / scripts / assets
- **重要约束**：安全限制、边界条件、禁止操作

**不要**重复大量基础常识（如"什么是 CSS"）。
**不要**把所有知识和边界情况全部写进 SKILL.md。

## scripts/ 规范

何时使用 Script 见 `$SKILL_ROOT/references/design-guidelines.md` 的 **Script vs Model 判断** 章节。

### Script 要求

- 有明确的输入输出
- 可独立运行测试
- 包含错误处理（参数校验、异常捕获）
- 不依赖未安装的包（或明确声明依赖）
- 有使用说明（注释或 --help）
- 输出明确的结果（成功/失败 + 原因）
- 开发脚本时，遵循 `$SKILL_ROOT/references/script-design-principles.md`

### 脚本语言

- 优先 Python（跨平台、标准库丰富）
- 或 Node.js（如果 Skill 面向前端项目）
- 或 Shell（简单操作）

## references/ 规范

何时使用 Reference 见 `$SKILL_ROOT/references/design-guidelines.md` 的 **内容分配决策** 章节。

### Reference 要求

- 每个文件聚焦一个主题
- 文件名清晰表达内容
- 避免深层嵌套（最多一级子目录）
- 内容可被 SKILL.md 导航引用

## assets/ 规范

何时使用 Asset 见 `$SKILL_ROOT/references/design-guidelines.md` 的 **内容分配决策** 章节。

### Asset 要求

- 二进制文件只提供 metadata，不粗暴展开
- 模板文件使用占位符标记可替换部分
- 文件名清晰
