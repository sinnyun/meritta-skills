# Eval Case: Weather Outfit Scenario Coverage (Positive)

## 用户需求

> 创建一个根据城市和天气提供穿搭建议的 Skill。

## 需求分析

- 输入：城市名称（required）、日期/日期范围（optional）
- 输出：穿搭建议
- 运行环境：需要真实天气 API
- 工具依赖：Weather API / Web Search
- 自然使用维度：时间（即时 vs 未来 vs 范围）、地点、使用目的

## 正确实现

Creator 正确识别了天气穿搭的自然使用维度，合理设计了 date/date-range 支持：

```text
weather-outfit/
├── SKILL.md          ← Description: "根据城市和天气提供穿搭建议，支持当前和未来天气查询"
├── scripts/
│   └── get_outfit.py  ← city: required, date/date-range: optional
└── tests/
    ├── test_current.py    ← 测试 "深圳今天怎么穿？" → current weather
    ├── test_forecast.py   ← 测试 "下周三去北京出差怎么穿？" → forecast
    └── test_range.py      ← 测试 "未来4天去成都旅游需要带什么衣服？" → multi-day forecast + packing advice
```

行为设计：
```text
无日期
→ current weather
→ 当前穿搭建议

指定日期
→ forecast
→ 未来某天穿搭建议

日期范围
→ multi-day forecast
→ 多天穿搭建议 + 打包清单
```

不要求无限扩展。Creator 只覆盖了自然、高概率、属于用户核心目标的场景。

## 验证重点

### 期望行为

- [ ] skill-review 应该 PASS
- [ ] Scenario Coverage 检查通过：日期/日期范围属于自然使用维度，Creator 已合理支持
- [ ] Scenario Expansion Challenge 通过：Reviewer 挑战的场景 Skill 能处理
- [ ] Claim 与实际能力一致：Description 声明覆盖当前和未来天气，实现确实覆盖
- [ ] FM-005 不触发：测试覆盖了多个自然使用场景，不只是一个默认场景
- [ ] 数据来源真实：天气数据来自真实 API，非 Creator 编造

### 不应该的行为

- [ ] 不应该因为 Creator 没有覆盖"所有可能的时间场景"而拒绝（不要求无限扩展）
- [ ] 不应该把合理的 optional 参数设计误判为"能力不足"
- [ ] 不应该要求 Creator 必须支持月度预报等小概率场景
- [ ] 不应该过度挑刺

## 评审要点

Reviewer 应该检查：
1. Skill 是否合理支持了日期/日期范围参数？
2. 无日期时是否正确降级为 current weather？
3. 指定日期时是否正确查询 forecast？
4. 日期范围时是否提供 multi-day forecast + packing advice？
5. Description 中的能力声明是否与实际能力一致？
6. 测试是否覆盖了多个自然使用场景（不只是一个默认场景）？
7. 天气数据是否来自真实数据源？
