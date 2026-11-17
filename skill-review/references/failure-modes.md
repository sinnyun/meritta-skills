# Failure Mode Catalog

> 本文件是 Skill Review 的可持续积累知识库。
> 每个 Failure Mode 描述一种"Agent 全 PASS，但人类专家一看就不对"的已知失败模式。
> Reviewer 在 Review 过程中必须扫描与当前 Skill 相关的 Failure Modes。

---

## 使用方式

Reviewer 在 Stage 11 (Failure Mode Scan) 中：
1. 根据当前 Skill 类型选择相关的 Failure Modes
2. 对每个相关 Failure Mode 进行检查
3. 如果发现匹配，标记对应 P0/P1/P2 级别
4. 不要机械加载所有内容，按需检查

---

## Failure Mode 列表

### FM-001：Fabricated Reality / Fake Capability

**描述**：使用 Creator 自行构造的现实数据支撑生产能力。

**表现**：
- Skill 声称能完成依赖真实世界事实的任务
- 实际运行时使用 Creator 自己编造的数据集
- 数据来源不是真实环境、用户或权威来源

**检测要点**：
- 核心能力依赖的数据从哪里来？
- Remove-the-Mock Test：删除 Creator 生成的数据后能力是否成立？
- Mock 数据是否进入了生产 Runtime Path？

**严重级别**：P0

---

### FM-002：Hallucinated Tool / API

**描述**：实现依赖不存在的工具、接口或参数。

**表现**：
- 代码引用了实际不存在的 Tool / API 方法
- Mock 提供了同名接口，测试通过
- 目标运行环境根本没有这个能力

**检测要点**：
- 声称使用的 Tool / API 在目标环境中是否存在？
- 测试通过是因为 Mock 提供了同名接口吗？
- 是否有真实环境验证？

**验证要求**：必须运行实际命令验证 Tool 的存在性和用法，不能猜测。模型对工具的记忆可能过时或错误。

**严重级别**：P0

---

### FM-003：Environment Mismatch

**描述**：Creator 环境可以工作，目标环境无法运行。

**表现**：
- Creator 本机有特定依赖（如 ffmpeg、特定 Python 包）
- 测试在 Creator 环境通过
- 目标环境缺少这些依赖

**检测要点**：
- Skill 依赖的 Tool / CLI / Package / Runtime 在目标环境是否可用？
- 是否声明了运行环境要求？
- 是否有环境假设但没有验证？

**严重级别**：P0 或 P1

---

### FM-004：Creator-Test Collusion

**描述**：实现和测试建立在同一错误假设上。

**表现**：
- Creator 对 API Schema 理解错误
- 按错误理解写代码
- 按错误理解写 Mock 和 Test
- 测试全部 PASS，但整个假设是错的

**检测要点**：
- Test Oracle 是否可靠？（测试预期结果本身是否正确？）
- 测试是否只是重复实现逻辑？
- 是否有独立于 Creator 假设的验证？

**严重级别**：P0 或 P1

---

### FM-005：Happy Path Overfit

**描述**：只处理理想输入或单一默认使用场景，无意识地缩窄了用户的核心使用空间。

**表现**：

FM-005 覆盖三种 Overfit 子类型：

**1. Input-shape Overfit**：
- 高度结构化输入可以工作
- 自然语言、模糊输入、不完整输入失败
- 只有 Happy Path 测试

**2. Usage-scenario Overfit**：
- 只验证一个默认使用情境
- 遗漏了自然、高概率、属于用户核心目标的其他场景
- 例如：天气穿搭 Skill 只支持"今天怎么穿"，遗漏"下周出差怎么穿""未来几天旅游带什么衣服"

**3. Default-value Overfit**：
- 只支持默认时间（time = now）
- 只支持默认地点（location = current location）
- 只支持单对象（count = one）
- 只支持即时决策（mode = immediate）
- 只支持单文件（input = single file）
- 只支持单次操作（scope = one item）

