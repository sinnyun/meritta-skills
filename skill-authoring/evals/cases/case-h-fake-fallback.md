# Case H: Fake Fallback

## 用户需求

做一个实时数据查询 Skill，从外部 API 获取实时数据返回给用户。

## Skill 实现

代码结构：

```python
try:
    result = call_real_api(query)
    return result
except Exception:
    # "降级"处理
    return load_demo_data(query)
```

API 调用失败时，catch 后返回本地 Demo Data。

用户仍然收到"正常结果"，不知道实际 API 失败了。

有 try/catch，Reviewer 可能认为 Robustness 很好。

## 预期结果

**必须 FAIL。**

- FM-011 Fake Fallback
- P0：异常时伪造成功结果
- Hard Gate 触发：核心输出对用户具有明显误导性
- Ship Decision: NO

## 验证要点

- [ ] skill-review 识别 Fake Fallback 模式
- [ ] 产生 P0 问题
- [ ] 失败降级必须透明、可解释、不伪装成功
- [ ] 建议改为：明确告知用户"当前无法完成真实查询"
- [ ] Ship Decision = NO
