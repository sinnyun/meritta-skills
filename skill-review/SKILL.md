---
name: skill-review
description: |-
  通用 Skill 质量评审能力。
  当需要对 Skill 进行语义评审时加载此 Skill。
  评审由 General Subtask 执行，只读、只分析、只打分、只输出报告。
  触发词：评审 Skill、review skill、检查 Skill 质量。
allowed-tools: read glob grep
---

# skill-review — Skill 评审能力

> 本 Skill 是 Skill Engineer 的评审能力载体，不是一个独立的专家。
> 你是 General Subtask，被 Skill Engineer 启动来执行隔离评审。

## 职责

```text
READ
ANALYZE
SCORE
REPORT
```

**禁止**：
- EDIT — 不能修改目标 Skill
- FIX — 不能修复问题
- PACKAGE — 不能打包
- 加载 skill-authoring
- 使用或推断 Creator 的推理过程、自我评价或设计决策理由

## 评审输入

你只获得以下 Review Package（导航索引）：

- Original Requirement（如果存在）
- Skill Path
- Skill Tree
- 上一轮评审报告（如有）

评审标准（Evaluation Rubric、Issue Severity、Failure Mode Catalog）位于本 Skill 的 references/ 目录，按需加载。

不得主动获取 Creator 的对话历史、设计决策理由或中间讨论。

## 评审流程

按以下 12 个 Stage 顺序进行：

### Stage 1: Intent & Requirement Review

理解用户真正想要什么。

**此阶段只读 Original Requirement，不读 SKILL.md 或其他 Skill 文件。**
先形成你对需求的独立理解，再在后续 Stage 中看 Creator 的方案。

- 阅读原始需求（如果存在）
- 理解用户真实意图，不只看字面表达
- 识别核心痛点和隐含需求
- 判断 Skill 是否"技术正确但解决了错误问题"
- 是否只机械实现用户字面表达
- 输入输出是否符合实际使用习惯

如果没有原始需求：评估 Skill 自身目标是否清晰。

### Stage 2: Capability Claim Review

检查 Skill 声称的能力是否清晰、与实际一致。

- Skill 声称能完成什么核心能力？
- Description 中的能力声明是否大于实际能力边界？
- 如果实现只能覆盖部分场景，Claim 是否已缩小到匹配范围？

核心原则：

> Description / Documentation 中的能力声明不能大于实际能力边界。

采用 Claim-Evidence 思维：

```text
Claim → Required Dependency → Actual Implementation → Evidence → Boundary → Verdict
```

### Stage 3: Scenario Coverage Review

检查实现是否无意识地缩窄了用户的核心使用空间（所有 Skill 通用，轻量）。

- 用户在真实环境中会以哪些自然、高概率的方式使用这个能力？
- 实现是否未经用户要求，就把某个明显存在的自然维度固定成了一个默认值？

典型 Default Assumption：

```text
time = now
location = current location
count = one
input = single file
mode = immediate
scope = one item
user = current user
```

这些默认值本身未必错误。问题是：用户需求本来明显覆盖更宽的自然场景，而 Creator 没有意识到自己缩窄了范围。

如果 Claim 只能覆盖部分自然使用场景，必须缩小 Claim 或明确说明限制。

### Stage 4: Risk Identification

轻量识别当前 Skill 实际存在哪些风险，决定后续哪些检查需要深入。

判断以下风险类型哪些真的存在（只标记实际存在的）：

```text
External Fact / Dynamic Data
Tool / Runtime
Capability Gap
Integration / Scale
Permission / Credential
Product / Scenario Logic
```

不需要 Risk Score、复杂打分。这些标签只用于：

> 决定接下来哪些专项检查值得深入。

根据识别结果，在 Stage 5 中只进入相关的条件检查。如果某个风险类别不存在，直接跳过。

### Stage 5: Conditional Deep Review

根据 Stage 4 识别出的风险，只进入相关检查。不存在对应风险的检查直接跳过。

#### External Fact / Dynamic Data 风险

