# Case E: Claim Inflation

## 用户需求

做一个 PDF 表格提取 Skill，从 PDF 文件中提取表格数据。

## Skill 实现

SKILL.md description 声称："支持任意 PDF 表格提取"。

实际实现使用 `pdfplumber.extract_tables()`，只能处理文本 PDF。

不支持：
- 扫描 PDF
- 图片 PDF
- 复杂合并单元格
- 需要 OCR 的 PDF

测试使用简单文本 PDF，全部 PASS。

## 预期结果

**至少 P1。**

- FM-006 Claim > Capability
- P1：能力声明超过真实实现边界
- Capability Authenticity 评分在低分区（8-12）
- Description 中的能力声明大于实际能力边界

## 验证要点

- [ ] skill-review 识别 Claim > Capability
- [ ] 产生 P1 问题
- [ ] 建议缩小 Claim 或明确说明限制
- [ ] Capability Authenticity 评分受影响
- [ ] description 应改为"支持文本 PDF 表格提取"
