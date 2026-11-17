# Grounding & Capability Gap Resolution 指导

> 本文件是条件性加载的参考文档。
> 只有当 Skill 的核心 Capability 依赖真实世界事实、动态数据，或检测到 Capability Gap 时，才需要深入阅读。

---

## External Facts / Grounding

> 只有当 Skill 的核心 Capability 依赖真实世界事实、动态数据时，才需要深入执行本节。

### Data Dependency Analysis

> **核心原则：Skill 可以创造算法、流程和规则，但不能为了让能力看起来可用而创造现实世界事实。**

```text
Skill can create logic.
Skill must not fabricate reality.
```

在创建每个 Skill 时，Creator 必须先回答：

> 完成这个 Skill 所需要的信息和事实，从哪里来？

将数据至少分为以下 5 类：

### 1. 用户输入数据

例如：会议记录、用户上传的 Excel、PDF、代码、用户填写的预算、用户当前位置。

来源：`User Input`。允许直接使用。

### 2. Skill 内置静态规则或知识

例如：公司写作规范、评分标准、固定模板、领域术语、计算公式、HTTP 状态码、税率规则、语言映射表。

来源：`references/` 或 `assets/`。只要这些内容本身适合长期固定，可以内置。

### 3. 用户提供的业务数据

例如：用户自己的客户列表、内部商品目录、企业知识库、自有餐厅列表。

来源：`User / Organization Provided`。不能由 Creator 自己脑补。

### 4. 外部现实世界事实

例如：真实地点、商家、商品、人员、组织、地址、评分、联系方式等本应从真实世界获取的实体或事实。

必须存在以下真实数据源中的至少一种：`Web Search` / `Business Search` / `Maps / POI API` / `Connector` / `Official API` / `User-provided dataset`。

### 5. 动态现实数据

例如：营业时间、实时价格、库存、新闻、航班、天气等会随时间变化的事实。

除了来源以外，还必须考虑 `Freshness`。不能通过长期内置静态 JSON 冒充实时能力。

### 静态知识 vs 动态事实的判断标准

> 这个数据是否代表一个本应从真实世界、用户或权威来源获取的事实？

- 税率规则、公司内部规范、固定模板、语言映射表、HTTP 状态码、行业术语 → 适合静态存在
- 真实实体列表、实时价格、实时状态、动态环境数据 → 必须来自真实数据源

不要写成 "Skill 不允许包含任何数据"。正确判断标准是数据是否代表本应从真实世界获取的事实。

### Hard Rule：禁止伪造生产数据

> NEVER fabricate external real-world entities, facts, or production datasets in order to make a Skill appear functional.

Creator 不得自己生成以下类型的数据，然后将这些数据作为生产路径中的真实数据使用：

- 任何代表真实世界实体的事实数据集（如真实地点、商家、商品、人员、组织等）
- 任何代表动态现实事实的数据（如实时价格、库存、天气、航班状态等）

通用判定规则：

> 如果 Skill 的核心能力依赖本应由真实环境、用户或权威来源提供的事实，而 Creator 使用自行构造的事实替代，则判定为 Fake Capability。

禁止的设计模式：

```text
skill-name/
├── assets/
│   └── <real-world-entities>.json   ← Creator 自己编造的现实数据
└── scripts/
    └── search.py                     ← 搜索 Creator 自己生成的数据
```

这是 Fake Capability。

#### Mock / Fixture 数据仍然允许

Mock 数据允许用于：`Unit Test` / `Integration Test` / `Evals` / `Examples` / `Fixtures`。

例如 `tests/fixtures/<entity>.mock.json` 是允许的，但必须：
- 明确标记 `TEST DATA ONLY`
- 不进入生产 Runtime Path

> 测试搜索算法可以使用假的测试数据。但真实给用户返回结果不能使用假数据。

#### Remove-the-Mock Test

创建完成后自检：

> 如果去掉 Creator 自己生成的测试数据，这个 Skill 是否仍然具有它声称的能力？

