# Workbench-Pro Skill

A dual-end workbench generator combining **personal-workbench** (functionality base) + **theme-dashboard** (theme skins). One base template + one color definition + ordered replacement engine = 4 themes × 2 ends = 8 HTML files.

---

## Directory Structure

```
workbench-pro/
├── SKILL.md                        # This document (skill definition)
├── scripts/
│   ├── build-base.js               # Conversion script: raw template → enhanced mint base
│   └── generate.js                 # Generation script: mint base → 4 themes × 2 ends
├── templates/
│   ├── workbench-desktop.html      # desktop base template (mint, ~1700 lines)
│   ├── workbench-mobile.html       # mobile base template (mint, ~1530 lines)
│   └── themes.json                 # 4 theme complete color definitions (80+ color points)
└── examples/
    ├── workbench-mint.html         # Output · Mint · desktop
    ├── workbench-mint-m.html       # Output · Mint · mobile
    ├── workbench-mocha.html        # Output · Mocha · desktop
    ├── workbench-mocha-m.html      # Output · Mocha · mobile
    ├── workbench-rose.html         # Output · Rose · desktop
    ├── workbench-rose-m.html       # Output · Rose · mobile
    ├── workbench-amber.html        # Output · Amber · desktop
    └── workbench-amber-m.html      # Output · Amber · mobile
```

**Two-step flow**: `build-base.js` (build base) → `generate.js` (themed generation). Re-run both steps after modifying base template.

---

## Usage

### Full Rebuild (from raw templates)

```bash
cd workbench-pro
node scripts/build-base.js    # Read personal-workbench raw templates, inject enhancements, output mint base
node scripts/generate.js      # Generate 4 themes × 2 ends = 8 files from mint base
```

### Regenerate Themes Only (base template unchanged)

```bash
node scripts/generate.js              # All 4 themes × 2 ends
node scripts/generate.js mint         # Only mint (both ends)
node scripts/generate.js mocha rose   # Multiple themes
node scripts/generate.js mint --mobile   # Only mobile
node scripts/generate.js mint --desktop  # Only desktop
```

### Adding New Themes

1. Add new theme key in `templates/themes.json`, copy existing theme structure and change colors
2. Add new chip in base template's theme switcher
3. Add replacement rules for new chip in `generate.js` RULES
4. Run `node scripts/generate.js newtheme`

---

## Architecture

### Fusion Strategy

```
personal-workbench (functionality)       theme-dashboard (skins)
  ├─ 5 modules (todo/checkin/progress/   ├─ 4 theme palettes
  │  finance/note)                         │  (mint/mocha/rose/amber)
  ├─ CONFIG-driven rendering             ├─ Ordered replacement engine
  ├─ localStorage persistence             ├─ Glassmorphism + orb background
  ├─ desktop + mobile dual-end           ├─ SVG noise texture
  └─ Semantic CSS Token system           └─ countUp/ripple/3D tilt
          │                                      │
          └──────────────┬───────────────────────┘
                         ▼
                    workbench-pro
                   ├─ build-base.js (fusion layer)
                   ├─ themes.json (Token mapping)
                   └─ generate.js (generation engine)
```

### build-base.js: Fusion Layer

Reads raw desktop/mobile templates from `personal-workbench/scripts/`, performs 6-step enhancement:

| Step | Operation | Description |
|------|-----------|-------------|
| 1 | Replace `:root` block | Inject mint theme colors + new visual tokens (body-glow/orb/noise) |
| 2 | Inject enhanced CSS | orb floating background, SVG noise, glassmorphism, 3D tilt, theme chip, gradient bars, ring gradients, trend chart |
| 3 | Inject theme switcher HTML | desktop: before sidebar `.foot`; mobile: after topbar `date-chip` |
| 4 | Inject enhanced JS | countUp, addRipple, addTilt, initReveal (IntersectionObserver), initThemeSwitcher |
| 5 | Add reveal class | Add scroll-triggered animation to `.greet` and other elements |
| 6 | Replace title | `My Workbench` → `🌿 My Workbench · Mint` |

### themes.json: Token Mapping Layer

Maps theme-dashboard color system to personal-workbench semantic token structure:

