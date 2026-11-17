# 浏览器兼容性规范

目标：生成的工作台在 Chrome/Edge（近 2 年版本）与 iOS Safari 14+、主流 Android WebView 上一次跑通。规则分三档：**允许**（放心用）、**带降级**（可用但必须写 fallback）、**禁止**（换了环境就崩）。

## JS 兼容规则

### 禁止（各端差异大，直接踩坑）

| 禁用项 | 原因 | 替代方案 |
|---|---|---|
| `new Date('YYYY-MM-DD')` | iOS Safari 按 UTC 解析，可能得到前一天；纯数字串返回 Invalid Date | `new Date(y, m-1, d)` 数字构造，或 `'YYYY/MM/DD'` 字符串。骨架的 `todayStr()`/`addDays()` 已封装，一律复用 |
| `crypto.randomUUID()` | iOS 15.4+ 才有 | `Date.now() + Math.random().toString(36).slice(2,6)` |
| `structuredClone()` | iOS 14.5+ 才有 | `JSON.parse(JSON.stringify(x))` |
| `Array.prototype.at()` | iOS 15.4+ 才有 | `arr[arr.length-1]` |
| top-level await | 老引擎直接整段脚本失效 | 包在 async 函数里调用 |
| `??=`、`&&=`、`||=` | iOS 14+ | 普通赋值 + if |
| 弃用的 `document.all`、同步 XHR | — | fetch / 事件委托 |

### 允许（iOS 13.4+/主流安卓全支持）

- `?.` 可选链、`??` 空值合并、`Promise.allSettled`、`Object.fromEntries`、`flat/flatMap`
- `let/const`、箭头函数、模板字符串、解构、扩展运算符、`class`
- `addEventListener`、`IntersectionObserver`、`MutationObserver`
- `localStorage`（全部读写包 try-catch：Safari 隐身模式写入会抛异常）

## CSS 兼容规则

### 禁止

| 禁用项 | 原因 |
|---|---|
| `:has()` 选择器 | 2023 年后才全量支持，老 WebView 直接丢弃整条规则 |
| `100vh` 直接用于关键布局 | iOS 地址栏伸缩导致视口溢出；需要满屏时用 `height:100vh; height:100dvh;` 双写降级 |
| `subgrid`、`text-wrap:balance`、容器查询单位（cqw 等） | 支持率不足 |
| `backdrop-filter` 作为唯一视觉手段 | 必须同时给不透明背景色兜底 |

### 带降级（双写模式：旧值在前，新值在后）

```css
/* aspect-ratio：iOS 15+ 才有，必须给旧引擎留高度 */
.fc-card{ min-height:380px; aspect-ratio:3/4; }

/* flex 布局的 gap：iOS 14.5- 不支持，列表类用 margin 兜底 */
.today-item + .today-item{ margin-top:8px; }  /* 与 gap 二选一或并用 */

/* dvh/svh 同理 */
.page{ min-height:100vh; min-height:100dvh; }
```

### 允许（放心用）

- CSS 自定义属性（变量）、flex、grid（含 `auto-fill`/`minmax`）、`position:sticky`
- `border-radius`、`box-shadow`、`transform`、`transition`、`animation`
- `calc()`、`clamp()`、`min()/max()`、`env(safe-area-inset-*)`（配合 `viewport-fit=cover`）
- `object-fit`、`aspect-ratio`（按上面双写）

## HTML / 交互规则

1. `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">` 必写。
2. 可点元素一律 `<button>`，禁止 `div onclick`——保证键盘可达性与默认 44px 命中区。
3. 输入框 `font-size ≥ 16px`（防 iOS 聚焦自动放大）；数字输入用 `type="number"` + `inputmode="numeric"`。
4. 弹层用页面内 div + `position:fixed`；注意 `transform` 祖先会让 `fixed` 退化为相对定位（翻卡等 3D 组件内的弹层要挂到 body 级）。
5. 触摸目标 ≥44×44px；`-webkit-tap-highlight-color:transparent` + `:active` 态替代 hover 态。
6. `<meta charset="UTF-8">` 与 `<html lang="zh-CN">` 必写。
7. 文件名、id、data-* 一律 ASCII；用户内容插入 DOM 前过 `esc()`。

## 自检方法（生成后必做）

1. **静态**：`node scripts/smoke-test.js <html路径>` —— 内联脚本语法检查 + 外链扫描，任何环境都能跑。
2. **真机冒烟**：同一脚本在 Playwright 环境自动升级为浏览器实测（报错采集/横向溢出/关键容器/截图）。交付前必须两组检查全绿。
