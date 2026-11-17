# 模板目录（场景 → 审美基准资产检索表）

本目录把 `examples/` 下已沉淀的成品工作台登记为**审美基准资产**（不是整页复制对象）。生成新工作台时：
- **命中场景** → 以对应模板的「布局形态 + 主题色板 + hero 构图 + 氛围元素」为审美下限，按分层流程（base-shell + 组件拼装 + 现场业务）生成，视觉对齐模板、结构保持可改。
- **未命中场景** → 走 `default` 通用基底 + 按场景类型选最优色板。

## 使用方式

1. 用户输入场景 → 查「场景匹配」列的关键词，命中则用该模板。
2. 打开对应模板文件，取其视觉资产（色板 token、布局、hero、氛围细节）。
3. 生成时以 `assets/base-shell.html` 为工程骨架，视觉资产只作"美的基准"，不整页复制。

---

## 模板清单

### T1 · 个人成长 / 目标管理（远行）

| 项 | 内容 |
|---|---|
| 文件 | `examples/个人成长.html` |
| 场景匹配 | 个人成长、目标、习惯、成长、自我提升、人生规划、年度目标、周复盘 |
| 布局形态 | 多页 SPA（`navigateTo()` 切 10 页：home/today/habit/insights/calendar/album/focus/review/settings/library）+ 左侧 moss 深绿 sidebar |
| 主题色板 | 苔绿纸感：`--moss:#466B52` `--moss-deep:#2F4A39` `--moss-soft:#C8D5BB` `--moss-tint:#E8EFE3`；`--paper:#F5EFE2` `--paper-deep:#E8DEC9`；`--ink:#2C2620` `--ink-soft:#5A4F44` `--ink-faint:#9C8E7E`；点缀 `--amber:#D88C4A` `--ember:#B8503C` `--sky:#7B96A8` |
| hero 构图 | 深绿渐变横幅 + 场景插画 + 日期章 + 标题（含 `em` 强调）+ 引言 + 行动按钮 + 右侧 stats 卡（含进度条） |
| 卡片形态 | 白卡圆角 + hover lift；today-item 米白底；path-card 成长路径图；habit-grid 5 宫格 |
| 氛围元素 | hero 场景插画、日期章、成长路径图、习惯矩阵、阶段成果里程碑、心情曲线、专注计时、成长日记 |
| 存储 key | `wb_yuanxing_workspace_v1` |
| 兼容状态 | ✅ 无外链（仅 SVG 命名空间）；含 `backdrop-filter`（带 rgba 底色兜底，符合降级规则） |
| 改造难度 | 高（多页结构 + 定制交互多） |
| 业务耦合度 | 低（习惯/日记/里程碑，通用业务）（高耦合=写死业务规则，仅作本场景专属模板；低耦合=通用引擎，可作其他场景基底） |
| 可迁移视觉资产 | moss 纸感色板、深色 sidebar、多页导航、hero 横幅构图、habit 矩阵、成长路径图 |

### T2 · 技术开发 / 职场效率（Mocha）

