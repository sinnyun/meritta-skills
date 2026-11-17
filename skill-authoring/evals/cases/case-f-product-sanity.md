# Case F: Product Sanity

## 用户需求

做一个商家推荐 Skill，用户描述场景（如"6个人家庭聚餐800元"），Skill 返回推荐结果。

## Skill 实现

使用真实 API、真实数据、真实距离。所有技术路径正确。

但排序算法只按照距离排序，不考虑：
- 用户人数
- 预算
- 聚餐类型
- 商家类型

结果可能返回：便利店、快餐店等。

测试只验证 API 调用和返回格式，全部 PASS。

## 预期结果

**至少 P1。**

- FM-007 Product Sanity Failure
- P1：技术正确但真实用户结果明显不合理
- Product / Human Sanity 评分在低分区（4-8）

## 验证要点

- [ ] skill-review 执行 Human Sanity Check
- [ ] 识别出"如果我是目标用户，结果有用吗？"= NO
- [ ] 产生 P1 问题
- [ ] Product / Human Sanity 评分在低分区
- [ ] 建议排序算法考虑用户场景
- [ ] Ship Decision 不应该是 YES
