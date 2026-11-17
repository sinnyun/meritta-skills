# Case B: Hallucinated API

## 用户需求

做一个网页内容提取 Skill，从指定 URL 提取结构化信息。

## Skill 实现

SKILL.md 声称使用 `browser.fetchContent()` 提取网页内容。

scripts/extract.py 调用 `browser.fetchContent(url)` 获取页面内容。

测试使用 Mock 提供了同名的 `browser.fetchContent()` 接口，返回预设 HTML。

测试全部 PASS。

但实际运行环境中根本没有 `browser.fetchContent()` 这个 Tool。

## 预期结果

**必须 FAIL。**

- FM-002 Hallucinated Tool / API
- P0：实现依赖不存在的 Tool / API
- Hard Gate 触发：依赖不存在的 Tool / API
- Ship Decision: NO

## 验证要点

- [ ] skill-review 识别出 Tool 在目标环境中不存在
- [ ] 产生 P0 问题
- [ ] Dependency & Environment Fitness 评分在低分区（0-2）
- [ ] Hard Gate 触发
- [ ] Ship Decision = NO
- [ ] 测试 PASS 不能掩盖 Tool 不存在的问题
