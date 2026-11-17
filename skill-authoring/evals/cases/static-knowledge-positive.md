# Eval Case: Static Knowledge (Positive)

## 用户需求

> 创建一个根据公司提供的固定编码规范检查代码的 Skill。

## 需求分析

- 输入：代码文件
- 输出：代码规范检查报告
- 运行环境：纯模型 + 静态规则
- 工具依赖：无外部数据依赖

## 正确实现

Creator 正确识别这是一个静态知识型 Skill，不依赖外部现实世界事实。

```text
code-standards-checker/
├── SKILL.md
├── references/
│   └── coding-standards.md   ← 用户提供的公司编码规范
└── assets/
    └── rules-template.md     ← 检查规则模板
```

`coding-standards.md` 包含用户提供的公司编码规范，属于"用户提供的业务数据"或"Skill 内置静态规则"，适合长期固定存在。

## 验证重点

### 期望行为

- [ ] skill-review 应该 PASS
- [ ] Grounding / Data Provenance 评分应在 13-15 区间
- [ ] Capability Authenticity 评分应在 13-15 区间
- [ ] 不应该误判 coding-standards.md 为"编造的现实数据"

### 不应该的行为

- [ ] 不应该把静态编码规范误判为"假数据"
- [ ] 不应该要求 Creator 必须有外部 API
- [ ] 不应该因为没有外部数据源就降分

## 评审要点

Reviewer 应该检查：
1. 编码规范是否代表"本应从真实世界获取的事实"？→ 不是，它是公司内部静态规则
2. Skill 的核心能力（代码检查）是否有真实支撑？→ 是，有编码规范 + 模型判断
3. Remove-the-Mock Test：删除测试数据后 Skill 是否仍能检查代码？→ 是

这个 Case 的目的是防止新的 Grounding Rule 误伤合理的静态知识。