| 项 | 内容 |
|---|---|
| 文件 | `examples/技术开发.html` |
| 场景匹配 | 技术、开发、程序员、极客、工作台、职场、效率、办公、DevOps |
| 布局形态 | 左侧 drawer 深色侧栏 + hero 横幅 + CONFIG 引擎（todo/checkin/progress/finance/note 五类模块） |
| 主题色板 | Mocha 摩卡暖棕：`--page-bg:#F5E6D3` `--accent:#B08968` `--accent-dark:#9C6F4A` `--accent-light:#D4A574` `--accent-muted:#F5E6D3` `--drawer-bg:#2D2018` `--text:#5D4037` `--text-secondary:#7D6555`；模块 5 色 `#B08968/#CB997E/#E6A85C/#9A5A6A/#6D4C41` |
| hero 构图 | hero-banner + hero-bar 数据条 |
| 卡片形态 | radius-tile/card/sheet 三级圆角；阴影带主色调 |
| 氛围元素 | drawer 深色面板 + 模块色轮转 + 背景光晕 orb |
| 存储 key | 未统一前缀（非 `wb_`） |
| 兼容状态 | ⚠️ **不合规**：`min-width:1000px`（违反响应式铁律）、含 `http://192.168.1.20`、`https://...` 残留外链 |
| 改造难度 | 中（CONFIG 引擎清晰，但需先修基线） |
| 业务耦合度 | 低（CONFIG 引擎：todo/checkin/progress/finance/note 通用模块）（高耦合=写死业务规则，仅作本场景专属模板；低耦合=通用引擎，可作其他场景基底） |
| 可迁移视觉资产 | drawer 深色侧栏、5 模块色轮转、CONFIG 引擎思路、摩卡暖棕色板 |

### T3 · 学习 / 考试规划（知行）

| 项 | 内容 |
|---|---|
| 文件 | `examples/学习记录.html`（原 考试学习.html，已改名） |
| 场景匹配 | 学习、考试、备考、刷题、课程、高考、考研、学生、单词、复习 |
| 布局形态 | 顶部 hero（左艺术区 + 右数据区）+ home-grid 双列 + 多页（学习地图/数据洞察/素材册/设置/阶段成果） |
| 主题色板 | 樱粉+钢笔蓝：`--pink:#E8A0AE` `--pink-2:#F3C9D2` `--pink-ink:#B9768A` `--sky:#BFD8E8` `--sky-2:#E4EFF6` `--cream:#FAF6EC` `--paper:#FFFDF9` `--ink:#4A6B9F`（钢笔蓝）`--text:#2C3A4B` `--muted:#7C8798` `--faint:#A6AEBB` |
| hero 构图 | 左艺术插画（飞机 SVG）+ 右 hero-body（eyebrow 日期 + 标题 + slogan + metrics 指标 + actions）；右上角 **hero-polaroid 拍立得**（倒计日历卡，旋转 -3deg，带 caption） |
| 卡片形态 | today-card 带头部横幅 + todo-row 分隔；stamp 邮戳胶囊；polaroid 拍立得 |
| 氛围元素 | 高考倒计时、stamp 邮戳、拍立得素材卡、课程表、学习地图 |
| 存储 key | `wb_zhixing_v1` |
| 兼容状态 | ✅ 无外链（仅 SVG 命名空间）；favicon 内联 SVG |
| 改造难度 | 高（多页 + 定制插画多） |
| 业务耦合度 | 极高（考试×33/课程×9，160 个函数，备考引擎极深）（高耦合=写死业务规则，仅作本场景专属模板；低耦合=通用引擎，可作其他场景基底） |
| 可迁移视觉资产 | 樱粉+钢笔蓝纸感色板、hero 左图右数据构图、polaroid 拍立得卡、stamp 邮戳、metrics 指标行 |

### T4 · 露营 / 户外装备（山野清单）

