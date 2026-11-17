#!/usr/bin/env node
/**
 * build-base.js — Transform personal-workbench templates into enhanced mint base templates.
 *
 * Reads the original desktop/mobile templates from ../personal-workbench/scripts/,
 * applies mint theme colors + visual enhancements (glass morphism, orbs, noise,
 * countUp, ripple, 3D tilt, theme switcher, IntersectionObserver), then writes
 * the enhanced mint base to templates/.
 *
 * Usage: node build-base.js
 */

const fs = require('fs');
const path = require('path');

const SRC_DIR = path.resolve(__dirname, '..', '..', 'personal-workbench', 'scripts');
const OUT_DIR = path.resolve(__dirname, '..', 'templates');

// ─── Mint :root replacement ──────────────────────────────────────
// Replaces the entire :root { ... } block with mint-themed tokens
// plus new visual effect tokens (body glows, orbs, glass, etc.)

const MINT_ROOT = `:root {
    /* ---- 页面与表面 ---- */
    --page-bg: #E8F5E9;
    --surface-card: #FFFFFF;
    --surface-nested: #F5FBF5;
    --surface-glass: rgba(255,255,255,.75);

    /* ---- 边框 ---- */
    --border: #D8EED8;
    --border-input: #C5E3C5;
    --glass-border: rgba(255,255,255,.6);

    /* ---- 文本层级 ---- */
    --text: #2E5E2E;
    --text-secondary: #5B7D5B;
    --text-tertiary: #8FBC8F;

    /* ---- 主色 ---- */
    --accent: #66BB6A;
    --accent-dark: #43A047;
    --accent-light: #A5D6A7;
    --accent-muted: #E8F5E9;
    --accent-glow: rgba(102,187,106,.4);
    --on-accent: #FFFFFF;

    /* ---- 模块色（5 色轮转） ---- */
    --module-1: #66BB6A;
    --module-2: #26A69A;
    --module-3: #FFB74D;
    --module-4: #EC407A;
    --module-5: #7E57C2;

    /* ---- 危险色 ---- */
    --danger: #EC407A;
    --danger-muted: #F8BBD0;

    /* ---- 抽屉/侧栏（深色面板） ---- */
    --drawer-bg: #1B2D1F;
    --drawer-bg-top: #1E3225;
    --drawer-text: #C8E6C9;
    --drawer-text-mute: rgba(200,230,201,.55);
    --drawer-hover: rgba(200,230,201,.08);
    --drawer-active: rgba(200,230,201,.12);

    /* ---- 背景图 ---- */
    --greet-image: radial-gradient(120% 130% at 85% 15%, rgba(102,187,106,.14), rgba(102,187,106,.05) 55%, rgba(102,187,106,0) 100%);
    --page-texture: none;

    /* ---- 圆角 ---- */
    --radius-control: 8px;
    --radius-tile: 12px;
    --radius-card: 16px;
    --radius-sheet: 22px;

    /* ---- 阴影 ---- */
    --shadow-card: 0 4px 16px rgba(102,187,106,.1);
    --shadow-overlay: 0 8px 32px rgba(102,187,106,.15), 0 2px 8px rgba(0,0,0,.04);
    --shadow-hover: 0 16px 48px rgba(102,187,106,.22), 0 4px 12px rgba(0,0,0,.06);

    /* ---- 视觉效果 token ---- */
    --body-glow-1: rgba(102,187,106,.08);
    --body-glow-2: rgba(38,166,154,.06);
    --body-glow-3: rgba(255,183,77,.04);
    --orb-1: rgba(102,187,106,.12);
    --orb-2: rgba(38,166,154,.1);
    --orb-3: rgba(255,183,77,.08);
    --noise-opacity: 0.03;

    /* ---- 字体与布局 ---- */
    --font: -apple-system, "PingFang SC", "Microsoft YaHei", system-ui, sans-serif;
    --sidebar-w: 258px;
  }`;

const MINT_ROOT_MOBILE = MINT_ROOT.replace('--sidebar-w: 258px;', '--nav-h: 62px;');

// ─── Enhancement CSS ────────────────────────────────────────────
// Glass morphism, orbs, noise, animations, theme switcher, 3D tilt

