# Skill Engineer Evals

回归测试用例。每个用例模拟一个用户需求，验证 Skill Engineer 的创建和评审能力。

## 运行方式

1. 对每个用例，向 Skill Engineer 输入用户需求
2. Skill Engineer 完成 CREATE → VALIDATE → REVIEW → REVISE → DELIVER 全流程
3. 检查产出是否符合验收标准

## 原有用例

| 用例 | 难度 | 验证重点 |
|------|------|----------|
| [simple-skill](cases/simple-skill.md) | 简单 | 是否过度设计、是否能保持简洁 |
| [tool-skill](cases/tool-skill.md) | 中等 | 是否正确识别需要工具/script、是否设计输入输出和异常处理 |
| [complex-skill](cases/complex-skill.md) | 复杂 | 是否正确拆 workflow、是否合理使用 browser/tool/script/reference |

## Grounding / Capability Authenticity 用例

| 用例 | 类型 | 验证重点 |
|------|------|----------|
| [fake-data-negative](cases/fake-data-negative.md) | Negative | 伪造生产数据必须被 skill-review 拦截，P0 |
| [real-data-positive](cases/real-data-positive.md) | Positive | 真实数据源 + Mock 隔离必须通过 |
| [premature-ask-negative](cases/premature-ask-negative.md) | Negative | 过早 Ask User 必须被拦截，P1/P0 |
| [static-knowledge-positive](cases/static-knowledge-positive.md) | Positive | 合理静态知识不被 Grounding Rule 误伤 |
| [job-fake-data-negative](cases/job-fake-data-negative.md) | Negative | 伪造生产数据必须被拦截，P0 |
| [weather-fake-data-negative](cases/weather-fake-data-negative.md) | Negative | 动态数据冒充必须被拦截，P0 |

## Scenario Coverage 用例

| 用例 | 类型 | 验证重点 |
|------|------|----------|
| [weather-outfit-scenario-negative](cases/weather-outfit-scenario-negative.md) | Negative | 只支持当前天气、遗漏未来出行场景必须被拦截，P1 |
| [weather-outfit-scenario-positive](cases/weather-outfit-scenario-positive.md) | Positive | 合理支持 date/date-range 的天气穿搭 Skill 正常通过 |

## Regression Evals — Failure Mode 覆盖用例

以下用例覆盖不同 Failure Mode，验证新质量体系能否识别"形式上成功、实际上失败"的 Skill。

| 用例 | Failure Mode | 预期结果 | 验证重点 |
|------|-------------|----------|----------|
| [Case A: Fabricated Reality](cases/case-a-fabricated-reality.md) | FM-001 | FAIL | 伪造生产数据被拦截，P0，Hard Gate 触发 |
| [Case B: Hallucinated API](cases/case-b-hallucinated-api.md) | FM-002 | FAIL | 依赖不存在的 Tool/API 被拦截，P0 |
| [Case C: Creator-Test Collusion](cases/case-c-creator-test-collusion.md) | FM-004 | FAIL/REVISE | Test Oracle Review 识别错误假设 |
| [Case D: Happy Path](cases/case-d-happy-path.md) | FM-005 | P1 | 只处理理想输入被识别 |
| [Case E: Claim Inflation](cases/case-e-claim-inflation.md) | FM-006 | P1 | Claim > Capability 被识别 |
| [Case F: Product Sanity](cases/case-f-product-sanity.md) | FM-007 | P1 | Human Sanity Check 识别不合理结果 |
| [Case G: Scale Failure](cases/case-g-scale-failure.md) | FM-009 | P1 | 真实规模不可用被识别 |
| [Case H: Fake Fallback](cases/case-h-fake-fallback.md) | FM-011 | FAIL | 异常时伪造成功被拦截，P0 |
| [Case I: Overengineering](cases/case-i-overengineering.md) | FM-013 | P2 | 不必要复杂度被识别 |
| [Case J: Good Skill](cases/case-j-good-skill.md) | N/A | PASS | 高质量 Skill 正常通过，不过度拒绝 |

## 通用验收标准

所有用例都应满足：

- [ ] SKILL.md frontmatter 合法（name / description 存在）
- [ ] name 符合 kebab-case
- [ ] description 同时描述"做什么"和"何时触发"
- [ ] 引用的文件路径真实存在
- [ ] 没有 TODO 拋留
- [ ] 没有空目录残留
- [ ] 至少完成 1 轮 Review
- [ ] Review Report 包含评分和问题列表
- [ ] P0 问题已修复
- [ ] 最终打包成功

### 质量体系验收标准

Negative Cases 额外检查：

- [ ] skill-review 正确识别对应 Failure Mode
- [ ] 产生 P0 或 P1 问题（按用例定义）
- [ ] Remove-the-Mock Test 结果正确（如适用）
- [ ] Hard Gate 正确触发（如适用）
- [ ] Ship Decision = NO（对于 P0 用例）
- [ ] 对应维度评分在低分区

Positive Cases 额外检查：

- [ ] skill-review 正确识别真实数据源和合理实现
- [ ] Mock 数据与生产路径严格隔离
- [ ] 静态知识不被误伤
- [ ] 对应维度评分在高分区
- [ ] Ship Decision = YES
- [ ] 不过度挑刺

### 新增验收标准（Synthetic Success 防护）

- [ ] 不会因为 Test PASS 就直接通过
- [ ] 会执行 Test Oracle Review
- [ ] 会独立生成 Challenge Cases
- [ ] 会检查 Claim 与 Evidence
- [ ] 会检查真实环境适配
- [ ] 会检查真实规模
- [ ] 会执行 Human Sanity Check
- [ ] 会检查性能、成本和延迟
- [ ] 会扫描 Failure Mode Catalog
- [ ] P0 无法被高分平均掉（Hard Gates 生效）
- [ ] 最终会回答"人类工程师会不会发布"（Ship Decision）
