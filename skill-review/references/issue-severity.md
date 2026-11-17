# Issue Severity

## Hard Gates

出现以下问题时，无论总分多少，都不能 PASS：

- 核心用户意图明显理解错误
- 核心 Capability 没有真实实现
- 核心能力依赖伪造现实事实
- 依赖不存在的 Tool / API
- 核心 Test Oracle 明显无效
- 目标环境根本无法运行核心路径
- 核心输出对用户具有明显误导性
- 存在 P0 Failure Mode

Hard Gates 不可被高分平均掉。

---

## P0 — 阻塞交付

必须修复，不能交付。

**指控前置条件**：P0 指控涉及 Tool / API 存在性或用法时，必须先实际运行命令验证。不能基于模型知识假设。

### 核心 Capability 问题

- 核心能力是假的（依赖 Creator 编造的现实数据支撑生产能力）
- 核心需求实现错了（用户要 A，Skill 做了 B）
- 核心 Tool / API 不存在（实现依赖不存在的工具、接口或参数）
- 真实运行环境不可执行核心路径
- 核心数据不可信且被当作真实结果返回给用户
- 测试无法证明核心能力但却被当作发布依据
- 核心输出对用户具有明显误导性

### 原有 P0

- Skill 无法运行（脚本报错、依赖缺失、路径错误）
- 使用不存在的工具（引用了未安装的 CLI 或库）
- 严重安全问题（Skill 会删除文件、泄露数据、执行恶意代码）
- 输出完全错误（生成的 Skill 产出与预期完全不符）
- SKILL.md frontmatter 不合法（name 缺失、description 缺失）
- name 不符合规范（大写、下划线、非 kebab-case）

### Failure Mode 相关 P0

- **FM-001 Fabricated Reality**：核心能力依赖 Creator 编造的现实数据
- **FM-002 Hallucinated API**：实现依赖不存在的 Tool / API
- **FM-011 Fake Fallback**：异常时伪造成功结果，用户收到"正常结果"但实际失败了

---

## P1 — 重要问题

Skill 可以部分工作，但真实使用存在明显风险。原则上必须修复。

### 真实使用风险

- Happy Path 过强（只处理理想结构化输入）
- 重要 Edge Case 缺失
- 能力声明偏大（Claim > Capability）
- 依赖探索不足（未按 Level 1/2/3 顺序探索）
- 性能 / 成本明显不合理
- 产品结果存在明显不合理情况（Product Sanity Failure）
- 真实数据源存在但 Freshness 未说明
- Creator 过早 Ask User 但仍有自主解决空间
- 能力声明明显超过工具支持范围

### 原有 P1

- 核心工作流不完整（缺少关键步骤）
- Trigger / description 明显设计错误（描述与功能不符、触发词不实际）
- 关键异常未处理（文件不存在、网络请求失败、参数错误）
- 实际使用稳定性明显不足（偶发崩溃、内存泄漏）
- 引用的文件路径不正确（references / scripts 路径错误）
- description 缺少触发场景描述

### Failure Mode 相关 P1

- **FM-003 Environment Mismatch**：Creator 环境工作，目标环境无法运行
- **FM-004 Creator-Test Collusion**：实现和测试建立在同一错误假设上
- **FM-005 Happy Path Overfit**：只处理理想输入
- **FM-006 Claim > Capability**：能力声明超过真实实现边界
- **FM-007 Product Sanity Failure**：技术正确但真实用户结果明显不合理
- **FM-008 Static-Dynamic Mismatch**：用静态数据冒充动态事实
- **FM-009 Scale Failure**：Demo 规模可运行，真实规模不可运行
- **FM-012 Premature Give-up**：可自主解决的依赖过早推给用户
- **FM-014 Underengineering**：问题复杂但实现明显不足
- **FM-015 Permission / Credential Assumption**：假设拥有不存在的权限

---

## P2 — 普通质量问题

不影响核心交付但值得优化。根据收益与复杂度判断是否修复。

### 结构与质量

- Context 效率不够好（SKILL.md 过长，应拆分到 references）
- 文件拆分不合理（一个文件塞了多个不相关主题）
- 可维护性问题（硬编码、命名不一致、缺少配置）
- 可以优化但不阻塞（性能优化、代码风格）
- 空目录残留（模板初始化后未清理）
- 触发词可以更丰富
- Provenance 可以进一步清晰
- 数据源描述可以更完善
- 边缘场景的降级策略不够完整

### Failure Mode 相关 P2

- **FM-010 Operationally Impractical**：成本、延迟、资源消耗不合理（如果不阻塞核心路径）
- **FM-013 Overengineering**：问题简单但实现过度复杂

---

## Suggestion — 锦上添花

不影响当前交付。可以在后续版本中改进。

- 可以增加更多异常场景处理
- 可以增加更多触发词
- 可以优化文档表述
- 可以增加单元测试
- 可以增加更多配置选项
- 可以增加更详细的数据来源说明文档

---

## Review 不能变成"无限挑刺"

问题必须和用户目标、核心能力或真实交付质量有明确关系。

不要把"也许未来可以支持更多格式"这种锦上添花的问题升级成 P1/P0。

Reviewer 应区分：

```text
Required for correctness          → P0/P1
Required for reliable real-world  → P1
Useful improvement                → P2
Optional enhancement              → Suggestion
```
