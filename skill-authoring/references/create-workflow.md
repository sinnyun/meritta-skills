# Create Skill Workflow

## 前置条件

- 已定位 `SKILL_ROOT`（见 skill-authoring SKILL.md 路径解析）
- 用户已提供 Skill 创建需求

## Step 1: Understand User Intent

从用户自然语言描述中提取：

| 维度 | 提取内容 | 示例 |
|------|----------|------|
| 核心目标 | 用户想让 Skill 做什么 | "给人物照片抠图" |
| 输入 | Skill 需要什么输入 | 图片文件路径 |
| 输出 | Skill 产出什么 | 去背景后的 PNG |
| 运行环境 | 在哪运行 | 本地 Node.js / 浏览器 / 纯模型 |
| 工具依赖 | 需要什么外部工具 | playwright-cli / ffmpeg / 无 |

关注用户真实意图，不要只机械实现字面表达。判断：
- 是否理解了真实任务目标？
- 是否遗漏关键使用场景？
- 输入输出是否符合实际使用习惯？
- 是否出现"技术实现正确，但解决了错误问题"的风险？

如果需求已足够明确，直接进入 Step 2。只有以下情况才询问用户（Intent Clarification，不是 Premature Give-up）：
- 核心目标不明确（无法判断 Skill 要做什么）
- 输入/输出完全不清晰（无法设计工作流）
- 存在多种合理解读且差异巨大

## Step 2: Identify Natural Usage Scenarios

轻量思考：用户在真实环境中，会以哪些自然、高概率的方式使用这个能力？

**目的**：防止 Creator 无意识地把某个维度固定成一个默认值，把更宽的 Capability 收窄成一个默认场景。

**约束**：只关注 Natural / High-probability / Core-goal-consistent 的场景，不要变成"无限扩需求"。

阅读 `$SKILL_ROOT/references/design-guidelines.md` 的 **Natural Usage Scenario Coverage** 章节，完成自然使用维度识别和 Default Assumption 检查。

**产出**：
- 当前 Capability 涉及哪些自然使用维度
- 是否存在未经用户要求就固定的默认值
- 是否需要扩展 Claim 或在 Description 中明确限制

## Step 3: Define Capability Claims & Boundaries

在开始实现之前，明确这个 Skill 声称拥有哪些核心能力。

```text
这个 Skill 声称能做什么？
```

为每个核心能力定义 Claim：

```text
Claim: <能力描述>
Required Dependency: <需要的工具/数据/环境>
Expected Boundary: <能力覆盖范围和限制>
Natural Scenario Coverage: <覆盖哪些自然使用场景>
```

核心原则：

> Description / Documentation 中的能力声明不能大于实际能力边界。

如果 Claim 只能覆盖部分场景，必须缩小 Claim 或明确说明限制。

如果 Step 2 识别出的自然使用场景中有些未被覆盖，要么扩展 Claim，要么在 Description 中明确排除。

## Step 4: Identify Relevant Risks / Dependencies

轻量判断：当前 Capability 实际有哪些风险和依赖？

识别是否存在以下风险（只标记实际存在的）：

```text
Semantic complexity
Tool / Runtime dependency
External facts
Dynamic data
External system / integration
Permission / credential
Scale / performance
Complex product logic
```

不需要 Risk Score、复杂打分、额外配置文件。这些标签只用于：

> 决定接下来哪些专项规则值得深入。

根据识别结果，在后续 Step 5 中只进入相关的条件检查。如果某个风险类别不存在，直接跳过。

当检测到 Web Access、Browser、Network、Online System、Remote API 风险时，读取 `$SKILL_ROOT/references/web-access-guidance.md`，按决策树选择最佳工具。

### 不同 Skill 类型的重点

**Simple Semantic Skill**（周报、会议纪要、文本润色、总结）：
- 重点：Intent、Scenario、Evidence、Output Quality、Human Sanity、Right-sized Engineering
- 默认不需要深入：Grounding、Freshness、Provider、Credential

**Tool / Runtime Skill**（图片处理、PDF 转换、浏览器自动化）：
- 重点：Tool 真实性、Runtime 兼容性、Package 可安装性、版本匹配、权限、实际执行证据
- 不要因为存在 Tool Dependency 就自动进入 Grounding / Freshness

