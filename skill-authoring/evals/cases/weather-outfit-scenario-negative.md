# Eval Case: Weather Outfit Scenario Coverage (Negative)

## 用户需求

> 创建一个根据城市和天气提供穿搭建议的 Skill。

## 需求分析

- 输入：城市名称
- 输出：穿搭建议
- 运行环境：需要真实天气 API
- 工具依赖：Weather API / Web Search
- 自然使用维度：时间（即时 vs 未来 vs 范围）、地点（当前城市 vs 其他城市）、使用目的（日常 vs 出差 vs 旅游）

## 故意错误实现

Creator 只实现了"当前天气穿搭"查询，无意识缩窄了能力范围：

```text
weather-outfit/
├── SKILL.md          ← Description: "根据城市和天气提供穿搭建议"
├── scripts/
│   └── get_outfit.py  ← 只接收 city，只查询 current weather
└── tests/
    └── test_outfit.py ← 只测试 "深圳今天怎么穿？"
```

关键问题：
- 只接收 city 参数
- 只查询 current weather
- 只支持此时此刻穿什么
- 无 date 参数
- 无 date range 参数
- Skill Description 没有明确限制"仅支持当前天气"
- Creator 只测试了一个默认场景

## 验证重点

### 期望行为

- [ ] skill-review 必须 FAIL / REVISE
- [ ] 至少产生 P1 问题
- [ ] P1 描述应涉及：Usage Scenario Overfit / Default Time Assumption / Claim > Capability
- [ ] FM-005 (Happy Path Overfit) 应被识别，覆盖 Usage-scenario Overfit 和 Default-value Overfit
- [ ] Scenario Expansion Challenge 应发现：日期/日期范围属于自然使用维度但 Skill 完全不支持

### 不应该的行为

- [ ] 不应该因为数据真实、测试通过就 PASS
- [ ] 不应该忽略"下周出差怎么穿""未来几天旅游带什么衣服"等自然使用场景
- [ ] 不应该把"只支持当前天气"误判为合理的默认值（因为 Description 没有明确限制）
- [ ] 不应该要求 Creator 必须支持所有未来时间场景（但至少应明确声明限制或扩展能力）

## 评审要点

Reviewer 应该检查：
1. 用户需求是"根据城市和天气提供穿搭建议"，天气穿搭的自然使用维度包括时间（即时/未来/范围）
2. Creator 是否无意识地把时间维度固定成了"当前"？
3. Description 没有明确限制"仅支持当前天气"，但实际能力只支持当前天气 → Claim > Capability
4. Reviewer 的 Scenario Expansion Challenge 应主动挑战：
   - "下周三去北京出差怎么穿？"
   - "未来4天去成都旅游需要准备什么衣服？"
5. 如果 Skill 完全无法处理这些自然场景，且 Description 未明确限制，不应 PASS
