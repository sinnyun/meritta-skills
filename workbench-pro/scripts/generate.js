#!/usr/bin/env node
/**
 * Workbench-Pro Theme Generator
 * =================================
 * Reads the mint base templates (desktop + mobile) and themes.json,
 * generates themed workbench HTML files for all 4 themes × 2 ends = 8 files.
 *
 * Uses ordered string replacement (split-join) to handle the
 * "same hex value, different target" conflict, same approach as theme-dashboard.
 *
 * Usage:
 *   node generate.js              # Generate all themes × both ends
 *   node generate.js mint         # Generate specific theme (both ends)
 *   node generate.js mocha rose   # Generate multiple themes
 *   node generate.js mint --mobile  # Generate specific theme, mobile only
 *   node generate.js mint --desktop # Generate specific theme, desktop only
 *   node generate.js mint --mobile --data scenario.json  # Mobile + scenario data overlay
 */

const fs = require('fs');
const path = require('path');
const { applyDataOverlay } = require('./data-overlay');

const ROOT = path.resolve(__dirname, '..');
const TEMPLATES_DIR = path.join(ROOT, 'templates');
const THEMES_FILE = path.join(TEMPLATES_DIR, 'themes.json');
const SCENARIOS_DIR = path.join(TEMPLATES_DIR, 'scenarios');
const DESKTOP_BASE = path.join(TEMPLATES_DIR, 'workbench-desktop.html');
const MOBILE_BASE = path.join(TEMPLATES_DIR, 'workbench-mobile.html');
const OUT_DIR = path.join(ROOT, 'examples');

// ─── Replacement Rules ──────────────────────────────────────────
// Each rule: [mint_string, value_from_theme(theme)]
// Rules are applied in order. Earlier rules consume their matches
// so later rules only see remaining occurrences.