如果答案 NO，就需要重新设计。

### 缺少真实数据源时的正确行为

如果 Creator 判断 Skill 需要真实外部数据，但当前环境没有 Web / API / Connector / 搜索 / 用户数据等真实来源：

禁止自行生成数据补齐能力。

正确行为按优先级：

1. **使用当前运行环境已经存在的真实能力** — 优先复用已有 Tool / Search / Connector
2. **明确声明运行依赖** — 如 "Requires a real data source provider for <capability>"
3. **明确告诉用户** — "当前环境缺少可靠的数据源，需要提供或启用对应工具"
4. **合理降级** — 如 "可以根据用户提供的数据进行排序，但无法自行搜索真实数据"

禁止：为了避免告诉用户"缺工具"，自己造数据把流程跑通。

---

## Capability Gap Detection 与 Resolution

> **只有实际检测到 Capability Gap 时才执行以下检查。** 不要每创建一个 Skill 都先探索一次 API / MCP。

### Capability Gap Detection

在 Data Dependency Analysis 后，Creator 必须判断：

> 完成这个 Skill 所需要的能力，当前运行环境是否已经具备？

如果发现 Capability Gap，**不能直接进入 Ask User**。必须进入 Capability Resolution。

#### Capability Resolution 自主解决顺序

按以下顺序探索：

**Level 1：检查当前环境已有能力** — 现有 Tools / Skills / MCP / Connectors / CLI / SDK / 项目 Dependencies / 已有 Search / Browser 能力。优先复用已经存在的能力。

**Level 2：检查当前项目已有实现** — 搜索当前代码仓是否已存在 API Client / HTTP Wrapper / MCP Config / Provider Adapter / Search Service。不要重复造轮子。

**Level 3：主动探索可接入能力** — 官方 API / 开放 API / 公开数据源 / MCP Server / CLI Tool / SDK / Package / Web Search / Browser-based retrieval / Open Data。

#### 优先选择"不需要用户介入"的方案

```text
无需额外配置即可使用
↓
当前环境已经授权
↓
公开且无需 Credential
↓
可以自动安装 / 配置
↓
需要 Credential
↓
需要用户提供额外业务数据
```

#### 评估候选数据源质量

找到接口不代表可以直接使用。必须评估：Coverage / Accuracy / Freshness / Availability / Rate Limit / Authentication / Cost / Terms / Integration Complexity / Required Fields。

不得因为找到一个 API，就假装所有能力已经解决。

#### 允许组合多个真实数据源

一个 Provider 不一定需要解决所有问题。允许 Source A 获取候选 + Source B 补充详情 + Algorithm 排序。

#### 需要 Credential 时仍然不要立即停止

如果最佳数据源需要 API Key / OAuth，Creator 仍应先完成 Provider Selection / Integration Design / Adapter Implementation / Configuration Interface / Fallback Design / Tests。直到只剩真正无法替用户完成的步骤（如填写 API_KEY），才向用户提出最小化请求。

#### Ask User = Last Resort

只有满足以下全部条件时才能要求用户解决：

1. 当前环境没有现成能力
2. 已检查当前项目没有可复用实现
3. 已主动探索合理的外部方案
4. 没有无需用户介入的可靠方案
5. 剩余阻塞确实只能由用户解决

#### 禁止 Lazy Dependency Resolution

> NEVER shift a solvable dependency problem to the user without first attempting reasonable discovery and resolution.

禁止：发现缺少真实数据 → 让用户提供数据源。
禁止：发现需要搜索 → 让用户自己找 MCP。
禁止：发现需要 API → 直接让用户提供 API。

如果这些能力可以通过自主探索解决。

#### 禁止两个错误极端

- **Fake Capability**：没有真实数据源 → 自己造数据 → 假装实现完成。禁止。
- **Premature Give-up**：没有真实数据源 → 立即告诉用户无法实现。禁止。

正确模式：没有真实数据源 → 主动寻找解决方案 → 找到则接入验证，找不到再判断是否需要用户。
