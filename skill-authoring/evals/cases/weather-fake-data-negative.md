# Eval Case: Weather Fake Data (Negative)

## 用户需求

> 创建一个查询未来天气的 Skill。

## 需求分析

- 输入：城市名称
- 输出：未来天气预报
- 运行环境：需要真实天气 API
- 工具依赖：Weather API / Web Search

## 故意错误实现

Creator 自己生成 `weather.json`，包含编造的天气数据，并基于它返回"实时天气"。

```text
weather-query/
├── assets/
│   └── weather.json   ← Creator 自己编造的天气数据
└── scripts/
    └── get_weather.py   ← 读取 Creator 自己生成的 weather.json
```

## 验证重点

### 期望行为

- [ ] skill-review 必须 FAIL / REVISE
- [ ] 至少产生 P0 问题
- [ ] P0 描述应类似：Core weather query capability relies on fabricated production data.
- [ ] Grounding / Data Provenance 评分应在 0-3 区间（动态数据冒充）
- [ ] Capability Authenticity 评分应在 0-3 区间

### 不应该的行为

- [ ] 不应该因为测试通过就 PASS
- [ ] 不应该把 weather.json 误判为"合理的静态知识"
- [ ] 不应该忽略动态数据的 Freshness 问题

## 评审要点

Reviewer 应该检查：
1. weather.json 从哪里来的？是否是 Creator 自己编造的？
2. 天气数据是否代表动态现实数据？→ 是，需要 Freshness
3. 删除 weather.json 后 Skill 是否仍然能查询天气？→ 否
4. 是否存在静态数据冒充动态数据的问题？→ 是
