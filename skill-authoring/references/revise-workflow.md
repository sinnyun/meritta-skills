# Revise Skill Workflow

## 前置条件

- Review Report 已生成
- 存在 P0 / P1 问题（或 P2 问题且 Creator 选择修复）

## Step 1: 问题分类

阅读 Review Report，按严重度分类：

- **P0**：阻塞交付的问题。**必须修复，不能跳过。**
- **P1**：重要问题，真实使用存在明显风险。**原则上必须修复**，有特殊情况不修复需明确记录理由。
- **P2**：普通质量问题。**根据修复收益与复杂度判断**，高收益低成本的修复优先做。
- **Suggestion**：锦上添花的建议。**可选择性采纳**，不影响当前交付。

## Step 2: 制定修改计划

按优先级排序修改项：
1. 先修 P0
2. 再修 P1
3. 选择性修 P2
4. Suggestion 视情况

每项修改明确：
- 修改哪个文件
- 具体改什么
- 预期效果

## Step 3: 执行修改

按计划逐项修改。每项修改后记录：
- 修改的文件
- 修改内容摘要
- 对应的问题编号

## Step 4: 重新 Static Validation

修改完成后运行：

```bash
python "$SKILL_ROOT/scripts/validate_skill.py" --skill-path "<目标Skill路径>"
```

- **PASS**：进入下一步
- **FAIL**：修复校验失败项，重新校验

## Step 5: 判断是否需要再次 Review

```text
if review_round < max_review_rounds (默认 2):
    if 仍存在 P0 或 P1 问题:
        → REVIEW（再次评审）
    else:
        → DELIVER
else:
    → DELIVER（已达最大轮数，记录剩余问题）
```

## Step 6: 记录修改摘要

在 `.review/revision-log.md` 中记录：
- 第几轮修改
- 修复了哪些问题
- 哪些问题选择不修复及理由
- 剩余问题