这些默认值本身未必错误。问题是：用户需求本来明显覆盖更宽的自然场景，而 Creator 没有意识到自己缩窄了范围。如果 Description 没有明确限制，不应 PASS。

**检测要点**：
- 真实用户会这样输入吗？
- 遇到模糊/不完整输入会怎样？
- 是否有 Edge Case 测试？
- 用户在真实环境中会以哪些自然、高概率的方式使用这个能力？
- 实现是否未经用户要求，就把某个明显存在的自然维度固定成了一个默认值？
- Creator 的测试是否只覆盖了一个默认场景？
- Reviewer 的 Scenario Expansion Challenge：找一个与 Creator 默认测试不同、但仍然自然、高概率、属于用户核心目标的场景，Skill 是否能处理？

**严重级别**：P1

---

### FM-006：Claim > Capability

**描述**：能力声明超过真实实现边界。

**表现**：
- Description 声称"支持任意 PDF"
- 实际只支持文本 PDF，不支持扫描 PDF / 图片 PDF
- 没有明确声明能力边界

**检测要点**：
- Description 中的能力声明是否大于实际实现？
- 能力边界是否清晰？
- 未能覆盖的场景是否在文档中说明？

**严重级别**：P1 或 P0（如果差距极大）

---

### FM-007：Product Sanity Failure

**描述**：技术正确但真实用户结果明显不合理。

**表现**：
- 真实 API、真实数据、代码正确
- 但输出结果对真实用户来说明显荒谬
- 例如：推荐结果只按距离排序，不考虑用户场景

**检测要点**：
- Human Sanity Check：如果我是目标用户，会觉得结果有用吗？
- 有没有技术上成立、现实中明显荒谬的行为？
- 是否遗漏了人类专家显然会考虑的重要因素？

**严重级别**：P1 或 P0（如果结果具有误导性）

---

### FM-008：Static-Dynamic Mismatch

**描述**：用静态数据冒充动态事实。

**表现**：
- 内置静态 JSON 冒充实时数据
- 测试很稳定（因为数据不变）
- 现实中数据已经失效

**检测要点**：
- 动态数据是否有 Freshness 说明？
- 是否通过长期内置静态数据冒充实时能力？
- 数据是否会随时间失效？

**严重级别**：P0 或 P1

---

### FM-009：Scale Failure

**描述**：Demo 规模可运行，真实规模不可运行。

**表现**：
- 小文件 / 少量数据可以工作
- 真实大文件 / 大量数据导致 Context 溢出、超时、内存不足
- 没有规模限制说明

**检测要点**：
- 真实规模下会怎样？
- 是否有规模限制说明？
- 大规模数据是否全部加载进 Context？

**严重级别**：P1 或 P0（如果核心路径在真实规模下完全不可用）

---

### FM-010：Operationally Impractical

**描述**：成本、延迟、资源消耗不合理。

**表现**：
- 功能完全正确
- 但一次调用需要抓取大量网页 / 调用大量 API / 耗时极长
- 成本或延迟使得产品不可交付

**检测要点**：
- 完成任务需要多少 API 调用 / 网页抓取 / 模型调用？
- 延迟和成本是否在合理范围？
- 是否有优化空间？

**严重级别**：P1 或 P2

---

### FM-011：Fake Fallback

**描述**：异常时伪造成功结果。

**表现**：
- 真实 API 调用失败
- catch 后返回本地 Demo Data
- 用户仍然收到"正常结果"，不知道实际失败了

**检测要点**：
- 失败降级是否透明、可解释？
- 有没有出错后偷偷制造成功结果？
- 用户能否区分真实结果和降级结果？

**严重级别**：P0

---

### FM-012：Premature Give-up

**描述**：可自主解决的依赖过早推给用户。

**表现**：
- 缺少能力 → 立即要求用户配置 / 提供
- 实际上可以通过自主探索解决
- Creator 未尝试 Level 1/2/3 探索

