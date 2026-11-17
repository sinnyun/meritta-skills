# Web Access & Tool Selection 指导
> 条件性加载：仅当 Skill 涉及 Web、Browser、Network、Search、Fetch、API、MCP、CLI 或网页自动化时阅读。
> 本文件只规定 Web / Browser 能力选择、Session、Runtime、安装与 Fallback。
> 事实真实性、来源与 Freshness 由 grounding 规则处理；Capability Gap 由对应能力规则处理。

## 核心原则
- Capability First：先判断需要什么能力。
- Browser-capable by Default：泛化网页任务默认具备真实 Browser 能力。
- Playwright CLI Preferred：Browser 场景默认优先 Playwright CLI。
- Reuse Before Recreate：优先复用已有 Session、Browser 与 Tool。
- Structured Before UI：结构化系统优先 API / Connector / CLI / MCP。
- Static Fetch Is Fast Path：Fetch 只用于明确静态页面。
- Correct Install Path：CLI 与 Browser Binary 分开安装。
- Fallback Preserves Claim：降级不能改变原 Capability Claim。
- Verify Before Claim：关键能力必须由真实执行验证。
- 目标是“最小充分能力”，不是“最少依赖”。

## 1. Tool 选择顺序
先把任务归类为 Search、Structured Access、Static Fetch 或 Browser。
- 只搜索公开信息、找官方页面、查最新资料：优先 Search。
- 已有稳定结构化接口：优先 API / Connector / SDK / CLI / MCP。
- 已确认公开静态 HTML：可用 Fetch / HTTP。
- 需要 JS、Session、Login、UI、Visual State：进入 Browser。
  不得只因为某个 Tool 调用更简单就降低任务能力。
  不得把 Search 结果当作登录后页面或真实 UI 的等价替代。

## 2. 泛化网页 Skill 默认 Browser-capable
以下 Claim 默认按 Browser-capable 设计：
- 网页分析、网页内容提取、网页转 Markdown。
- 网页视觉分析、网页 CSS / Design Token 提取。
- 网页临摹、网页风格迁移、网页自动化、网站信息采集。
  只有用户或任务明确限定时，才可缩小到静态访问。
  可缩小的典型条件：公开 HTML、无需 JS、无需登录、无需 Session、无需真实视觉状态。
  现实网页可能依赖 SPA、Lazy Loading、Cookie、LocalStorage、SSO、动态 DOM、Computed Style 与交互。
  单个静态 Demo 不能决定整个 Skill 的能力边界。
  不得把泛化网页 Skill 因 Demo 可 Fetch 而改成 Fetch-only。

## 3. 不需要 Browser 的场景

### Search
目标只是搜索公开信息、发现资料或定位官方页面时使用 Search Tool。
Search 负责发现，不负责模拟真实登录态或 UI 状态。

### Structured Access
目标系统已有 Official API、Connector、SDK、CLI 或 MCP 时优先使用结构化接口。
典型场景包括 GitHub、邮箱、Calendar、数据库与云服务。
不要无理由通过网页 UI 操作已有稳定结构化接口的系统。

### Static Fetch
只有同时满足以下条件时，Fetch / HTTP 才可作为主路径：
- 公开 URL。
- 无需登录、Cookie、Session。
- 无需 JavaScript Render。
- HTTP Response 已包含完整目标内容。
- 不依赖真实视觉状态。
  Fetch 是明确静态页面的优化路径，不是泛化网页架构。

## 4. 必须进入 Browser 的场景
核心能力涉及以下任意一项时使用 Browser：
- JavaScript Rendering、Rendered DOM。
- CSSOM、getComputedStyle、真实视觉状态。
- Cookie、LocalStorage、Session、Login、SSO。
- Click、Fill、Scroll、Drag、Multiple Tabs。
- Lazy Loading、UI Upload / Download、Screenshot。
- 需要验证真实页面行为。
  以下任务默认走 Browser：网页视觉分析、网页风格迁移、CSS Token 提取、登录后读取、SPA 提取、真实 UI 验证。