const ENHANCEMENT_CSS = `
  /* ============================================================
     VISUAL ENHANCEMENTS — theme-dashboard fusion
     ============================================================ */

  /* ---- floating orb backgrounds ---- */
  .orb-layer { position: fixed; inset: 0; z-index: -2; pointer-events: none; overflow: hidden; }
  .orb { position: absolute; border-radius: 50%; filter: blur(60px); will-change: transform; }
  .orb.o1 { width: 420px; height: 420px; top: -120px; right: -80px; background: var(--orb-1); animation: orbFloat1 25s ease-in-out infinite; }
  .orb.o2 { width: 360px; height: 360px; bottom: -100px; left: 10%; background: var(--orb-2); animation: orbFloat2 30s ease-in-out infinite; }
  .orb.o3 { width: 300px; height: 300px; top: 40%; left: 50%; background: var(--orb-3); animation: orbFloat3 35s ease-in-out infinite; }
  @keyframes orbFloat1 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(-30px,40px)} }
  @keyframes orbFloat2 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(40px,-30px)} }
  @keyframes orbFloat3 { 0%,100%{transform:translate(0,0)} 50%{transform:translate(-50px,-20px)} }

  /* ---- SVG noise texture overlay ---- */
  .noise-layer { position: fixed; inset: 0; z-index: -1; pointer-events: none; opacity: var(--noise-opacity);
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='2'/%3E%3C/filter%3E%3Crect width='200' height='200' filter='url(%23n)'/%3E%3C/svg%3E"); }

  /* ---- glass morphism on cards ---- */
  .card, .tile, .panel, .modcard, .rec, .pin, .side-card, .mini, .quote, .hero, .hero-banner {
    backdrop-filter: blur(20px) saturate(1.2); -webkit-backdrop-filter: blur(20px) saturate(1.2); }
  body { background-image: radial-gradient(circle at 20% 15%, var(--body-glow-1), transparent 50%),
    radial-gradient(circle at 80% 85%, var(--body-glow-2), transparent 50%),
    radial-gradient(circle at 50% 50%, var(--body-glow-3), transparent 60%); }

  /* ---- 3D card tilt ---- */
  .tilt { transform-style: preserve-3d; transition: transform .08s ease-out; }
  .tilt .tilt-inner { transform: translateZ(20px); }

  /* ---- countUp animation ---- */
  .countup { display: inline-block; font-variant-numeric: tabular-nums; }

  /* ---- click ripple ---- */
  .ripple { position: absolute; border-radius: 50%; background: rgba(255,255,255,.4); pointer-events: none;
    animation: rippleAnim .6s ease-out; }
  @keyframes rippleAnim { from{transform:scale(0);opacity:.5} to{transform:scale(4);opacity:0} }

  /* ---- scroll reveal ---- */
  .reveal { opacity: 0; transform: translateY(24px); transition: opacity .5s ease, transform .5s ease; }
  .reveal.in { opacity: 1; transform: translateY(0); }

  /* ---- gradient progress bars ---- */
  .gbar-1 { background: linear-gradient(90deg, #66BB6A, #43A047); }
  .gbar-2 { background: linear-gradient(90deg, #26A69A, #00897B); }
  .gbar-3 { background: linear-gradient(90deg, #FFB74D, #FF9800); }
  .gbar-4 { background: linear-gradient(90deg, #EC407A, #C2185B); }

  /* ---- SVG ring gradient defs ---- */
  .ring-grad-1 { stop-color: #66BB6A; }
  .ring-grad-1b { stop-color: #43A047; }
  .ring-grad-2 { stop-color: #FFB74D; }
  .ring-grad-2b { stop-color: #FF9800; }
  .ring-grad-3 { stop-color: #26A69A; }
  .ring-grad-3b { stop-color: #00897B; }
  .ring-grad-4 { stop-color: #EC407A; }
  .ring-grad-4b { stop-color: #C2185B; }

  /* ---- trend chart colors ---- */
  .trend-stroke { stroke: #66BB6A; }
  .trend-fill { stop-color: #66BB6A; }
  .trend-grid { stroke: #E8F5E9; }
  .trend-label { fill: #8FBC8F; }

  /* ---- reduced motion ---- */
  @media (prefers-reduced-motion: reduce) {
    .orb { animation: none; } .reveal { opacity: 1; transform: none; } .ripple { display: none; }
  }
`;

// ─── Enhancement JS ──────────────────────────────────────────────
// countUp, ripple, 3D tilt, IntersectionObserver, theme switcher