| 项 | 内容 |
|---|---|
| 文件 | `examples/野外露营.html` |
| 场景匹配 | 露营、户外、装备、徒步、登山、野营、营地、旅行（户外向） |
| 布局形态 | 长页单列 + 顶部 hero + 十类记录 ledger 卡 + 底部 tabbar（`tabbar__in`）+ daypanel 日面板 + albumsec 相册 |
| 主题色板 | 山野绿+沙米：`--forest:#5C8A6B` `--forest-deep:#3E6B4E` `--forest-soft:#8FB49B` `--forest-wash:#EDF3EE` `--khaki:#D4CC9A` `--khaki-soft:#E8E3C6` `--ember:#D96045` `--tent:#F5EFE2` `--tent-deep:#E7DCC6` `--ink:#1F2C25` `--ink-2:#57685F` `--ink-3:#8A998F` |
| hero 构图 | hero 内含 topo 等高线 SVG + sparks 火星粒 + 左 shot 指南针 + 右 log 日期/文案 + 进度环 prog |
| 卡片形态 | `card--ledger` 账本卡（十类记录：activity/camp/route/weather/gear/food/budget/maintenance/purchase/media）+ 通用 card + card--wash |
| 氛围元素 | 帐篷尖符号（tip）、空状态专属插画（ART_EMPTY/NOSEARCH/NOALBUM/BROKEN）、SVG 图标库（IC）、crest 徽章、火星粒 |
| 存储 key | `wb_shanye_v1` |
| 兼容状态 | ✅ 无外链（仅 SVG 命名空间 + data: 内联 favicon） |
| 改造难度 | 高（十类记录引擎 + 大量定制交互） |
| 业务耦合度 | 极高（营地×51/装备×52，装备清单/天气建议业务规则写死）（高耦合=写死业务规则，仅作本场景专属模板；低耦合=通用引擎，可作其他场景基底） |
| 可迁移视觉资产 | 山野绿+沙米色板、ledger 账本卡、tabbar、topo 等高线 hero、空状态插画体系、SVG 图标库、crest 徽章 |

---

## 通用基底（default）候选

未命中场景时基于哪套改？关键约束：**必须技术基线合规（无外链、无固定 min-width、响应式）**。

- 首选：**T1 个人成长（moss 纸感）**——布局最中性（sidebar + 多页），色板最克制，符合"通用"定位；但多页结构改造成本高。
- 次选：**T4 野外露营**——长页单列 + tabbar 更贴近"个人工具"直觉，但十类记录引擎有场景串味风险。
- **T2 技术开发**：**不可作基底**（`min-width:1000px` + 外链残留，需先修基线）。

## 已登记模板演进记录

| 日期 | 变更 |
|---|---|
| 2026-09-12 | 初始登记 4 套（T1-T4）；标记 T2 基线不合规；确立 default 基底候选 |
| 2026-09-12 | 新增登记 7 套（T5-T11：个人备考/企业管理/宠物养成/新闻资讯/旅行规划/识字启蒙/运动打卡）；T3 改名学习记录.html；全库达 11 套 |

---

## 新增登记（T5-T11）

### T5 · 备考 / 考试（考研）

| 项 | 内容 |
|---|---|
| 文件 | `examples/个人备考.html` |
| 场景匹配 | 考研、备考、考试、冲刺、复习计划、上岸 |
| 布局形态 | 左侧 sidebar + 顶栏 + 多页（nav/nav-group/nav-item） |
| 主题色板 | 奶油纸感多彩：`--bg:#FFF6D6` `--ink:#16110B` `--paper:#FFFDF3`；语义 `--red:#FF5A5F` `--orange:#FF8A3D` `--yellow:#FFC93C` `--green:#2ED573` `--teal:#26C6A8` `--blue:#4D8BFF` |
| 存储 key | `wb_kaoyan_`（affairs/focus/hint_dismissed） |
| 兼容状态 | ✅ 无外链 |
| 改造难度 | 高（2348 行，15 个 render 函数，模块多） |
| 业务耦合度 | 高（刷题×16/单词×4，70 函数）（高耦合=写死业务规则，仅作本场景专属模板；低耦合=通用引擎，可作其他场景基底） |
| 双端导航 | PC sidebar（移动端转抽屉）✓ / 移动端 sidebar 抽屉 ✓ |
| 可迁移视觉资产 | 备考冲刺氛围、科目分组导航 |

### T6 · 企业管理 / 项目