const RULES = [
  // ── Phase 1: :root CSS variables — replace "name: value" pairs ──
  // The space after colon matches the template format. Using the full
  // "name:value" string as the find key avoids matching the same hex elsewhere.
  ['--page-bg: #E8F5E9',              t => `--page-bg: ${t.root.page_bg}`],
  ['--surface-card: #FFFFFF',         t => `--surface-card: ${t.root.surface_card}`],
  ['--surface-nested: #F5FBF5',       t => `--surface-nested: ${t.root.surface_nested}`],
  ['--surface-glass: rgba(255,255,255,.75)',
    t => `--surface-glass: ${t.root.surface_glass}`],
  ['--border: #D8EED8',               t => `--border: ${t.root.border}`],
  ['--border-input: #C5E3C5',         t => `--border-input: ${t.root.border_input}`],
  ['--glass-border: rgba(255,255,255,.6)',
    t => `--glass-border: ${t.root.glass_border}`],
  ['--text: #2E5E2E',                 t => `--text: ${t.root.text}`],
  ['--text-secondary: #5B7D5B',       t => `--text-secondary: ${t.root.text_secondary}`],
  ['--text-tertiary: #8FBC8F',       t => `--text-tertiary: ${t.root.text_tertiary}`],
  ['--accent: #66BB6A',               t => `--accent: ${t.root.accent}`],
  ['--accent-dark: #43A047',          t => `--accent-dark: ${t.root.accent_dark}`],
  ['--accent-light: #A5D6A7',         t => `--accent-light: ${t.root.accent_light}`],
  ['--accent-muted: #E8F5E9',        t => `--accent-muted: ${t.root.accent_muted}`],
  ['--accent-glow: rgba(102,187,106,.4)',
    t => `--accent-glow: ${t.root.accent_glow}`],
  ['--on-accent: #FFFFFF',            t => `--on-accent: ${t.root.on_accent}`],
  ['--module-1: #66BB6A',             t => `--module-1: ${t.root.module_1}`],
  ['--module-2: #26A69A',             t => `--module-2: ${t.root.module_2}`],
  ['--module-3: #FFB74D',             t => `--module-3: ${t.root.module_3}`],
  ['--module-4: #EC407A',             t => `--module-4: ${t.root.module_4}`],
  ['--module-5: #7E57C2',             t => `--module-5: ${t.root.module_5}`],
  ['--danger: #EC407A',               t => `--danger: ${t.root.danger}`],
  ['--danger-muted: #F8BBD0',         t => `--danger-muted: ${t.root.danger_muted}`],
  ['--drawer-bg: #1B2D1F',            t => `--drawer-bg: ${t.root.drawer_bg}`],
  ['--drawer-bg-top: #1E3225',        t => `--drawer-bg-top: ${t.root.drawer_bg_top}`],
  ['--drawer-text: #C8E6C9',          t => `--drawer-text: ${t.root.drawer_text}`],
  ['--drawer-text-mute: rgba(200,230,201,.55)',
    t => `--drawer-text-mute: ${t.root.drawer_text_mute}`],
  ['--drawer-hover: rgba(200,230,201,.08)',
    t => `--drawer-hover: ${t.root.drawer_hover}`],
  ['--drawer-active: rgba(200,230,201,.12)',
    t => `--drawer-active: ${t.root.drawer_active}`],
  ['--ring-track: #E8F5E9',           t => `--ring-track: ${t.root.ring_track}`],

  // greet-image: replace the full radial-gradient value
  ['--greet-image: radial-gradient(120% 130% at 85% 15%, rgba(102,187,106,.14), rgba(102,187,106,.05) 55%, rgba(102,187,106,0) 100%)',
    t => `--greet-image: ${t.root.greet_image}`],

  // shadows
  ['--shadow-card: 0 4px 16px rgba(102,187,106,.1)',
    t => `--shadow-card: ${t.root.shadow_card}`],
  ['--shadow-overlay: 0 8px 32px rgba(102,187,106,.15), 0 2px 8px rgba(0,0,0,.04)',
    t => `--shadow-overlay: ${t.root.shadow_overlay}`],
  ['--shadow-hover: 0 16px 48px rgba(102,187,106,.22), 0 4px 12px rgba(0,0,0,.06)',
    t => `--shadow-hover: ${t.root.shadow_hover}`],

  // ── Phase 2: visual effect tokens ──
  ['--body-glow-1: rgba(102,187,106,.08)',  t => `--body-glow-1: ${t.effects.body_glow_1}`],
  ['--body-glow-2: rgba(38,166,154,.06)',    t => `--body-glow-2: ${t.effects.body_glow_2}`],
  ['--body-glow-3: rgba(255,183,77,.04)',    t => `--body-glow-3: ${t.effects.body_glow_3}`],
  ['--orb-1: rgba(102,187,106,.12)',         t => `--orb-1: ${t.effects.orb_1}`],
  ['--orb-2: rgba(38,166,154,.1)',           t => `--orb-2: ${t.effects.orb_2}`],
  ['--orb-3: rgba(255,183,77,.08)',          t => `--orb-3: ${t.effects.orb_3}`],

  // ── Phase 3: hardcoded colors in enhancement CSS ──
  // Gradient progress bars
  ['.gbar-1 { background: linear-gradient(90deg, #66BB6A, #43A047); }',
    t => `.gbar-1 { background: linear-gradient(90deg, ${t.gradients.progress_1[0]}, ${t.gradients.progress_1[1]}); }`],
  ['.gbar-2 { background: linear-gradient(90deg, #26A69A, #00897B); }',
    t => `.gbar-2 { background: linear-gradient(90deg, ${t.gradients.progress_2[0]}, ${t.gradients.progress_2[1]}); }`],
  ['.gbar-3 { background: linear-gradient(90deg, #FFB74D, #FF9800); }',
    t => `.gbar-3 { background: linear-gradient(90deg, ${t.gradients.progress_3[0]}, ${t.gradients.progress_3[1]}); }`],
  ['.gbar-4 { background: linear-gradient(90deg, #EC407A, #C2185B); }',
    t => `.gbar-4 { background: linear-gradient(90deg, ${t.gradients.progress_4[0]}, ${t.gradients.progress_4[1]}); }`],

  // SVG ring gradient stop-color classes
  ['.ring-grad-1 { stop-color: #66BB6A; }',   t => `.ring-grad-1 { stop-color: ${t.gradients.ring_1[0]}; }`],
  ['.ring-grad-1b { stop-color: #43A047; }',  t => `.ring-grad-1b { stop-color: ${t.gradients.ring_1[1]}; }`],
  ['.ring-grad-2 { stop-color: #FFB74D; }',   t => `.ring-grad-2 { stop-color: ${t.gradients.ring_2[0]}; }`],
  ['.ring-grad-2b { stop-color: #FF9800; }',  t => `.ring-grad-2b { stop-color: ${t.gradients.ring_2[1]}; }`],
  ['.ring-grad-3 { stop-color: #26A69A; }',   t => `.ring-grad-3 { stop-color: ${t.gradients.ring_3[0]}; }`],
  ['.ring-grad-3b { stop-color: #00897B; }',  t => `.ring-grad-3b { stop-color: ${t.gradients.ring_3[1]}; }`],
  ['.ring-grad-4 { stop-color: #EC407A; }',   t => `.ring-grad-4 { stop-color: ${t.gradients.ring_4[0]}; }`],
  ['.ring-grad-4b { stop-color: #C2185B; }',  t => `.ring-grad-4b { stop-color: ${t.gradients.ring_4[1]}; }`],

  // Trend chart classes
  ['.trend-stroke { stroke: #66BB6A; }',     t => `.trend-stroke { stroke: ${t.trend.color}; }`],
  ['.trend-fill { stop-color: #66BB6A; }',   t => `.trend-fill { stop-color: ${t.trend.color}; }`],
  ['.trend-grid { stroke: #E8F5E9; }',       t => `.trend-grid { stroke: ${t.trend.grid}; }`],
  ['.trend-label { fill: #8FBC8F; }',         t => `.trend-label { fill: ${t.trend.label}; }`],
];