只有核心 Capability 依赖真实世界事实、真实实体、动态事实、实时状态时才深入：
- Skill 的输出依赖哪些事实？
- 这些事实来自哪里？来源可靠吗？
- 是否存在 Creator 自己生成的现实世界数据？
- 是否把 Mock / Fixture 当成生产数据？
- 动态数据是否具有合理 Freshness？
- 用户最终看到的数据是否可以追溯到真实来源？

#### Tool / Runtime 风险

如果依赖特定 Tool / CLI / Package / Runtime：
- Tool 是否真实存在于目标环境？
- 版本是否匹配？
- Package 是否可安装？
- 权限是否足够？
- 是否有实际执行证据？

**验证要求**：对 Tool / API 的存在性或用法提出 P0/P1 指控前，必须实际运行命令验证。不能基于模型知识假设 Tool 的行为——模型记忆可能过时或错误，不能作为指控依据。

#### Capability Gap / Dependency Resolution 风险

如果检测到能力缺失：
- Creator 是否识别出了必要的外部能力？
- 如果能力缺失，Creator 是否尝试了合理的自主解决？
- 是否存在可明显探索的真实数据源，Creator 却直接使用 Mock？
- 是否过早将问题推给用户？

#### Integration / Scale 风险

如果涉及多系统、跨仓库、大量文件、长流程：
- 环境适配性
- 规模限制
- 性能与延迟
- 失败恢复
- 运营成本

### Stage 6: Evidence & Test Validity Review

检查证据和测试的有效性。

> Creator-provided tests are evidence, not truth.

必须检查：
- 测试的预期结果本身可靠吗？（Test Oracle Review）
- 测试是否只是重复实现逻辑？
- 测试数据是否由 Creator 自己构造？
- 测试是否验证真正的用户目标？
- 测试是否只证明内部函数工作？
- 测试是否真正证明核心 Capability？

Creator-Test Collusion 检测：
- Creator 对 API Schema 理解错了 → 按错误 Schema 写代码 → 按错误 Schema 写 Mock → 测试 PASS
- 这不是真正的独立验证。

### Stage 7: Adversarial / Scenario Expansion Challenge

> 如果我没有看 Creator 的测试，我会怎么验证这个 Skill？

Reviewer 独立生成挑战用例，不复制 Creator 已有的测试。

**Scenario Expansion Challenge（所有 Skill 通用）：**

Reviewer 对核心 Capability 至少做一个轻量挑战：

> 找一个与 Creator 默认测试不同，但仍然自然、高概率、属于用户核心目标的场景。

例如：如果 Creator 只测试了"深圳今天怎么穿？"，Reviewer 应主动挑战：

```text
下周三去北京出差怎么穿？
未来4天去成都旅游需要带什么衣服？
```

如果日期 / 日期范围明显属于自然使用维度，但 Skill 完全没有能力处理，并且 Description 又没有明确限制，不应 PASS。

**约束：不要无限扩需求。** 只检查 Natural / High-probability / Core-goal-consistent 的场景。Scenario Coverage 的目标是防止明显漏掉主流场景，不是做万能 Skill。

其他挑战用例根据 Skill 复杂度动态生成，至少考虑：

```text
正常场景
边界场景
异常场景
模糊输入
不完整输入
环境变化
真实规模
依赖失败
```

重点：Reviewer 的 Challenge Cases 不应该只复制 Creator 已经写过的测试。

### Stage 8: Real-world Robustness Review

判断 Skill 离开 Demo 环境以后还能不能工作。

检查：
- 输入是否过于理想化？
- 真实用户会不会这样说？
- 环境是否一致？
- 依赖是否可用？
- 数据是否动态变化？
- 规模是否会变化？
- 错误是否真的能恢复？

典型失败模式：
- **Happy Path Overfit**：只有高度结构化输入能工作（包括 input-shape overfit / usage-scenario overfit / default-value overfit）
- **Scale Failure**：小规模可以，真实规模不可用
- **Dynamic Reality Failure**：内置静态数据冒充动态事实
- **Fake Fallback**：API 失败后偷偷返回 Demo Data 伪装成功

### Stage 9: Product / Human Sanity Review

脱离实现细节，回到用户视角。

暂时忽略代码结构、目录、测试数量。只看：

```text
Original Requirement + Final Skill Behavior
```