**External Fact / Dynamic Data Skill**（餐厅推荐、天气查询、航班搜索）：
- 重点：完整 Grounding 体系（Data Dependency、Provenance、Freshness、Capability Gap、Remove-the-Mock）

**Complex Integration / Scale Skill**（多系统、跨仓库、长流程）：
- 重点：Integration Boundary、Environment Fitness、Scale、Performance、Failure Recovery、Operational Cost

## Step 5: Conditional Deep Checks

根据 Step 4 识别出的风险，只进入相关检查。不存在对应风险的 Skill 直接跳过。

### 5.1: External Fact / Dynamic Data 风险

只有核心 Capability 依赖真实世界事实、真实实体、动态事实、实时状态时，才执行：

阅读 `$SKILL_ROOT/references/design-guidelines.md` 的以下章节：
- **Data Dependency Analysis**：判断数据来源和类型
- **Hard Rule：禁止伪造生产数据**：理解 Mock 与生产数据的边界

产出：
- data source classification
- freshness requirement
- fallback behavior

### 5.2: Capability Gap Detection 与 Resolution

**只有实际检测到 Capability Gap 时才执行。** 不要每创建一个 Skill 都先探索一次 API / MCP。

如果发现 Capability Gap，阅读 `$SKILL_ROOT/references/design-guidelines.md` 的 **Capability Gap Detection 与 Resolution** 章节，按 Level 1 → 2 → 3 顺序自主探索，禁止直接进入 Ask User。

注意区分：

```text
Dependency Ask（能力缺失，需要用户配置）
≠
Requirement Clarification（需求本身有歧义，正常询问）
```

### 5.3: Tool / Runtime 风险

如果依赖特定 Tool / CLI / Package / Runtime，阅读 `$SKILL_ROOT/references/design-guidelines.md` 的 **Tool / Runtime 风险** 章节，检查 Tool 真实性、版本匹配、Package 可安装性、权限和实际执行证据。

当涉及 Web / Browser / Network Access / Search / Fetch / API / MCP / CLI 工具选型时，阅读 `$SKILL_ROOT/references/web-access-guidance.md`，按 Capability First 原则选择最小充分工具，检查复用优先级，避免自动 Provision Browser Runtime。

### 5.4: Integration / Scale 风险

如果涉及多系统、跨仓库、大量文件、长流程，阅读 `$SKILL_ROOT/references/design-guidelines.md` 的 **Integration / Scale 风险** 章节，检查集成边界、环境适配、规模、性能、失败恢复和运营成本。

## Step 6: Design Minimum Sufficient Architecture

阅读 `$SKILL_ROOT/references/design-guidelines.md`：
- **内容分配决策**：判断哪些内容用 instruction / scripts / references / assets
- **Right-sized Engineering**：确保复杂度与问题匹配（避免 Overengineering 和 Underengineering）

**不要机械生成所有目录**。没有必要的目录不创建（目录结构规范见 `$SKILL_ROOT/references/skill-spec.md`）。

确定：
1. Skill 名称（lowercase, kebab-case，命名规则见 skill-spec.md）
2. 需要哪些目录（scripts / references / assets）
3. SKILL.md 的核心工作流
4. 每个文件的大致内容

## Step 7: Define Evidence Plan

在开始实现核心能力之前，内部思考：核心 Claim 需要什么 Evidence 来证明？

> Evidence is universal. Grounding is one possible evidence requirement.

所有 Skill 都需要证据，只是证据形式不同：

- **周报 Skill**：真实工作记录 → 生成周报 → 是否突出成果、避免流水账
- **图片处理 Skill**：真实图片 → 实际执行 → 输出质量验证
- **网页自动化 Skill**：真实页面 → 实际操作 → 页面状态变化
- **餐厅推荐 Skill**：真实业务数据 → 实际候选 → 推荐结果

Evidence Plan 不需要生成额外文件，作为 Authoring 内部推理和工作流程的一部分即可。

Evidence 的类型、排除标准和详细规则见 `$SKILL_ROOT/references/design-guidelines.md` 的 **Evidence Plan** 章节。