| 项 | 内容 |
|---|---|
| 文件 | `examples/企业管理.html` |
| 场景匹配 | 企业管理、项目管理、工作台、审批、合同、项目看板、任务管理 |
| 布局形态 | 顶栏 + 底部导航（bottom-nav）+ 表格（table-scroll/table-toolbar） |
| 主题色板 | 商务蓝：`--primary:#2563EB` `--primary-deep:#1D4ED8` `--primary-light:#EEF4FF` `--page:#F3F5F9` `--card:#FFF` `--line:#E8ECF3`；语义 `--green:#0F9D6E` `--red:#E24B4A` `--amber:#D97706` |
| 存储 key | `wb_empmgr_` |
| 兼容状态 | ✅ 无外链 |
| 改造难度 | 中（1326 行，12 个 render，表格密集） |
| 业务耦合度 | 高（合同×51/审批×18/项目×21/客户×11）（高耦合=写死业务规则，仅作本场景专属模板；低耦合=通用引擎，可作其他场景基底） |
| 双端导航 | 底部 bottom-nav ✓（移动端） |
| 可迁移视觉资产 | 商务蓝专业色板、表格/审批/合同台账形态、底部导航 |

### T7 · 宠物养成 / 健康养护

| 项 | 内容 |
|---|---|
| 文件 | `examples/宠物养成.html` |
| 场景匹配 | 宠物、猫狗、养成、健康、疫苗、喂食、日常养护 |
| 布局形态 | hero（hero-art/hero-card/hero-strip）+ sidebar + 顶栏 |
| 主题色板 | 暖萌绿杏：`--green:#8FBC9F` `--green-d:#578A6C` `--green-l:#E6F1E9` `--apricot:#F2DDB5` `--apricot-d:#D9BC84` `--apricot-l:#FBF3E1` `--milk:#FAF6EC` |
| 存储 key | `wb_weiba_`（pet_v1/ui_v1） |
| 兼容状态 | ✅ 无外链 |
| 改造难度 | 高（4152 行，16 个 render，全库最大） |
| 业务耦合度 | 高（体重×34/疫苗×26/喂食×11）（高耦合=写死业务规则，仅作本场景专属模板；低耦合=通用引擎，可作其他场景基底） |
| 双端导航 | sidebar ✓ / 移动端底部导航条（position:fixed bottom）✓ |
| 可迁移视觉资产 | 宠物场景插画、养成闭环（喂食/健康/疫苗）、hero 组合 |

### T8 · 新闻资讯 / 信息聚合

| 项 | 内容 |
|---|---|
| 文件 | `examples/新闻资讯.html` |
| 场景匹配 | 新闻、资讯、阅读、收藏、RSS、信息流、书签、稍后读 |
| 布局形态 | 顶栏（topbar-card）+ 卡片流；无独立 sidebar |
| 主题色板 | 紫色现代：`--accent:#6c5ce7` `--blue:#3b82f6` `--teal:#0ea5a4` `--orange:#f59e0b` `--pink:#ec4899` `--text:#2b2f3a` `--card:rgba(255,255,255,.74)` |
| 存储 key | `wb_workspace_v1` / `wb_ws_cache_` |
| 兼容状态 | ✅ 外链仅为业务数据字段（用户收藏的网址 URL：GitHub/知乎/DeepSeek/音乐链接），非外部资源引用，合规 |
| 改造难度 | 中（1317 行，10 个 render） |
| 业务耦合度 | 低（无专有业务词，通用卡片流）（高耦合=写死业务规则，仅作本场景专属模板；低耦合=通用引擎，可作其他场景基底） |
| 双端导航 | 顶栏导航承载（无独立 sidebar/tabbar）；移动端 680px 断点顶栏调整 + 底部提醒浮标。⚠️ 无底部 Tab，移动端导航靠顶栏，若命中此模板需注意"移动端不丢导航"要求 |
| 可迁移视觉资产 | 紫色现代信息流、收藏/稍后读、卡片流布局 |

### T9 · 旅行规划 / 回忆