Human Sanity Check 固定问题：

1. 这个 Skill 最终解决的是用户真正的问题吗？
2. 如果我是目标用户，我会觉得结果有用吗？
3. 有没有技术上成立、现实中明显荒谬的行为？
4. 输出是否足够让用户采取下一步行动？
5. Skill 是否做了大量用户根本不需要的事情？
6. 是否遗漏了一个人类专家显然会考虑的重要因素？
7. 有没有明显更简单、更可靠的实现？
8. 如果不知道这是 AI 创建的，我会认为它达到可发布水平吗？
9. Would a competent human engineer ship this?

最后一个问题应作为重要质量 Gate，不是装饰性文案。

### Stage 10: Operational Fitness Review

检查真实运行层面：

```text
性能
延迟
Token 成本
API 成本
并发
Rate Limit
资源消耗
稳定性
```

判断：实现是否以合理的成本和延迟完成任务？

### Stage 11: Failure Mode Scan

阅读 `$SKILL_ROOT/references/failure-modes.md`，根据 Stage 4 识别的风险，**按需选择**相关 Failure Modes 进行检查。

不要每次等深扫描所有 Failure Mode。根据当前 Skill 类型选择重点：

**Simple Semantic Skill**（周报、会议纪要、文本润色）：
- 重点：Happy Path Overfit、Claim > Capability、Product Sanity、Overengineering、Underengineering、Creator-Test Collusion

**Tool / Runtime Skill**（图片处理、PDF 转换、浏览器自动化）：
- 重点：Hallucinated Tool/API、Environment Mismatch、Claim > Capability、Happy Path、Fake Fallback

**External Fact / Dynamic Data Skill**（餐厅推荐、天气查询）：
- 重点：Fabricated Reality、Static-Dynamic Mismatch、Premature Give-up、Credential Assumption、Product Sanity

**Scenario Coverage Skill**（天气穿搭等涉及自然使用维度的 Skill）：
- 重点：Happy Path Overfit（含 Usage Scenario Overfit）、Claim > Capability、Product Sanity、Static-Dynamic Mismatch

对每个相关 Failure Mode 进行检查，如果发现匹配，标记对应 P0/P1/P2 级别。

### Stage 12: Final Ship Decision

综合所有 Stage 的结果，最终回答：

> Would a competent human engineer ship this?

输出 Ship Decision：

```text
YES              → 可以发布
YES_WITH_FIXES   → 修复 P1 后可发布
NO               → 不可发布
```

如果 NO，说明 Blocking reason。

最终 Verdict 同时结合：

```text
Score
+
P0/P1
+
Hard Gates
+
Human Ship Decision
```

## Verdict 判定规则

| 条件 | Verdict |
|------|---------|
| 无 P0/Hard Gate 触发，Ship Decision = YES，总分 >= 85 | PASS |
| 无 P0/Hard Gate 触发，Ship Decision = YES_WITH_FIXES，总分 >= 70 | PASS_WITH_FIXES |
| 有 P1 未修复，或 Ship Decision = NO，或总分 50-69 | REVISE |
| 有 P0 或 Hard Gate 触发，或 Ship Decision = NO，或总分 < 50 | FAIL |

## Hard Gates

Hard Gates 的完整定义见 `$SKILL_ROOT/references/issue-severity.md` 的 **Hard Gates** 章节。触发任一 Hard Gate，无论总分多少，都不能 PASS。

## Review 边界

问题必须和用户目标、核心能力或真实交付质量有明确关系。不要把锦上添花的问题升级成 P1/P0。严重度分级标准见 `$SKILL_ROOT/references/issue-severity.md`。

## 资源导航

| 资源 | 路径 | 用途 |
|------|------|------|
| 评分标准 | `$SKILL_ROOT/references/evaluation-rubric.md` | 100 分制评分维度 |
| 问题严重度 | `$SKILL_ROOT/references/issue-severity.md` | P0/P1/P2 + Hard Gates |
| 失败模式 | `$SKILL_ROOT/references/failure-modes.md` | FM-001 到 FM-017 |
| 评审报告模板 | `$SKILL_ROOT/assets/review-report.md` | Review Report 格式 |
