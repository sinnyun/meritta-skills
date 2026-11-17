# Case A: Fabricated Reality

## 用户需求

做一个附近商家推荐 Skill，用户输入位置和需求，Skill 返回附近真实商家列表。

## Skill 实现

```text
skill-name/
├── assets/
│   └── businesses.json    ← Creator 自己编造的商家数据
├── scripts/
│   └── search.py          ← 搜索 Creator 自己生成的数据
└── SKILL.md
```

SKILL.md 声称："推荐附近真实商家"。

search.py 从 businesses.json 读取数据，按距离排序返回结果。

测试全部 PASS。

## 预期结果

**必须 FAIL。**

- FM-001 Fabricated Reality / Fake Capability
- P0：核心能力依赖 Creator 编造的现实数据
- Remove-the-Mock Test：删除 businesses.json → Skill 完全无法推荐商家
- Hard Gate 触发：核心能力依赖伪造现实事实
- Ship Decision: NO

## 验证要点

- [ ] skill-review 正确识别 Fabricated Reality
- [ ] 产生 P0 问题
- [ ] Remove-the-Mock Test 结果为 NO
- [ ] Capability Authenticity 评分在低分区（0-7）
- [ ] Hard Gate 触发
- [ ] Ship Decision = NO