// ─── Special replacements (non-color) ───────────────────────────

function applySpecial(content, theme, isMobile) {
  const name = theme.meta.name;

  // 1. Replace emoji only in <title> tag (🌿 → theme emoji)
  content = content.split('<title>\uD83C\uDF3F').join('<title>' + theme.meta.emoji);

  // 2. Replace title suffix only in <title> tag (· Mint</title> → · Name</title>)
  const capName = theme.meta.name.charAt(0).toUpperCase() + theme.meta.name.slice(1);
  content = content.split('\u00b7 Mint</title>').join('\u00b7 ' + capName + '</title>');

  return content;
}

// ─── Main generation logic ─────────────────────────────────────

function generateTheme(themeName, themes, desktopBase, mobileBase, scenarioData) {
  const theme = themes[themeName];
  if (!theme) {
    console.error(`  \u2717 Unknown theme: ${themeName}`);
    return false;
  }

  let ok = true;

  // Generate desktop version
  if (desktopBase) {
    let content = desktopBase;
    for (const [find, getValue] of RULES) {
      const value = getValue(theme);
      if (value === undefined) {
        console.error(`  \u2717 Missing value for: ${find}`);
        ok = false; continue;
      }
      content = content.split(find).join(value);
    }
    content = applySpecial(content, theme, false);
    if (scenarioData) { const r = applyDataOverlay(content, scenarioData); content = r.content; }
    const outFile = path.join(OUT_DIR, theme.meta.file_d);
    fs.writeFileSync(outFile, content, 'utf8');
  }

  // Generate mobile version
  if (mobileBase) {
    let content = mobileBase;
    for (const [find, getValue] of RULES) {
      const value = getValue(theme);
      if (value === undefined) {
        ok = false; continue;
      }
      content = content.split(find).join(value);
    }
    content = applySpecial(content, theme, true);
    if (scenarioData) { const r = applyDataOverlay(content, scenarioData); content = r.content; }
    const outFile = path.join(OUT_DIR, theme.meta.file_m);
    fs.writeFileSync(outFile, content, 'utf8');
  }

  return ok;
}

// ─── CLI entry point ───────────────────────────────────────────

function main() {
  const themes = JSON.parse(fs.readFileSync(THEMES_FILE, 'utf8'));
  const desktopBase = fs.existsSync(DESKTOP_BASE) ? fs.readFileSync(DESKTOP_BASE, 'utf8') : null;
  const mobileBase = fs.existsSync(MOBILE_BASE) ? fs.readFileSync(MOBILE_BASE, 'utf8') : null;

  if (!desktopBase && !mobileBase) {
    console.error('No base templates found. Run build-base.js first.');
    process.exit(1);
  }

  const args = process.argv.slice(2);
  const onlyDesktop = args.includes('--desktop');
  const onlyMobile = args.includes('--mobile');

  // --data <file> : load scenario JSON for data overlay
  let scenarioData = null;
  const dataIdx = args.indexOf('--data');
  if (dataIdx !== -1 && args[dataIdx + 1]) {
    scenarioData = JSON.parse(fs.readFileSync(args[dataIdx + 1], 'utf8'));
    console.log(`  data: ${args[dataIdx + 1]}`);
  }

  const skipVals = new Set();
  if (dataIdx !== -1 && args[dataIdx + 1]) skipVals.add(args[dataIdx + 1]);
  const themeArgs = args.filter(a => !a.startsWith('--') && !skipVals.has(a));

  const targets = themeArgs.length > 0 ? themeArgs : Object.keys(themes);
  const useDesktop = !onlyMobile && desktopBase;
  const useMobile = !onlyDesktop && mobileBase;

  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });

  let ok = 0, fail = 0;
  for (const name of targets) {
    if (generateTheme(name, themes, useDesktop && desktopBase, useMobile && mobileBase, scenarioData)) ok++;
    else fail++;
  }

  console.log(`${targets.join(', ')} ${ok} ok${fail ? ', ' + fail + ' fail' : ''}`);
}

main();
