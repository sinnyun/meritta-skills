# Eval Case: Premature Ask User (Negative)

## 用户需求

> 创建一个根据聚餐人数、预算和地点推荐附近餐厅的 Skill。

## 需求分析

- 输入：聚餐人数、预算、地点
- 输出：附近餐厅推荐列表
- 运行环境：需要真实 POI/商家搜索能力
- 工具依赖：Business Search / Maps / POI API

## 故意错误实现

Creator 输出：

> 当前没有餐厅接口，请用户提供 API。

但运行环境实际上存在可发现的 Business/POI Search 能力（如 Web Search、Maps MCP 等）。Creator 未进行任何探索就直接要求用户提供 API。

## 验证重点

### 期望行为

- [ ] skill-review 必须 FAIL / REVISE
- [ ] 至少产生 P1 问题（如果未阻塞核心能力）或 P0（如果阻塞）
- [ ] 问题描述应类似：Creator prematurely asked user for API without attempting discovery, while existing search capability is available.
- [ ] Dependency Resolution Review 应发现 Creator 未尝试探索

### 不应该的行为

- [ ] 不应该因为"Creator 诚实"就 PASS
- [ ] 不应该忽略运行环境中已有的能力

## 评审要点

Reviewer 应该检查：
1. Creator 是否尝试了 Level 1（检查当前环境已有能力）？
2. Creator 是否尝试了 Level 2（检查当前项目已有实现）？
3. Creator 是否尝试了 Level 3（主动探索可接入能力）？
4. 运行环境中是否实际存在可用的 Search / POI 能力？
5. Creator 是否过早将问题推给用户？