## 5. Browser 默认实现：Playwright CLI
对于 Coding Agent / Skill Runtime，Browser Capability 默认优先 Playwright CLI。
不要混淆 `@playwright/cli`、`playwright` 与 `@playwright/test`。
Playwright CLI Package 是 `@playwright/cli`。
命令是 `playwright-cli`。
CLI 缺失时执行：
`npm install -g @playwright/cli@latest`
安装后验证：
`playwright-cli --help`
不要为了 CLI 安装 `playwright`。
不要为了 CLI 安装 `@playwright/test`。
只有需要直接编写 Playwright API Code 时才使用 `playwright`。
只有任务本身是 Playwright Test Framework 时才使用 `@playwright/test`。

## 6. Browser 任务启动顺序
Step 1：检测全局 CLI。
`playwright-cli --help`
成功则直接复用，不安装任何东西。
Step 2：检查项目是否已有 Playwright。
`npx --no-install playwright --version`
如果已有，可复用现有项目能力。
检测时不得使用会隐式联网安装 Package 的 `npx` 命令。
Step 3：两者都不存在时安装 CLI。
`npm install -g @playwright/cli@latest ; playwright-cli --help`
不得用 `npm install playwright` 或 `npm install @playwright/test` 替代。

## 7. CLI 与 Browser Binary 分开处理
安装 `@playwright/cli` 只解决 CLI Capability。
CLI 安装成功不等于 Browser Binary 已安装。
不要在安装 CLI 后机械下载 Chromium。
先解析当前环境已有 Browser，再决定是否安装 Browser Binary。
Correct Install Path 是硬规则，不得为了省步骤混用项目 Playwright 安装流程。

## 8. Browser Runtime 复用优先级
按以下顺序获取 Browser Capability：
1. 已打开且可复用的 Browser 实例。
2. 已登录的 Chrome / Edge，可直接 Attach。
3. Persistent Profile / Saved Storage State。
4. 系统已安装 Chrome。
5. 系统已安装 Edge。
6. 都不存在时再安装 Playwright CLI Browser。
   不要一开始就下载新的 Chromium。
   Reuse Before Recreate。

## 9. 优先复用已登录 Browser
涉及登录后网站、企业内部系统、GitHub、SSO、2FA 或已有账号状态时，优先 Attach 当前 Chrome / Edge。
Chrome 示例：
`playwright-cli attach --cdp=chrome`
Edge 示例：
`playwright-cli attach --cdp=msedge`
目标 Browser 需要允许 Remote Debugging。
如果环境配置了 Playwright Browser Extension，也可使用 Extension Attach。
登录页面出现时优先解决 Authentication / Session，不要重装 Browser。
不要新开匿名 Browser 后要求用户无理由重复登录。

## 10. Persistent Profile 与 Storage State
无法直接 Attach 但需要保持登录态时，使用 Persistent Profile 或 Storage State。
Persistent Session 示例：
`playwright-cli open https://example.com --persistent`
Storage State 使用 `state-save` / `state-load` 保存和恢复 Cookie / Storage。
需要人工 SSO、2FA、扫码、CAPTCHA 或设备确认时：
1. 打开 Browser。
2. 用户完成一次认证。
3. 保存或保持 Session。
4. 后续继续复用。
   不要反复重新认证。
   不要声称已经绕过 CAPTCHA、2FA 或其他认证挑战。

## 11. 优先使用系统 Chrome / Edge
需要新 Browser Session 且无需复用现有 Browser 时，优先使用系统浏览器。
Chrome：
`playwright-cli open https://example.com --browser=chrome`
Edge：
`playwright-cli open https://example.com --browser=msedge`
这样可以避免无必要下载 Playwright-managed Browser Binary。
只有系统 Browser 不可用且核心能力确实需要 Browser 时才进入安装路径。

## 12. 确实没有 Browser 时才安装
只有确认以下条件后才安装 Browser：
- 没有可复用 Session。
- 没有可 Attach Browser。
- 没有可用 Persistent Profile / Storage State。
- 没有系统 Chrome / Edge。
- 核心 Capability 确实需要 Browser。
  默认安装：
  `playwright-cli install-browser`
  指定 Browser：
  `playwright-cli install-browser firefox`
  仅在需要 Linux System Dependencies 时：
  `playwright-cli install-browser --with-deps`
  不得替换成 `npx playwright install chromium` 或 `npx playwright install`。
  当前安装目标是 Playwright CLI 所使用的 Browser，不是新建 Playwright Project Runtime。

