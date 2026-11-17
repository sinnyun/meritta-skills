# 组件目录

每个组件文件是可独立双击预览的完整 HTML。文件内两个标记行之间（`⬇ 组件代码开始` 到 `⬆ 组件代码结束`）为可复制区，包含 `<style>` + `<section>` + `<script>` 三段，直接粘进骨架的模块槽即可。

所有组件依赖骨架 `:root` 提供的设计令牌，并带同值 fallback（`var(--c-primary, #4f6ef7)`），因此脱离骨架也能正常显示。所有组件已内建：空数据不崩、示例数据种子、`wb_` 前缀隔离的独立存储 key（集成进工作台时应把组件内的独立存储改为读写工作台统一 state，避免双份存储）。

## progress-ring — SVG 进度环

- 用途：完成率、正确率、目标达成度等单一百分比指标。
- 配置：`data-label`（环下文案）、`data-color`（可选，覆盖主题色）。
- API：`ProgressRing.set(id, value0to100)` 更新数值，带动画过渡。
- 数据结构：无持久化，由调用方传入数值。

## checkin-matrix — 多习惯打卡矩阵

- 用途：3-5 个习惯 × 最近 7 天的打卡格子。
- 配置：`data-days`（显示天数，默认 7）。
- API：`CheckinMatrix.render(el, habits)`；habits = `[{name, days:{"2026-09-11":true}}]`。
- 交互：点击格子切换打卡；表头自动算连续天数 streak。
- 存储 key：`wb_{id}_habits`。

## calendar-heatmap — 日历热力图

- 用途：按月展示每日完成度深浅（习惯、学习时长、记账笔数等）。
- 配置：`data-month`（YYYY-MM，默认当月）；左右箭头切月。
- API：`Heatmap.render(el, values)`；values = `{"2026-09-11": 3}`，数值 0-4 映射五档色深。
- 存储 key：无（由调用方聚合后传入）。

## trend-chart — SVG 趋势折线图

- 用途：体重、支出、刷题量、平台数据等时间序列。
- 配置：`data-height`（px，默认 160）；自动计算纵轴范围与网格线。
- API：`TrendChart.render(el, points, opts)`；points = `[{x:"9/1", y:62.5}]`；opts = `{unit:"kg", downIsGood:true}`（downIsGood=true 时下降趋势显示绿色箭头）。
- 数据点悬停/点击显示数值气泡；数据少于 2 条时显示空态文案。

## pie-chart — SVG 分类占比环图

- 用途：支出分类、时间分配、错题科目分布等。
- 配置：`data-size`（px，默认 180）。
- API：`PieChart.render(el, items)`；items = `[{label:"餐饮", value:820, color:"#f59e0b"}]`，color 可省略（自动取调色板）。
- 右侧图例自动生成，含金额/数量与百分比；全为 0 时显示空态。

## point-shop — 积分商城

- 用途：完成任务得积分、兑换奖励的激励闭环（育儿/习惯/学习场景通用）。
- 配置：无。
- API：`PointShop.render(el)`；内部状态 = `{points, history, rewards}`。
- 交互：加分按钮（可自定义分数）、兑换按钮（余额不足置灰）、兑换后进入"待确认"由家长/管理员确认；兑换需二次确认。
- 存储 key：`wb_{id}_points`。

## flip-card — 翻卡学习卡

- 用途：识字/单词/知识点的正反面翻转学习（象形字卡片、单词卡）。
- 配置：`data-hint`（正面角标文案，如"第 3 张 / 共 5 张"）。
- API：`FlipCard.load(el, cards)`；cards = `[{front:"日", frontSub:"象形字", back:"rì", backSub:"太阳·日出·日常"}]`。
- 交互：点击翻面（CSS 3D transform）、上一张/下一张、"认识/再看看"双按钮记录掌握度。
- 存储 key：`wb_{id}_cards_progress`。
- 儿童向使用时：外层容器追加 class `kid`（字号放大、按钮 ≥50px）。

## 新组件登记格式

沉淀新组件时按以上格式追加条目：组件名 — 用途 / 配置（data-*）/ API / 交互 / 存储 key / 特殊说明。
