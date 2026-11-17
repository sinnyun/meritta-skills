# Case I: Overengineering

## 用户需求

做一个简单文案改写 Skill，把一段文字改正式一点。

## Skill 实现

```text
skill-name/
├── references/
│   ├── formality-rules.md
│   ├── tone-guidelines.md
│   ├── writing-standards.md
│   ├── style-matrix.md
│   ├── context-adaptation.md
│   └── revision-checklist.md
├── scripts/
│   ├── analyze_text.py
│   ├── transform_tone.py
│   └── validate_output.py
├── assets/
│   └── templates.json
└── SKILL.md
```

6 个 reference、3 个 script、配置系统、数据文件、复杂 workflow。

实际任务只需要一个简单的 SKILL.md 指令就能完成。

## 预期结果

**P2。**

- FM-013 Overengineering
- P2：问题简单但实现过度复杂
- Structure / Context Efficiency 评分受影响

## 验证要点

- [ ] skill-review 识别 Overengineering
- [ ] 产生 P2 问题
- [ ] 指出复杂度与问题复杂度不匹配
- [ ] 建议简化为最小充分实现
- [ ] Structure / Context Efficiency 评分在低分区
- [ ] 不应该升级为 P1/P0（不阻塞核心功能）