## 13. 不依赖隐式 Browser 下载
Playwright CLI 首次运行可能触发 Browser 下载，但不要把隐式下载作为最佳实践。
隐式下载会带来未知网络耗时、代理问题、长时间卡住和不透明行为。
正确流程：先解析现有 Browser → 优先系统 Chrome / Edge → 确实没有 → 显式 `playwright-cli install-browser`。
Browser 安装失败后不要无限重试。
不要失败后改成 `npm install playwright` 或 `npx playwright install chromium`。
优先检查 Network、Proxy、VPN、Certificate、Registry / Download Source、Permission。
必要时使用其他已存在的 Browser Provider。

## 14. Browser MCP / Managed Browser
如果 Runtime 已提供 Browser MCP、Managed Browser 或其他成熟 Browser Tool，可以直接复用。
默认 Browser Best Practice 仍然是 Playwright CLI。
其他 Provider 属于 Alternative / Runtime-specific Provider。
不要为了使用备选 Provider 而降低核心 Capability。
不要把 Search、缓存截图或静态 HTML 冒充真实 Browser Runtime。

## 15. 网页转 Markdown
泛化“网页 → Markdown”默认 Browser-capable。
推荐主路径：Playwright CLI → 打开真实页面 → 必要时复用 Session / Login → 获取 Rendered DOM → Cleanup → Markdown。
Browser 负责 Access、Rendering、Authentication、Session。
转换逻辑负责 Main-content Extraction 与 Markdown Conversion。
只有明确证明页面公开、静态、无需 JS、无需登录、HTTP 内容完整时，才可用 Fetch Fast Path。
静态路径：Fetch → HTML Cleanup → Markdown。
不得因为一个 Demo 页面可 Fetch，就把泛化网页转 Markdown 实现成 requests-only。

## 16. 禁止静态 HTTP 冒充 Browser

如果核心 Capability 需要 JS Rendering、Session、Authentication、Rendered DOM 或真实网页状态，不得用静态 HTTP 方案声称等价能力。
禁止仅靠 `requests` / `urllib` + BeautifulSoup + 自行管理 Cookie 冒充 Browser Runtime。
Python / Node Script 可以负责数据清洗、Markdown Conversion、Token 聚合、结构化处理与算法。
静态脚本不能替代真实 Browser Rendering、Session 与 UI 行为。
不得为了依赖更少、安装更简单或代码更短而牺牲 Capability。

## 17. CSS / Design Token 提取

只读取 CSS Source、CSS Variables 或 Stylesheet 时，可使用静态 CSS Parser。
如果 Claim 是实际视觉 Token、网页风格分析、网页临摹或风格迁移，默认使用真实 Browser。
推荐链路：Playwright CLI → Rendered Page → DOM / CSSOM → getComputedStyle → Representative Sampling → Token Aggregation → Screenshot Verification。
CSS-in-JS、Runtime Theme、Inheritance、Media Query、Dynamic Class 与 Component State 可能改变最终视觉状态。
因此 CSS Source 不等于最终视觉结果。
实际视觉 Claim 必须基于真实 Rendered Page 验证。

## 18. 访问失败先分类

禁止采用“访问失败 → 重装 Playwright”的机械处理。
至少区分：
- Playwright CLI Missing / Browser Missing。
- Network Unreachable / DNS / Proxy / VPN。
- TLS / Certificate / Permission。
- Authentication Missing / Authorization Denied。
- CAPTCHA / 2FA / Website Challenge。
- Rate Limit / Timeout。
- Content Not Rendered / Lazy Loading / JS State。
  出现 `/login` 通常表示 Authentication Missing，而不是安装失败。
  企业内网页面打不开时优先检查 VPN、Proxy、DNS、Certificate 与 Permission。
  内容未渲染时优先检查 JS、等待条件、Lazy Loading 与页面状态。
  不要用“重装”替代故障分类。

## 19. Fallback 必须保持 Capability Claim

Fallback must preserve the Capability Claim。
可接受：Browser 失败，但确认目标本身是公开静态页面 → Fetch → Markdown。
不可接受：登录后网页访问不了 → 搜索截图 → 猜 CSS Token → 当成真实 Token。
如果降级后只能提供 Partial、Approximate 或 Unavailable，必须明确告诉调用方。
不得用推测、缓存或二手内容伪装成当前真实页面结果。
不得用能力更弱的路径悄悄替换原 Claim。

