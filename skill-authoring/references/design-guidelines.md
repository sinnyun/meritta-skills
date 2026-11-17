# Skill 设计指南

## 什么问题适合 Skill

- 重复工作（每次都走相同流程）
- 多步骤 Workflow（需要协调多个步骤）
- Tool / Connector 使用规范（需要正确的工具调用方式）
- 组织标准（团队约定的规范流程）
- 专业流程（需要领域知识的流程）
- 高复用任务（多人会重复使用）

## 什么情况不值得 Skill 化

如果一句普通 Prompt 就能可靠完成，不要为了 Skill 而 Skill。

判断标准：
- 给普通 AI 一句话 Prompt 就能完成 70-80% 效果 → 不值得 Skill 化
- 没有工作流、工具调用、数据获取、状态管理或专业机制 → 只是 Prompt 套壳
- 使用频率极低且场景单一 → 直接写 Prompt 更高效

## Natural Usage Scenario Coverage

> 防止 Creator 无意识地把某个维度固定成一个默认值，把更宽的 Capability 收窄成一个默认场景。

在定义 Capability 之前，轻量思考：用户在真实环境中，会以哪些自然、高概率的方式使用这个能力？

### 识别自然使用维度

只考虑和当前 Capability 明显相关的维度：

```text
时间（即时 vs 未来 vs 范围）
地点
对象
数量（单个 vs 批量）
范围
输入形态
使用目的
```

不要机械枚举全部。Creator 应问：

> 当前实现是否未经用户要求，就把某个明显存在的自然维度固定成了一个默认值？

### 典型 Default Assumption

```text
time = now
location = current location
count = one
input = single file
mode = immediate
scope = one item
```

这些默认值本身未必错误。问题是：用户需求本来明显覆盖更宽的自然场景，而 Creator 没有意识到自己缩窄了范围。

### 约束：不要变成"无限扩需求"

只关注 Natural / High-probability / Core-goal-consistent 的场景。

判断标准：

> 如果把这个需求交给一个有经验的人类产品经理或工程师，他是否很自然就会想到这个场景？

如果 YES：应该考虑。如果只是小概率未来可能：不需要加入。

Scenario Coverage 的目标是防止明显漏掉主流场景，不是做万能 Skill。

---

## 内容分配决策

```text
模型本身擅长完成的语义任务
→ instruction（写入 SKILL.md）

重复、确定、容易出错的操作
→ scripts（创建脚本文件）

大量领域知识、规范、API 文档
→ references（创建参考文档）

需要直接复制或使用的模板、素材
→ assets（创建素材文件）
```

### Script vs Model 判断

优先 Script：
- 文件转换（格式 A → 格式 B）
- 文件解析（提取结构化数据）
- 批处理（对多个文件执行相同操作）
- 结构校验（检查格式是否合法）
- 确定性计算（数学运算、统计）
- 重复性操作（模板初始化）

优先 Model：
- 总结
- 判断（语义对错、质量高低）
- 创作（文案、代码）
- 语义分析（理解用户意图）
- 非确定性推理（多种合理解读）

### 混合模式

很多 Skill 是混合模式：Script 做确定性部分，Model 做语义判断部分。

示例：
- Style Transfer：playwright-cli 截图（Script）+ 视觉差异分析（Model）
- Code Review：脚本提取 diff（Script）+ 代码质量评估（Model）

## Progressive Loading

### 原则

SKILL.md 应尽量精简。不要把所有知识和边界情况全部写进 SKILL.md。

```text
SKILL.md
   ↓
只包含核心工作流和资源导航

references/
   ↓
存放详细知识和复杂规则

scripts/
   ↓
负责确定性任务

assets/
   ↓
负责模板和最终输出素材
```

### Context 预算

SKILL.md 建议：
- 核心工作流：200-500 字
- Tool 使用规则：100-200 字
- Resource 导航：表格形式，简洁
- 重要约束：100-200 字
- 总计：建议控制在 2000 字以内

超出部分应拆分到 references。

### 避免的情况

- SKILL.md 超过 5000 字 → Context 效率低，考虑拆分
- references 超过 3 层嵌套 → 导航困难，考虑扁平化
- scripts 超过 10 个文件 → 可能过度设计，考虑合并
- 每个文件只有几行内容 → 不值得独立文件，合并

## 目录设计原则

不要为了目录看起来完整就机械生成所有子目录。目录结构规范见 `$SKILL_ROOT/references/skill-spec.md`。

使用模板初始化后，删除不需要的空目录。最终交付的 Skill 目录应该只包含有实际内容的文件。

---

## Conditional Risk Guidance

> 以下内容是**条件性风险指导**，只在 Skill 存在对应风险时深入执行。
>
> 不是所有 Skill 都需要执行以下所有章节。只有当 Skill 的核心 Capability 依赖相关风险时，才进入对应部分。