| 项 | 内容 |
|---|---|
| 文件 | `examples/旅行规划.html` |
| 场景匹配 | 旅行、旅游、行程、攻略、回忆、路线、打卡景点 |
| 布局形态 | drawer + hero（hero-eyebrow/hero-body/hero-acts）+ tabbar + sidebar |
| 主题色板 | 天空沙地旅行：`--sky:#6FB7D2` `--sky-d:#57A2BE` `--sky-l:#E9F4F9` `--sand:#F5EFE2` `--sand-d:#E7DCC6` `--sand-l:#FBF8F1`；点缀 `--orange:#E89B3D` `--teal:#24718A` |
| 存储 key | `wb_yuanfang_`（db_v1/prefs_v1） |
| 兼容状态 | ✅ 无外链 |
| 改造难度 | 高（3815 行，13 个 render） |
| 业务耦合度 | 高（行程×14/景点×9，133 函数）（高耦合=写死业务规则，仅作本场景专属模板；低耦合=通用引擎，可作其他场景基底） |
| 双端导航 | sidebar + tabbar 双全 ✓ |
| 可迁移视觉资产 | 旅行手帐氛围、行程/日程完成、预算统计、drawer+tabbar 双导航 |

### T10 · 识字启蒙 / 育儿

| 项 | 内容 |
|---|---|
| 文件 | `examples/识字启蒙.html` |
| 场景匹配 | 识字、启蒙、认字、汉字、宝宝、亲子、育儿、拼音 |
| 布局形态 | hero + 顶栏 + 移动端底部操作条（.mobile-bar，小屏才显示） |
| 主题色板 | 清新绿：`--bg:#eef4ef` `--ink:#2f4a3c` `--green:#5cb98c` `--green-deep:#3f9d70` `--mint:#dcefe3` `--yellow:#f5b942` `--blue:#6aa9e8` |
| 存储 key | `wb_literacy_v1` |
| 兼容状态 | ✅ 无外链 |
| 改造难度 | 中（1424 行，13 个 render） |
| 业务耦合度 | 低（无专有业务词，儿童向通用练习）（高耦合=写死业务规则，仅作本场景专属模板；低耦合=通用引擎，可作其他场景基底） |
| 双端导航 | 移动端 .mobile-bar 底部操作条 ✓（PC 无 sidebar，靠顶栏+hero） |
| 可迁移视觉资产 | 清新绿儿童色板、识字翻卡/练习、移动底部操作条、儿童向大按钮 |

### T11 · 运动打卡 / 健身

| 项 | 内容 |
|---|---|
| 文件 | `examples/运动打卡.html` |
| 场景匹配 | 健身、运动、打卡、减脂、锻炼、训练、跑步、健身记录 |
| 布局形态 | hero + 顶栏 + tabbar（移动端）+ 数据洞察/记录库/分类标签/快捷记录 |
| 主题色板 | 深蓝紫活力：`--ink:#262B47` `--paper:#F3F4FB` `--acc:#4F5AE5` `--acc-deep:#3A44BC` `--sage:#2FA373` `--water:#4E7FE8` |
| 存储 key | `wb_jidong_v1`（肌动） |
| 兼容状态 | ✅ 无外链 |
| 改造难度 | 中（1517 行） |
| 业务耦合度 | 高（训练×54/体重×14，训练记录引擎）（高耦合=写死业务规则，仅作本场景专属模板；低耦合=通用引擎，可作其他场景基底） |
| 双端导航 | tabbar ✓（移动端） |
| 可迁移视觉资产 | 深蓝紫运动色板、数据洞察/趋势、记录库/分类标签、tabbar |

---

## 覆盖度评估（2026-09-12）

当前 11 套模板覆盖场景：成长/目标、技术/职场、学习/考试、露营/户外、备考、企业管理、宠物、新闻资讯、旅行、识字育儿、运动健身。**已基本覆盖常见个人工作台场景**；仍可补：记账理财、习惯打卡、阅读管理、求职进度、自媒体创作（高频缺口，建议优先）。
