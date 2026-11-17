# Eval Case: Complex Skill

## 用户需求

> 创建一个通过浏览器分析参考网站 Design Token，并应用到目标项目的 Skill

## 需求分析

- 输入：参考网站 URL + 目标项目路径
- 输出：修改后的目标项目样式
- 运行环境：本地 Node.js + 浏览器
- 工具依赖：playwright-cli（浏览器操作）、Node.js（脚本）

## 验证重点

### 应该做到的

- [ ] 正确拆分多阶段 Workflow（分析 → 提取 → 迁移 → 校准）
- [ ] 合理使用 browser/tool/script/reference：
  - 浏览器操作用 playwright-cli 命令
  - 样式统计用 Node.js 脚本
  - 设计规范用 references
  - 视觉差异分析用模型判断
- [ ] SKILL.md Context 控制在合理范围（2000-4000 字）
- [ ] references/ 包含详细的设计规范和评分标准
- [ ] scripts/ 包含确定性操作脚本
- [ ] Progressive Loading 合理（SKILL.md 只含核心工作流，详细规则在 references）

### 不应该做的

- [ ] 不应该把所有内容塞进 SKILL.md
- [ ] 不应该用模型做确定性操作（如截图、文件解析）
- [ ] 不应该缺少异常处理（浏览器启动失败、页面加载超时）
- [ ] 不应该创建不必要的目录

## 评审要点

Reviewer 应该检查：
1. 是否正确拆分 Workflow（多阶段）
2. 是否合理分配 Tool / Script / Model
3. SKILL.md Context 是否高效
4. references 是否聚焦
5. scripts 是否可运行
6. 异常场景是否考虑完整
7. Reviewer 是否能发现架构问题（如过度设计或设计不足）
