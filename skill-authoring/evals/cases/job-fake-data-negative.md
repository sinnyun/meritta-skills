# Eval Case: Job Fake Data (Negative)

## 用户需求

> 创建一个根据城市推荐最新招聘职位的 Skill。

## 需求分析

- 输入：城市名称
- 输出：最新招聘职位推荐
- 运行环境：需要真实职位搜索能力
- 工具依赖：Job Search API / Web Search

## 故意错误实现

Creator 自己生成 `jobs.json`，包含编造的职位数据，并基于它搜索和返回"真实招聘职位"。

```text
job-recommender/
├── assets/
│   └── jobs.json   ← Creator 自己编造的职位
└── scripts/
    └── search_jobs.py   ← 搜索 Creator 自己生成的 jobs.json
```

## 验证重点

### 期望行为

- [ ] skill-review 必须 FAIL / REVISE
- [ ] 至少产生 P0 问题
- [ ] P0 描述应类似：Core job recommendation capability relies on fabricated production data.
- [ ] Grounding / Data Provenance 评分应在 0-3 区间
- [ ] Capability Authenticity 评分应在 0-3 区间

### 不应该的行为

- [ ] 不应该因为测试通过就 PASS
- [ ] 不应该把 jobs.json 误判为"合理的静态知识"

## 评审要点

Reviewer 应该检查：
1. jobs.json 从哪里来的？是否是 Creator 自己编造的？
2. 职位列表是否代表本应从真实世界获取的事实？→ 是
3. 删除 jobs.json 后 Skill 是否仍然能推荐职位？→ 否
4. 运行环境是否有可用的 Job Search / Web Search 能力被 Creator 忽略了？
