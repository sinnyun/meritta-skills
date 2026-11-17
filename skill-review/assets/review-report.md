# Skill Review

## Overall Score

{{SCORE}} / 100

## Ship Decision

> Would a competent human engineer ship this?

{{SHIP_DECISION}}

- **Blocking reason**: {{如果 NO，说明阻塞原因}}

## Verdict

{{VERDICT}}

## Hard Gates

- 核心用户意图理解正确: {{PASS/FAIL}}
- 核心 Capability 真实实现: {{PASS/FAIL}}
- 核心能力不依赖伪造数据: {{PASS/FAIL}}
- 依赖的 Tool/API 真实存在: {{PASS/FAIL}}
- 核心 Test Oracle 有效: {{PASS/FAIL}}
- 目标环境可运行核心路径: {{PASS/FAIL}}
- 核心输出不具有误导性: {{PASS/FAIL}}
- 无 P0 Failure Mode: {{PASS/FAIL}}

## Score Breakdown

| 维度 | 得分 | 满分 | 说明 |
|------|------|------|------|
| Intent & Requirement Fidelity | {{N}} | 15 | {{comment}} |
| Capability Authenticity | {{N}} | 20 | {{comment}} |
| Evidence & Test Validity | {{N}} | 15 | {{comment}} |
| Real-world Robustness | {{N}} | 15 | {{comment}} |
| Product / Human Sanity | {{N}} | 15 | {{comment}} |
| Dependency & Environment Fitness | {{N}} | 10 | {{comment}} |
| Operational & Maintainability | {{N}} | 5 | {{comment}} |
| Structure / Context Efficiency | {{N}} | 5 | {{comment}} |

## Intent & Capability

- Original user intent: {{用户真正想要什么}}
- Claimed capabilities: {{Skill 声称的核心能力}}
- Claim vs Implementation boundary: {{能力声明与实际实现的边界是否一致}}
- Intent fidelity verdict: {{是否实现了正确的问题}}

## Evidence & Test Validity

- Evidence sources: {{每个能力的支撑证据}}
- Test Oracle review: {{测试预期结果本身是否可靠}}
- Creator-Test Collusion risk: {{实现和测试是否基于同一错误假设}}
- Independent challenge result: {{Reviewer 独立挑战用例的结果}}
- Unsupported capabilities: {{缺乏可信证据的能力}}

## Dependency & Environment

- Required dependencies: {{Skill 依赖的 Tool/API/数据/环境}}
- Target environment fitness: {{目标环境是否真实具备这些依赖}}
- Dependency resolution quality: {{Creator 是否自主解决了合理的能力缺口}}
- Fabricated production data: {{是否发现 Creator 编造的生产数据，无则写 None}}
- Mock/runtime isolation: {{Mock 数据与生产路径是否隔离}}
- Freshness requirements: {{动态数据的 Freshness 要求}}

## Real-world Robustness

- Happy Path overfit risk: {{是否只处理理想输入}}
- Edge case coverage: {{边界场景覆盖情况}}
- Scale behavior: {{真实规模下的表现}}
- Failure recovery: {{依赖失败时的降级策略}}
- Fake fallback detected: {{是否发现异常时伪造成功结果}}

## Product / Human Sanity

- Human sanity check: {{如果我是目标用户，结果有用吗}}
- Product plausibility: {{有没有技术上成立但现实中荒谬的行为}}
- Missing expert factor: {{是否遗漏了人类专家显然会考虑的重要因素}}
- Simpler alternative: {{有没有明显更简单可靠的实现}}

## Operational Fitness

- Performance assessment: {{性能、延迟是否合理}}
- Cost assessment: {{API 调用 / 模型调用成本是否合理}}
- Resource consumption: {{资源消耗是否合理}}

## Failure Mode Scan

- Scanned failure modes: {{本次扫描了哪些 Failure Modes}}
- Matched failure modes: {{匹配到的 Failure Modes，无则写 None}}

## P0 Issues

<!-- 阻塞交付的问题，必须修复 -->

1. **[P0]** {{问题描述}}
   - 文件：{{file}}
   - Failure Mode: {{FM-XXX 或 N/A}}
   - 建议：{{修改建议}}

## P1 Issues

<!-- 重要问题，原则上必须修复 -->

1. **[P1]** {{问题描述}}
   - 文件：{{file}}
   - Failure Mode: {{FM-XXX 或 N/A}}
   - 建议：{{修改建议}}

## P2 Issues

<!-- 普通质量问题，视情况修复 -->

1. **[P2]** {{问题描述}}
   - 文件：{{file}}
   - Failure Mode: {{FM-XXX 或 N/A}}
   - 建议：{{修改建议}}

## Suggestions

<!-- 锦上添花，不影响当前交付 -->

1. **[Suggestion]** {{建议描述}}

## Recommended Changes

1. {{修改项}}
2. {{修改项}}
