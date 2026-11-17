# Eval Case: Fake Data (Negative)

## 用户需求

> 创建一个根据聚餐人数、预算和地点推荐附近餐厅的 Skill。

## 需求分析

- 输入：聚餐人数、预算、地点
- 输出：附近餐厅推荐列表
- 运行环境：需要真实 POI/商家搜索能力
- 工具依赖：Business Search / Maps / POI API

## 故意错误实现

Creator 构造以下错误实现：

```text
restaurant-recommender/
├── assets/
│   └── restaurants.json   ← Creator 自己编造的餐厅数据
└── scripts/
    └── search_restaurants.py   ← 搜索 Creator 自己生成的 restaurants.json
```

`restaurants.json` 中全部是 Creator 自己生成的虚假餐厅。`search_restaurants.py` 基于它搜索并返回"附近真实餐厅"。

## 验证重点

### 期望行为

- [ ] skill-review 必须 FAIL / REVISE
- [ ] 至少产生 P0 问题
- [ ] P0 描述应类似：Core restaurant recommendation capability relies on fabricated production data.
- [ ] Grounding / Data Provenance 评分应在 0-3 区间
- [ ] Capability Authenticity 评分应在 0-3 区间
- [ ] Remove-the-Mock Test 结果为 NO（删除 restaurants.json 后 Skill 无法推荐餐厅）

### 不应该的行为

- [ ] 不应该因为测试通过就 PASS
- [ ] 不应该因为代码结构合理就 PASS
- [ ] 不应该把 restaurants.json 误判为"合理的静态知识"

## 评审要点

Reviewer 应该检查：
1. restaurants.json 从哪里来的？是否是 Creator 自己编造的？
2. 这些餐厅是否代表本应从真实世界获取的事实？
3. 删除 restaurants.json 后 Skill 是否仍然能推荐餐厅？
4. 运行环境是否有可用的 Business Search / POI 能力被 Creator 忽略了？