## 20. Verification

涉及真实网页行为、登录态、视觉状态或动态内容的 Claim，都要用真实执行验证。
能打开 URL 不等于目标内容已渲染。
能看到 DOM 不等于视觉 Token 已正确提取。
能安装 CLI 不等于 Browser Runtime 已可用。
能下载 Browser 不等于 Authentication 已解决。
验证对象必须与 Claim 对齐。
不能验证时明确说明限制，不得伪造成功。

## 21. Tooling 信息要考虑时效性

Playwright CLI、Playwright MCP、Browser Provider、安装命令、版本、Session / Attach 能力都可能变化。
新增或修改 Browser Tooling 且允许联网时，优先查看当前官方文档、官方 Repository 与当前 Release。
不要根据模型旧知识自动生成安装方案。
官方命令与本文冲突时，先确认当前官方状态，再更新 Skill 规则。
时效性验证不改变本文件的 Capability First 与 Fallback Preserves Claim 原则。

## 22. 决策速查

- 只搜索公开信息 → Search。
- 已有结构化接口 → API / Connector / CLI / MCP。
- 明确公开静态页面 → Fetch Fast Path。
- 需要 JS / Login / Session / UI / Visual → Browser。
- Browser 默认 → Playwright CLI。
- 已有 Session → 复用。
- 已登录 Chrome / Edge → Attach。
- 有 Persistent Profile / State → 复用。
- 有系统 Chrome / Edge → 直接使用。
- 都没有且必须 Browser → `playwright-cli install-browser`。
- 失败 → 先分类，再修复。
- 降级 → 不得改变 Capability Claim。

# Hard Rules

1. **泛化网页 Skill 默认 Browser-capable。**
2. **Playwright CLI 是 Browser 场景默认最佳实践。**
3. **Playwright CLI Package 是 `@playwright/cli`，不是 `playwright`。**
4. **CLI 缺失时使用 `npm install -g @playwright/cli@latest`。**
5. **不得为了获得 CLI 而执行 `npm install playwright`。**
6. **不得为了获得 CLI 而执行 `npm install @playwright/test`。**
7. **优先复用已有 Session，而不是重复启动 Browser。**
8. **登录态优先复用已登录 Chrome / Edge、Persistent Profile 或 Storage State。**
9. **优先使用系统已有 Chrome / Edge。**
10. **只有确实没有可用 Browser 时才安装 Browser Binary。**
11. **安装 Browser 使用 `playwright-cli install-browser`。**
12. **不得用 `npx playwright install chromium` 作为 Playwright CLI Browser 安装方案。**
13. **不要依赖首次运行时隐式 Browser 下载。**
14. **Fetch 只作为明确静态页面 Fast Path。**
15. **不得因 Fetch Fast Path 让泛化网页 Capability 退化。**
16. **不得用 requests / urllib 冒充 Browser Rendering / Session 能力。**
17. **结构化系统优先 API / Connector / CLI / MCP，不无理由操作网页 UI。**
18. **Browser MCP / Managed Browser 可作为备选，但不得降低 Capability。**
19. **访问失败先判断 Tool / Browser / Network / Authentication / Content State。**
20. **禁止把 Authentication Missing 当成 Browser 安装失败。**
21. **Fallback 必须保持原 Capability Claim。**
22. **无法保持 Claim 时必须明确标注 Partial / Approximate / Unavailable。**
23. **视觉与 CSS Token Claim 必须基于真实 Rendered Page。**
24. **网页转 Markdown 的泛化实现默认 Browser-capable。**
25. **禁止以单个静态 Demo 推导整个 Skill 应为 Fetch-only。**
26. **CLI 安装与 Browser Binary 安装必须分开判断。**
27. **不要为了“依赖更少”牺牲登录、Session、JS 或真实 UI 能力。**
28. **所有关键 Capability Claim 必须由真实执行验证。**
29. **Tool、Provider 与安装命令存在时效性，修改前优先核对当前官方文档。**
30. **环境已有能力足够时坚持 Reuse Before Recreate。**

# Copy-Paste Patterns

以下模式从已验证的 Skill 中提取，可直接使用。