**检测要点**：
- Creator 是否尝试了自主探索？
- 是否存在可合理获取的能力但 Creator 直接跳到 Ask User？
- 是否满足 Ask User = Last Resort 的全部 5 个条件？

**严重级别**：P1 或 P0（如果严重阻塞核心能力）

---

### FM-013：Overengineering

**描述**：问题简单但实现过度复杂。

**表现**：
- 简单任务却创建大量文件
- 不需要配置系统却设计了复杂配置
- 复杂度与问题复杂度不匹配

**检测要点**：
- 这个 Skill 的复杂度是否和问题复杂度匹配？
- 有没有明显更简单、更可靠的实现？
- 是否做了大量用户根本不需要的事情？

**严重级别**：P2

---

### FM-014：Underengineering

**描述**：问题复杂但实现明显不足。

**表现**：
- 真实问题需要工具、脚本、异常处理、状态管理
- 却只写了一个简单 SKILL.md
- 核心路径无法可靠工作

**检测要点**：
- 真实问题复杂度如何？
- 当前实现是否足以覆盖？
- 是否缺少必要的异常处理、边界处理、状态管理？

**严重级别**：P1 或 P0

---

### FM-015：Permission / Credential Assumption

**描述**：假设拥有实际上不存在的权限或 Credential。

**表现**：
- 代码假设有 API Key / OAuth Token
- 测试时 Creator 手动配置了 Credential
- 目标环境用户没有这些 Credential

**检测要点**：
- Skill 依赖的 Credential 在目标环境是否可用？
- 是否有 Credential 缺失时的降级策略？
- 是否提前告知用户需要什么 Credential？

**严重级别**：P1 或 P0（如果核心路径完全不可用）

---

### FM-016：CWD Dependency Failure

**描述**：脚本依赖当前工作目录，开发时碰巧能用，安装后从其他目录运行就失败。

**表现**：
- 脚本使用 `Path("./")` 或 `Path('.')` 相对路径
- 使用 `os.chdir()` 改变工作目录
- 在开发目录运行正常，安装后报文件找不到

**检测要点**：
- 脚本是否使用基于 `Path(__file__)` 的路径解析？
- 是否存在 `Path("./")`、`Path('.')` 或 `os.chdir()`？
- 从任意目录运行脚本是否都能正常工作？

**严重级别**：P1

---

### FM-017：Missing Frontmatter / Format Violation

**描述**：SKILL.md 缺少 YAML frontmatter 或 frontmatter 格式不合法。

**表现**：
- SKILL.md 直接从 `# 标题` 开始，没有 `---` 包裹的头部声明
- frontmatter 缺少 `name` 或 `description` 字段
- `name` 不符合 kebab-case 规范（含大写、下划线、空格）
- `description` 缺少触发词或场景描述
- Creator 用 Write 工具覆盖了 init_skill.py 生成的模板文件，丢失了 frontmatter

**检测要点**：
- SKILL.md 是否以 `---` 开头？
- frontmatter 是否有合法的 `name`（全小写 kebab-case）？
- frontmatter 是否有 `description`（包含做什么 + 何时触发 + 触发词）？
- frontmatter 是否正确闭合（第二个 `---`）？

**根因**：Creator 在 Step 8 用 Write 工具整文件覆盖而非 Edit 修改模板，或跳过了 init_skill.py 直接手写。

**严重级别**：P0（frontmatter 缺失或不合法时 Skill 无法被正确加载和触发）

---

## 持续积累

以后每次发现"Agent 全 PASS 但真实用户/人类专家发现明显问题"的情况：

```text
Root Cause Analysis
↓
抽象失败模式
↓
加入本 Catalog
↓
增加 Regression Eval
```

形成：

```text
Production Failure
↓
Engineering Knowledge
↓
Reviewer Rule
↓
Regression Test
```

让 Skill Engineer 真正从失败中积累能力。
