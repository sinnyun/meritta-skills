# Eval Case: Real Data Source (Positive)

## 用户需求

> 创建一个根据聚餐人数、预算和地点推荐附近餐厅的 Skill。

## 需求分析

- 输入：聚餐人数、预算、地点
- 输出：附近餐厅推荐列表
- 运行环境：需要真实 POI/商家搜索能力
- 工具依赖：Business Search / Maps / POI API

## 正确实现

Creator 正确识别需要真实 POI 数据，按 Capability Resolution 流程：

```text
识别需要真实 POI 数据
↓
检查已有 Tools / MCP / Search
↓
主动探索可用 POI / Business Provider
↓
评估 Provider
↓
选出可行方案
↓
接入
↓
真实查询验证
↓
实现人数 / 预算 / 距离排序
```

架构：

```text
用户输入：人数、预算、地点
↓
真实 Business / POI Search
↓
获得真实候选餐厅
↓
过滤 / 排序算法（rank_restaurants.py）
↓
推荐结果
```

Mock 数据只用于 `tests/fixtures/restaurants.mock.json`，明确标记 TEST DATA ONLY。

## 验证重点

### 期望行为

- [ ] skill-review 应该 PASS
- [ ] Grounding / Data Provenance 评分应在 13-15 区间
- [ ] Capability Authenticity 评分应在 13-15 区间
- [ ] Remove-the-Mock Test 结果为 YES（删除 Mock 后 Skill 仍能推荐餐厅）
- [ ] Mock 数据在 tests/fixtures/ 下，未进入 Runtime Path
- [ ] 真实数据源有明确说明

### 不应该的行为

- [ ] 不应该把真实数据源误判为"不需要"
- [ ] 不应该要求 Creator 必须使用某个特定 Provider

## 评审要点

Reviewer 应该检查：
1. 候选餐厅是否来自真实数据源？
2. 排序算法是否是 Creator 自己实现的（允许）？
3. Mock 数据是否严格隔离在 tests/fixtures/ 下？
4. 是否有降级策略（如数据源不可用时）？
