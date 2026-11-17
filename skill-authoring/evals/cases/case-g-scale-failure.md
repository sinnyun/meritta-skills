# Case G: Scale Failure

## 用户需求

做一个代码分析 Skill，分析代码仓库的结构和依赖关系。

## Skill 实现

测试使用 100 行代码的小文件，全部 PASS。

实际使用时，Skill 将全部代码文件内容加载进 LLM Context。

10 万行代码仓库会导致 Context 溢出、超时或内存不足。

没有规模限制说明。

## 预期结果

**至少 P1。**

- FM-009 Scale Failure
- P1：Demo 规模可运行，真实规模不可运行
- Real-world Robustness 评分受影响

## 验证要点

- [ ] skill-review 检查真实规模下的行为
- [ ] 产生 P1 问题
- [ ] 识别出大规模数据全部加载进 Context
- [ ] 建议增加规模限制或分批处理
- [ ] Real-world Robustness 评分在低分区