## Step 8: Implement Skill

### 初始化目录

运行初始化脚本：

```bash
python "$SKILL_ROOT/scripts/init_skill.py" \
  --name "<skill-name>" \
  --skill-root "$SKILL_ROOT"
```

**重要**：Skill 会直接在**当前工作目录**下创建（`./<skill-name>/`），整个开发过程都在此工作目录中进行。

脚本会从模板创建基础目录结构。初始化后根据设计决定保留哪些目录。

### 编写 SKILL.md

阅读 `$SKILL_ROOT/references/skill-spec.md`，编写 SKILL.md：

YAML frontmatter 重点：

```yaml
---
name: <skill-name>
description: |
  <一句话说清楚 Skill 做什么>
  <什么场景应该触发>
  触发词：关键词1、关键词2、关键词3。
allowed-tools: <列出需要的工具权限>
---
```

Body 重点：
- **Workflow**：核心步骤，每步有明确输入输出
- **Tool 使用规则**：何时用脚本、何时用模型
- **Resource 导航**：指向 references / scripts
- **重要约束**：安全限制、边界条件

**不要**重复大量基础常识。**不要**把所有知识塞进 SKILL.md。

### 编写 Supporting Resources

**scripts/**：确定性操作脚本。每个脚本必须有明确的输入输出、可独立运行测试、包含错误处理、不依赖未安装的包。

**references/**：详细知识和复杂规则。每个文件聚焦一个主题。

**assets/**：模板和素材文件。只放需要直接复制使用的内容。

### 清理模板残留

检查并删除：
- 模板中的占位符文本（如 `<TODO>`、`example-placeholder`）
- 没有实际内容的空目录
- 不需要的模板文件

## Step 9: Run Static Validation

运行静态校验：

```bash
python "$SKILL_ROOT/scripts/validate_skill.py" --skill-path <path>
```

修复所有静态错误。

## Step 10: Run Creator Tests

创建测试验证 Skill 的核心能力。

测试应覆盖 Step 2 识别出的主要自然使用场景，不只是单一默认场景。

注意：
- 测试数据与生产数据严格隔离
- Mock 数据必须标记 `TEST DATA ONLY`
- 不进入生产 Runtime Path

## Step 11: Check Capability Claims Against Evidence

第一版 Skill 创建完成以后，在进入 Review 前，Creator 自己先做一次 Claim-Evidence 对齐检查。

必须回答：

1. Skill 声称能完成什么核心能力？（回顾 Step 3 的 Capability Claims）
2. 每个能力依赖哪些数据和工具？
3. 数据来源是什么？是否真实可靠？
4. 是否存在 Creator 自己生成的现实世界数据？
5. Mock 数据是否进入 Runtime Path？
6. 所有核心能力是否都有真实 Tool / Data / Input 支撑？
7. Description 中的能力声明是否大于实际能力边界？
8. 测试是否真正证明了核心 Capability，而不只是内部函数工作？
9. 测试的预期结果本身是否可靠？（Test Oracle Review）
10. 自然使用场景覆盖检查：实现是否无意识地缩窄了用户的核心使用空间？

### 条件检查

**Remove-the-Mock Test**（只在存在 Mock / Fixture / Creator-generated external facts 时执行）：

> 如果删除 Creator 生成的 fixtures/examples，Skill 是否仍然具有它声称的能力？

纯文本处理 Skill（如周报生成）没有 Mock/Data，不需要执行此检查。

### 静态知识不要误伤

静态知识与动态事实的判断标准见 `$SKILL_ROOT/references/design-guidelines.md` 的 **静态知识 vs 动态事实的判断标准** 章节。

如果任何 Claim 缺少充分 Evidence，需要：
- 缩小 Claim 至证据可支撑的范围
- 或补充真实证据
- 或重新设计实现

## Step 12: Prepare Independent Review

自检通过后，准备 Review Package：

```bash
python "$SKILL_ROOT/scripts/prepare_review.py" \
  --skill-path <path> \
  --requirement "<原始需求>" \
  --skill-root "$SKILL_ROOT"
```

进入 REVIEW 状态。