### 风险类型快速判断

| 风险类型 | 何时需要深入 |
|----------|--------------|
| **External Facts / Grounding** | 核心能力依赖真实世界事实、动态数据 |
| **Tool / Runtime** | 依赖特定工具、CLI、运行时环境 |
| **Capability Gap** | 发现完成 Skill 需要的能力当前环境不具备 |
| **Integration / Scale** | 涉及多系统、跨仓库、大量文件、长流程 |

如果 Skill 不涉及对应风险，直接跳过相关章节。

---

## External Facts / Grounding & Capability Gap Resolution

> 只有当 Skill 的核心 Capability 依赖真实世界事实、动态数据，或检测到 Capability Gap 时，才需要深入执行本节。

完整的数据依赖分析（5 类数据分类、静态知识 vs 动态事实判断标准、禁止伪造生产数据 Hard Rule、Mock/Fixture 规则、Remove-the-Mock Test）和 Capability Gap Resolution（Level 1/2/3 自主解决顺序、Ask User = Last Resort 5 个条件、禁止两个错误极端）详见：

→ `$SKILL_ROOT/references/grounding-guidance.md`

---

### Tool / Runtime 风险

> 只有当 Skill 依赖特定 Tool / CLI / Package / Runtime 时才需要深入检查。

**检查要点**：

```text
Tool 是否真实存在于目标环境？
版本是否匹配？
Package 是否可安装？
权限是否足够？
实际执行是否有证据？
```

**不要因为存在 Tool Dependency 就自动进入 Grounding / Freshness / External Fact Provenance。** Tool 依赖和数据真实性是两类不同的风险。

当 Skill 涉及 Web、Browser、Network Access、Search / Fetch / API / MCP / CLI 工具选型时，读取 `$SKILL_ROOT/references/web-access-guidance.md`。

**典型 Failure Mode**：
- Hallucinated Tool / API（FM-002）：引用不存在的工具或接口
- Environment Mismatch（FM-003）：Creator 环境可以工作，目标环境无法运行
- Permission / Credential Assumption（FM-015）：假设拥有实际上不存在的权限

---

### Integration / Scale 风险

> 只有当 Skill 涉及多系统、跨仓库、大量文件、长流程时才需要深入检查。

**检查要点**：

```text
Integration Boundary：多系统集成的边界是否清晰？
Environment Fitness：目标环境是否支持？
Scale：真实规模下是否可用？
Performance：延迟和成本是否在合理范围？
Failure Recovery：失败时是否能恢复？
Operational Cost：运营成本是否可接受？
```

**典型 Failure Mode**：
- Scale Failure（FM-009）：Demo 规模可运行，真实规模不可运行
- Operationally Impractical（FM-010）：成本、延迟、资源消耗不合理

---

## Right-sized Engineering

> 使用能够可靠完成任务的最小充分复杂度。

### 避免 Overengineering

如果一句普通 Prompt 或一个简单 SKILL.md 就能可靠完成，不要为了 Skill 而 Skill。

过度设计的表现：
- 简单任务却创建大量 reference / script / asset 文件
- 不需要配置系统却设计了复杂配置
- 不需要状态管理却引入了状态层
- 一个 20 行能解决的问题被扩展为 6 个文件 + 复杂 workflow

判断标准：

> 这个 Skill 的复杂度是否和问题复杂度匹配？

### 避免 Underengineering

反过来，如果真实问题明显需要工具、脚本、参考文档、异常处理、状态管理，却只写了一个简单的 SKILL.md，也属于问题。

容易 Underengineering 的场景：
- 跨仓库代码分析
- 网页自动化
- 复杂文档处理
- 真实 API 工作流
- 需要多步骤协调的任务

判断标准：

> 如果这个任务交给一个有经验的人类工程师，他会需要哪些工具和步骤？

### 目标

```text
最小，但足够
简单，但可靠
能力边界清晰
证据与声明匹配
```

不是"越简单越好"，也不是"越复杂越专业"。

---

## Evidence Plan

> Creator 在开发之前就应该知道：最后用什么证据证明这个 Skill 真的完成了任务？

在开始实现核心能力之前，内部思考：

```text
核心 Claim 是什么？

要证明这个 Claim，
至少需要什么 Evidence？
```

Evidence 可以是：

```text
真实 Tool 调用
真实 API
真实 Connector
实际运行结果
用户提供数据
可信数据源
独立测试
真实文件验证
真实 Browser 行为
外部系统响应
```

但以下内容不能自动被视为充分证据：

```text
Creator 自己写的说明
Creator 自己构造的 Mock
Creator 自己定义的预期结果
Creator 自己写的一组 Happy Path 测试
```

Evidence Plan 不需要生成额外文件，作为 Authoring 内部推理和工作流程的一部分即可。

目标是提升质量，而不是增加文件数量。