```json
{
  "mint": {
    "meta": { "name", "file_d", "file_m", "emoji", "title" },
    "root": { 30+ semantic CSS tokens: page_bg, surface_card, accent, module_1~5, drawer_bg, ... },
    "effects": { body_glow_1/2/3, orb_1/2/3 },
    "gradients": { ring_1~4, progress_1~4 },
    "trend": { color, grid, label }
  },
  "mocha": { ... },
  "rose": { ... },
  "amber": { ... }
}
```

### generate.js: Ordered Replacement Engine

**Core challenge**: The same mint base value needs to map to different target values in different contexts. Uses ordered `content.split(find).join(value)` replacement; earlier rules "consume" their matches, later rules only process remaining occurrences.

**3 replacement phases**:

| Phase | Target | Rules | Example |
|--------|--------|-------|---------|
| Phase 1 | `:root` CSS variables | 30+ | `--page-bg: #E8F5E9` → `--page-bg: ${root.page_bg}` |
| Phase 2 | Visual effect tokens | 6 | `--body-glow-1: rgba(102,187,106,.08)` → `${effects.body_glow_1}` |
| Phase 3 | Enhanced CSS hardcoded colors | 20 | `.theme-chip[data-t="mint"] { background: linear-gradient(...)` |

**applySpecial function** (non-color replacements):
1. Active class migration: mint chip → target theme chip (compatible with both desktop and mobile formats)
2. Emoji replacement: only 🌿 inside `<title>` tag → target emoji
3. Title suffix replacement: only `· Mint` inside `<title>` tag → `· Name`
4. JS redirect condition: `t !== 'mint'` → `t !== '<theme>'`
5. Mobile filename suffix: `workbench-mint.html` → `workbench-mint-m.html`

---

## 4 Theme Palettes

### Primary Colors

| Theme | emoji | page_bg | accent | module_1 | drawer_bg | text |
|-------|-------|---------|--------|----------|-----------|------|
| mint | 🌿 | `#E8F5E9` | `#66BB6A` | `#66BB6A` | `#1B2D1F` | `#2E5E2E` |
| mocha | ☕ | `#F5E6D3` | `#B08968` | `#B08968` | `#2D2018` | `#5D4037` |
| rose | 🌹 | `#FFF0F5` | `#F06292` | `#F06292` | `#2D1A22` | `#4A2A3A` |
| amber | 🌻 | `#FFFDE7` | `#FFB74D` | `#FFA726` | `#2D2010` | `#4E342E` |

### Gradient Pairs

| Theme | ring_1 | ring_2 | ring_3 | ring_4 |
|-------|--------|--------|--------|--------|
| mint | `#66BB6A, #43A047` | `#FFB74D, #FF9800` | `#26A69A, #00897B` | `#EC407A, #C2185B` |
| mocha | `#B08968, #9C6F4A` | `#E6A85C, #FF9800` | `#CB997E, #A07560` | `#9A5A6A, #7A3A4A` |
| rose | `#F06292, #EC407A` | `#FFB74D, #FF9800` | `#FF80AB, #F06292` | `#BA68C3, #AB47BC` |
| amber | `#FFA726, #FB8C00` | `#FFB300, #FF8F00` | `#FF7043, #F4511E` | `#EF5350, #C62828` |

Full palette in `templates/themes.json`.

---

## 8-Dimension Visual Enhancements

Base template includes the following enhancements, automatically inherited by all themes:

### 1. Animation & Micro-interactions
- `requestAnimationFrame` + cubic ease countUp number animation
- Click ripple: dynamically create `<span>` + CSS animation
- Card 3D tilt: `mousemove` + `perspective` + `rotateX/rotateY`
- `IntersectionObserver` scroll trigger for `.reveal` elements

### 2. Visual Hierarchy & Depth
- Glassmorphism: `backdrop-filter: blur(20px)` + semi-transparent background
- Three-layer shadow system: `--shadow-card` / `--shadow-overlay` / `--shadow-hover`
- SVG noise texture overlay (`--noise-opacity`)
- Multi-layer radial gradient background (`body::before` + 3 floating orbs)