## Pattern 1：检测与安装

```bash
# Step 1：检测 CLI 是否已存在
playwright-cli --version

# Step 2：不存在时安装（两步，不要跳过第二步）
npm install -g @playwright/cli
playwright-cli install
```

`playwright-cli install` 自动检测系统 Chrome，有则复用，无则下载。
不要执行 `pip install playwright`。不要执行 `playwright install chromium`。

## Pattern 2：打开页面 + 截图

```bash
playwright-cli open "<url>"
playwright-cli resize 1440 900
playwright-cli screenshot --full-page --filename "output/screenshot.png"
playwright-cli close
```

## Pattern 3：运行 JS 提取数据

将提取逻辑写成 JS 文件，通过 `eval` 在浏览器上下文中执行：

```bash
# JS 文件返回数据，--filename 将结果保存为 JSON
playwright-cli eval "$(cat "$SKILL_ROOT/scripts/extract-data.js")" --filename "output/data.json"
```

JS 文件格式（导出为函数，在浏览器上下文执行）：

```javascript
// extract-data.js — 在浏览器上下文中执行
() => {
  // 使用 document、window 等浏览器 API
  const data = { /* ... */ }
  return data  // 返回值自动序列化为 JSON
}
```

## Pattern 4：同一任务内浏览器复用

同一任务中多个操作复用同一浏览器实例（`open` 后不 `close`，后续命令直接作用于当前页面）：

```bash
playwright-cli open "https://example.com"
playwright-cli goto "https://example.com/page2"
playwright-cli eval "$(cat script.js)" --filename "output.json"
playwright-cli screenshot --filename "output.png"
playwright-cli close
```

## Pattern 5：数据后处理（Node.js 脚本）

浏览器操作产出 JSON 后，用 Node.js 脚本做数据处理：

```bash
node "$SKILL_ROOT/scripts/process-data.mjs" --input "output/raw.json" --output "output/summary.json"
```

数据处理脚本用 Node.js（`fs`、`path` 等标准库），不引入 Python。

## 常见场景模板

### 网页转 Markdown

```text
Browser 负责：Access、Rendering、Session → playwright-cli open / eval / close
脚本负责：HTML → Markdown 转换 → Node.js 脚本（turndown / markdown-it）
```

```bash
# 1. 用 playwright-cli 获取渲染后 HTML
playwright-cli open "<url>"
playwright-cli eval "document.documentElement.outerHTML" --filename ".workdir/raw.html"
playwright-cli close

# 2. 用 Node.js 脚本转换
node "$SKILL_ROOT/scripts/convert.mjs" --input ".workdir/raw.html" --output "output.md"
```

### 网页截图 + 视觉分析

```bash
playwright-cli open "<url>"
playwright-cli resize 1440 900
playwright-cli screenshot --full-page --filename "output/screenshot.png"
playwright-cli close
# Agent 直接读取 screenshot.png 进行视觉分析
```

### CSS / Design Token 提取

```bash
playwright-cli open "<url>"
playwright-cli eval "$(cat "$SKILL_ROOT/scripts/extract-page-info.js")" --filename "page-info.json"
playwright-cli eval "$(cat "$SKILL_ROOT/scripts/extract-styles.js")" --filename "raw-styles.json"
playwright-cli close
node "$SKILL_ROOT/scripts/summarize-styles.mjs" --input "raw-styles.json" --output "style-summary.json"
```

## 反模式速查

| 错误做法 | 正确做法 |
|----------|----------|
| `pip install playwright` | `npm install -g @playwright/cli` |
| `playwright install chromium` | `playwright-cli install` |
| `npx playwright install chromium` | `playwright-cli install` |
| `npm install playwright` | `npm install -g @playwright/cli` |
| `npm install @playwright/test` | `npm install -g @playwright/cli` |
| Python `from playwright.sync_api import sync_playwright` | `playwright-cli open/eval/screenshot` |
| 每次操作启动新浏览器 | `playwright-cli open` 后复用同一 Session |
| 用 requests/urllib 获取需要 JS 的页面 | `playwright-cli open` 获取渲染后 DOM |
| 浏览器操作 + 数据处理混在一个 Python 脚本 | 浏览器操作用 `playwright-cli`，数据处理用 Node.js 脚本 |
