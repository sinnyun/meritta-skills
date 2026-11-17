# Case D: Happy Path

## 用户需求

做一个文件格式转换 Skill，用户描述要转换的格式，Skill 完成转换。

## Skill 实现

Skill 只支持高度结构化输入：

```text
输入格式: 将 {文件路径} 转换为 {目标格式}
```

测试全部使用这种理想结构化输入，全部 PASS。

但真实用户会说：

```text
把这个文件转成 PDF
帮我改一下格式
这个能不能变成 Word？
```

Skill 无法处理。

## 预期结果

**至少 P1。**

- FM-005 Happy Path Overfit
- P1：只处理理想结构化输入
- Real-world Robustness 评分在低分区（4-8）

## 验证要点

- [ ] skill-review 识别 Happy Path Overfit
- [ ] 产生 P1 问题
- [ ] Real-world Robustness 评分在低分区
- [ ] Independent Challenge 用自然语言输入测试
- [ ] 建议增加自然语言解析能力