### 3. Typography & Fonts
- System font stack: `-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- Font weight hierarchy: 300/400/500/600/700
- Number font size gradient: 12px → 64px

### 4. Data Visualization Enhancements
- SVG `linearGradient` ring charts (4 independent gradient definitions)
- Trend chart: line + grid + labels
- Gradient progress bars + percentage labels

### 5. Interaction Feedback
- Theme switcher chips (4 themes + active state)
- Click to navigate: `window.location.href` to corresponding theme file
- Theme selection persisted to localStorage

### 6. Detail Decoration
- Card border radius hierarchy: `--radius-card` / `--radius-tile` / `--radius-sheet`
- Border glow: `--glass-border`
- Floating orb background animation

### 7. Theme & Personalization
- 4 theme switching: mint/mocha/rose/amber
- `:root` semantic token system
- Independent gradient definitions and shadow colors per theme

### 8. Responsive & Dual-end Adaptation
- Desktop: sidebar + multi-column grid, min-width:1000px
- Mobile: drawer + bottom tab + floating + button, max-width:480px, safe-area
- `@media (prefers-reduced-motion: reduce)` for reduced animation

---

## 5 Functional Modules

Based on personal-workbench CONFIG-driven rendering:

| Module | Function | Data Storage |
|--------|----------|--------------|
| todo | Task list (todo/completed) | localStorage |
| checkin | Habit check-in (heatmap) | localStorage |
| progress | Goal progress (ring chart + progress bar) | localStorage |
| finance | Income/expense tracking (monthly stats) | localStorage |
| note | Quick notes | localStorage |

---

## Verification Checklist

After generation, verify the following:

- [ ] `:root` CSS variables (30+) match themes.json root block
- [ ] Visual effect tokens (6) match effects block
- [ ] Enhanced CSS hardcoded colors (20) match gradients/trend block
- [ ] Active class on target theme chip (desktop + mobile)
- [ ] Title emoji and name replaced (desktop + mobile)
- [ ] JS redirect condition updated (desktop + mobile)
- [ ] Mobile themeData filename has `-m` suffix

Quick verification:
```bash
# Color verification
grep -E "^\s*--page-bg:|--accent:|--drawer-bg:" examples/workbench-<theme>.html

# Active chip verification
grep -o 'class="theme-chip active" data-t="[a-z]*"' examples/workbench-<theme>*.html

# Title verification
grep '<title>' examples/workbench-<theme>*.html

# JS redirect verification
grep -o "t !== '[a-z]*'" examples/workbench-<theme>*.html
```

---

## Modification Notes

### Modifying Base Template (Important: prefer scripts over Edit tool)

Base template is 1500+ lines of HTML; directly using Edit tool may cause string matching failures due to whitespace/newline differences. **Recommended: write one-off Node scripts for string replacement**, 100% reliable:

```javascript
// scripts/_patch.js (temporary script, delete after use)
const fs = require('fs'), path = require('path');
const f = path.join(__dirname, '..', 'templates', 'workbench-desktop.html');
let s = fs.readFileSync(f, 'utf8');
s = s.replace('old string', 'new string');  // Exact match
fs.writeFileSync(f, s, 'utf8');
```

```bash
node scripts/_patch.js && node scripts/generate.js
```

If you must use Edit tool: Read target file first to ensure content is current, include enough context in old_string for uniqueness.

After modifying `templates/workbench-desktop.html` or `templates/workbench-mobile.html`:
1. Check if new color values fall within RULES replacement scope
2. If adding colors, add rules in `generate.js` RULES, add entries in all 4 themes in `themes.json`
3. Keep mint base values unchanged (mint color values are the RULES find strings)
4. Re-run `node scripts/generate.js`

### Modifying Raw Functionality Templates

After modifying `personal-workbench/scripts/` raw templates:
1. Re-run `node scripts/build-base.js` to rebuild base template
2. Re-run `node scripts/generate.js` to regenerate all themes

### Modifying Colors

Change color values for corresponding theme in `templates/themes.json`, re-run `node scripts/generate.js`. Ensure structure completeness (all fields required).

---

## Technical Constraints

- **Zero dependencies**: Pure HTML + CSS + JS, no build step, no npm packages
- **Single-file delivery**: Each theme × end is a complete HTML file, opens directly in browser
- **Data localization**: localStorage storage, no backend; built-in sandbox-compatible storage layer (`storage`) that automatically falls back to in-memory storage when the page runs inside a sandboxed iframe lacking `allow-same-origin` (e.g. share/preview environments), avoiding the `SecurityError` and keeping all features working (data only lives in the current session)
- **Generation script dependencies**: Only Node.js built-in `fs` / `path` modules
- **Dual-end independence**: desktop and mobile are independent files, no shared runtime
