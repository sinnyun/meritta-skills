# Case C: Creator-Test Collusion

## 用户需求

做一个订单数据提取 Skill，从订单 JSON 中提取关键字段（价格、数量、客户名）。

## Skill 实现

Creator 理解 API Schema 时，把 `price_per_person` 误认为是 `price_per_group`。

按错误字段写代码：`order["price_per_group"]`。

按错误字段写 Mock：`{"price_per_group": 100}`。

按错误字段写测试：`assert result["price"] == 100`。

测试全部 PASS。

但真实 API 返回的字段是 `price_per_person`，真实数据中没有 `price_per_group`。

## 预期结果

**必须 FAIL 或 REVISE。**

- FM-004 Creator-Test Collusion
- P0 或 P1：实现和测试建立在同一错误假设上
- Test Oracle Review：测试预期结果本身不可靠
- Creator-Test Collusion 风险高

## 验证要点

- [ ] skill-review 执行 Test Oracle Review
- [ ] 识别出测试只是重复实现逻辑
- [ ] 识别出测试数据由 Creator 自己构造
- [ ] Evidence & Test Validity 评分在低分区（0-3）
- [ ] 建议使用真实 API Schema 验证
- [ ] 建议独立挑战用例验证