const ENHANCEMENT_JS = `
  /* ============================================================
     VISUAL ENHANCEMENTS JS
     ============================================================ */

  // --- countUp: animate numbers from 0 to target ---
  function countUp(el, target, duration=1200) {
    const start = 0; const startTime = performance.now();
    const ease = t => 1 - Math.pow(1 - t, 3); // cubic ease-out
    function tick(now) {
      const p = Math.min((now - startTime) / duration, 1);
      const val = Math.round(start + (target - start) * ease(p));
      el.textContent = val;
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  // --- click ripple ---
  function addRipple(el) {
    el.style.position = el.style.position || 'relative';
    el.addEventListener('click', function(e) {
      const rect = this.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;
      const span = document.createElement('span');
      span.className = 'ripple';
      span.style.width = span.style.height = size + 'px';
      span.style.left = x + 'px';
      span.style.top = y + 'px';
      this.appendChild(span);
      setTimeout(() => span.remove(), 600);
    });
  }

  // --- 3D card tilt ---
  function addTilt(el, max=6) {
    el.classList.add('tilt');
    el.innerHTML = '<div class="tilt-inner">' + el.innerHTML + '</div>';
    el.addEventListener('mousemove', function(e) {
      const r = this.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width - 0.5;
      const py = (e.clientY - r.top) / r.height - 0.5;
      this.style.transform = 'perspective(600px) rotateY(' + (px * max) + 'deg) rotateX(' + (-py * max) + 'deg)';
    });
    el.addEventListener('mouseleave', function() { this.style.transform = ''; });
  }

  // --- IntersectionObserver scroll reveal ---
  function initReveal() {
    const io = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.reveal').forEach(function(el) { io.observe(el); });
  }

  // --- init all enhancements after DOM ready ---
  function initEnhancements() {
    // inject orb + noise layers
    if (!document.querySelector('.orb-layer')) {
      var ol = document.createElement('div'); ol.className = 'orb-layer';
      ol.innerHTML = '<div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div>';
      document.body.appendChild(ol);
    }
    if (!document.querySelector('.noise-layer')) {
      var nl = document.createElement('div'); nl.className = 'noise-layer';
      document.body.appendChild(nl);
    }
    // countUp on .countup elements
    document.querySelectorAll('.countup').forEach(function(el) {
      var target = parseInt(el.dataset.target || '0', 10);
      if (target > 0) countUp(el, target);
    });
    // ripple on buttons
    document.querySelectorAll('.btn, .qbtn, .modcard, .pin-chk, .hcell').forEach(function(el) {
      addRipple(el);
    });
    // 3D tilt on cards (desktop only — too heavy on mobile)
    if (window.innerWidth >= 768) {
      document.querySelectorAll('.modcard, .tile, .panel').forEach(function(el) {
        addTilt(el, 4);
      });
    }
    initReveal();
  }

  // run after original render
  var _origRender = (typeof render === 'function') ? render : null;
  if (_origRender) {
    var _renderWrapper = function() {
      _origRender.apply(null, arguments);
      setTimeout(initEnhancements, 50);
    };
    render = _renderWrapper;
  }
  // also run on DOMContentLoaded as fallback
  if (document.readyState !== 'loading') { setTimeout(initEnhancements, 100); }
  else { document.addEventListener('DOMContentLoaded', function() { setTimeout(initEnhancements, 100); }); }
`;

// ─── Build function ───────────────────────────────────────────────

function buildDesktop() {
  const src = fs.readFileSync(path.join(SRC_DIR, 'workbench-desktop.html'), 'utf8');
  let out = src;

  // 1. Replace :root block
  const rootStart = out.indexOf(':root {');
  const rootEnd = out.indexOf('}', out.indexOf('--sidebar-w', rootStart));
  if (rootStart === -1 || rootEnd === -1) throw new Error('Cannot find :root block in desktop template');
  out = out.slice(0, rootStart) + MINT_ROOT + out.slice(rootEnd + 1);

  // 2. Inject enhancement CSS before </style>
  out = out.replace('</style>', ENHANCEMENT_CSS + '\n</style>');

  // 3. Inject enhancement JS before the last </script>
  const lastScript = out.lastIndexOf('</script>');
  out = out.slice(0, lastScript) + ENHANCEMENT_JS + '\n</script>' + out.slice(lastScript + 9);

  // 4. Add reveal class to key elements
  out = out.replace(/class="hero-banner"/g, 'class="hero-banner reveal"');
  out = out.replace(/class="bento"/g, 'class="bento reveal"');

  // 5. Replace title
  out = out.replace('<title>我的工作台 · 桌面版</title>', '<title>🌿 我的工作台 · Mint</title>');

  fs.writeFileSync(path.join(OUT_DIR, 'workbench-desktop.html'), out, 'utf8');
}

function buildMobile() {
  const src = fs.readFileSync(path.join(SRC_DIR, 'workbench-mobile.html'), 'utf8');
  let out = src;

  // 1. Replace :root block
  const rootStart = out.indexOf(':root {');
  const rootEnd = out.indexOf('}', out.indexOf('--nav-h', rootStart));
  if (rootStart === -1 || rootEnd === -1) throw new Error('Cannot find :root block in mobile template');
  out = out.slice(0, rootStart) + MINT_ROOT_MOBILE + out.slice(rootEnd + 1);

  // 2. Inject enhancement CSS before </style>
  out = out.replace('</style>', ENHANCEMENT_CSS + '\n</style>');

  // 3. Inject enhancement JS before the last </script>
  const lastScript = out.lastIndexOf('</script>');
  out = out.slice(0, lastScript) + ENHANCEMENT_JS + '\n</script>' + out.slice(lastScript + 9);

  // 4. Add reveal class
  out = out.replace(/class="greet"/g, 'class="greet reveal"');

  // 5. Replace title
  out = out.replace('<title>我的工作台</title>', '<title>🌿 我的工作台 · Mint</title>');

  fs.writeFileSync(path.join(OUT_DIR, 'workbench-mobile.html'), out, 'utf8');
}

// ─── Main ────────────────────────────────────────────────────────

function main() {
  if (!fs.existsSync(OUT_DIR)) fs.mkdirSync(OUT_DIR, { recursive: true });
  buildDesktop();
  buildMobile();
  console.log('base ✓');
}

main();
