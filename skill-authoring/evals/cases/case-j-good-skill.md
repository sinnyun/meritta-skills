# Case J: Good Skill

## 用户需求

做一个代码格式化 Skill，读取代码文件，按团队规范格式化后输出。

## Skill 实现

- SKILL.md 精简，只包含核心工作流和资源导航
- 使用真实 `prettier` CLI 工具（目标环境已安装）
- 团队规范放在 `references/team-rules.md`（静态知识，适合内置）
- 格式化脚本 `scripts/format.py` 可独立运行，有明确输入输出和错误处理
- 测试使用真实代码文件（非 Mock 数据）
- Description 准确描述能力边界："使用 prettier 按团队规范格式化代码"
- 能力声明不大于实际实现
- 异常处理：prettier 不存在时明确告知用户
- 复杂度与问题复杂度匹配

## 预期结果

**必须 PASS。**

防止 Reviewer 变成"什么东西都不敢放行"。

- 无 P0/P1 问题
- 无 Hard Gate 触发
- Ship Decision: YES
- 总分 >= 85

## 验证要点

- [ ] skill-review 正确通过高质量 Skill
- [ ] 无 P0 问题
- [ ] 无 P1 问题
- [ ] Hard Gate 全部 PASS
- [ ] Ship Decision = YES
- [ ] 总分 >= 85
- [ ] Verdict = PASS
- [ ] 不应该过度挑刺
