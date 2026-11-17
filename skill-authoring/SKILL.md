---
name: skill-authoring
description: |-
  Skill 开发、修改、校验和交付能力。
  当 Skill Engineer 需要创建、修改、校验或交付 Skill 时加载此 Skill。
  触发词：创建 Skill、修改 Skill、校验 Skill、打包 Skill、交付 Skill。
allowed-tools: Bash(python:*) Bash(pip:*) read write edit glob grep
---

# skill-authoring — Skill 开发能力

> 本 Skill 是 Skill Engineer 的开发能力载体，不是一个独立的专家。

## 职责

```text
Understand User Intent
→ Identify Natural Usage Scenarios
→ Define Capability Claims & Boundaries
→ Identify Relevant Risks / Dependencies
→ Conditional Deep Checks
→ Design Minimum Sufficient Architecture
→ Define Evidence Plan
→ Implement Skill
→ Run Static Validation
→ Run Creator Tests
→ Check Capability Claims Against Evidence
→ Prepare Independent Review
```

## 路径

`$SKILL_ROOT` 由 Skill Engineer Agent 在加载本 Skill 前已解析（见 agent.md 路径解析章节）。后续所有脚本和参考文件引用均基于此路径。

## 核心原则

1. **不要把普通 Prompt 包装成 Skill** — 模型擅长的语义任务用 instruction；重复确定性操作用 scripts；大量领域知识用 references；模板素材用 assets。没有必要的目录不创建

2. **Progressive Loading** — SKILL.md 精简，只含核心工作流和资源导航。详细知识和复杂规则放 references

3. **Static Validation 和 Semantic Review 分离** — 脚本检查确定性问题，Semantic Review 由 General Subtask + skill-review 执行

4. **Skill 可以创造算法，但不能创造现实世界事实** — Skill 可以创造逻辑、流程和规则，但禁止为了让能力看起来可用而伪造现实世界实体、事实或生产数据。详见 `design-guidelines.md` 的 Data Dependency Analysis 和 Hard Rule 章节

5. **Claim-Evidence 思维** — 每个核心能力声明必须有可信证据支撑。Creator 自构造的 Mock / 测试不算充分证据。在开发前就应该知道最后用什么证据证明 Skill 真的完成了任务

6. **Right-sized Engineering** — 使用能够可靠完成任务的最小充分复杂度。避免 Overengineering 和 Underengineering

## 工作流

### 创建 Skill

阅读 `$SKILL_ROOT/references/create-workflow.md`，按 12 步流程执行：

1. **Understand User Intent** — 理解用户真实意图，不只看字面表达
2. **Identify Natural Usage Scenarios** — 轻量识别自然使用维度，防止无意识缩窄能力范围
3. **Define Capability Claims & Boundaries** — 明确 Skill 声称拥有哪些核心能力及边界
4. **Identify Relevant Risks / Dependencies** — 轻量判断当前 Skill 存在哪些实际风险
5. **Conditional Deep Checks** — 只深入检查实际存在的风险（External Facts / Tool / Capability Gap / Integration）
6. **Design Minimum Sufficient Architecture** — 判断需要 scripts / references / assets 中的哪些
7. **Define Evidence Plan** — 思考最后用什么证据证明 Skill 真的完成了任务
8. **Implement Skill** — 初始化目录、编写 SKILL.md 和 supporting resources、清理模板残留
9. **Run Static Validation** — 运行 `validate_skill.py`
10. **Run Creator Tests** — 创建测试，覆盖主要自然使用场景，Mock 数据与生产数据严格隔离
11. **Check Capability Claims Against Evidence** — Claim-Evidence 对齐检查，包含自然使用场景覆盖检查
12. **Prepare Independent Review** — 准备 Review Package，进入 REVIEW 状态

### 修改 Skill

阅读 `$SKILL_ROOT/references/revise-workflow.md`，按工作流执行：

- P0 → 必须修复
- P1 → 原则上必须修复
- P2 → 根据收益与复杂度判断
- Suggestion → 可不修改

### 交付 Skill

阅读 `$SKILL_ROOT/references/deliver-workflow.md`，按工作流执行：

1. Final Validation
2. 清理临时文件
3. 打包
4. 安装到 Agent 的全局 skills 目录

## 脚本

| 脚本 | 用途 | 用法 |
|------|------|------|
| `init_skill.py` | 从模板初始化 Skill 目录（在当前工作目录下创建） | `python "$SKILL_ROOT/scripts/init_skill.py" --name <name> --skill-root "$SKILL_ROOT"` |
| `validate_skill.py` | 静态校验 | `python "$SKILL_ROOT/scripts/validate_skill.py" --skill-path <path>` |
| `prepare_review.py` | 生成隔离 Review Package | `python "$SKILL_ROOT/scripts/prepare_review.py" --skill-path <path> --requirement "<需求>" --skill-root "$SKILL_ROOT" --output <path>` |
| `package_skill.py` | 最终打包（在当前工作目录下生成 zip） | `python "$SKILL_ROOT/scripts/package_skill.py" --skill-path <path> --skill-root "$SKILL_ROOT"` |
| `install_skill.py` | 安装 Skill 到目标目录 | `python "$SKILL_ROOT/scripts/install_skill.py" --skill-zip <zip> --target <path>` |

## 资源导航

| 资源 | 路径 | 用途 |
|------|------|------|
| 创建工作流 | `$SKILL_ROOT/references/create-workflow.md` | Skill 创建 12 步全流程 |
| 修改工作流 | `$SKILL_ROOT/references/revise-workflow.md` | 根据评审报告修改 |
| 交付工作流 | `$SKILL_ROOT/references/deliver-workflow.md` | 最终交付流程 |
| Skill 规范 | `$SKILL_ROOT/references/skill-spec.md` | Skill 目录和文件规范 |
| 设计指南 | `$SKILL_ROOT/references/design-guidelines.md` | 何时用 Skill / Scenario Coverage / 内容分配 / Right-sized Engineering / Conditional Risk Guidance |
| Web Access 指导 | `$SKILL_ROOT/references/web-access-guidance.md` | Web / Browser / Network 工具选型（条件加载） |
| Skill 模板 | `$SKILL_ROOT/assets/skill-template/SKILL.md` | Skill 初始模板 |
