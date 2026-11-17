#!/usr/bin/env node
/**
 * workbench-pro 冒烟测试器
 * 用法: node smoke-test.js <html路径>
 *
 * 第 1 层 静态检查（任何环境可跑）：
 *   - 全部内联 <script> 语法检查（node vm）
 *   - 外链扫描（CDN/字体/图片/库，发现即失败）
 *   - 禁用 API 扫描（new Date('YYYY-MM-DD') 模式等）
 * 第 2 层 真机冒烟（装了 playwright + 本机有 Chromium 内核时自动启用）：
 *   - 手机 375×812 与桌面 1280×800 双视口加载
 *   - 采集 console error / pageerror（必须为零）
 *   - 横向溢出检查
 *   - 关键容器存在性（顶栏标题 / 今日列表 / 至少一个模块卡）
 *   - 截图 <页面名>.mobile.png / .desktop.png
 * 退出码：0 全绿；1 有失败项。
 */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const target = process.argv[2];
if (!target || !fs.existsSync(target)) {
  console.error('用法: node smoke-test.js <html路径>');
  process.exit(1);
}
const html = fs.readFileSync(target, 'utf8');
let failed = 0;
const fail = (...a) => { failed++; console.log('❌', ...a); };
const pass = (...a) => console.log('✅', ...a);

/* ---------- 第 1 层：静态检查 ---------- */
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
scripts.forEach((code, i) => {
  try { new vm.Script(code); pass(`脚本块 ${i + 1}/${scripts.length} 语法 OK`); }
  catch (e) { fail(`脚本块 ${i + 1} 语法错误: ${e.message}`); }
});

if (/(<link[\s>]|<script[^>]+src=|@import|url\(\s*['"]?https?:)/.test(html)) fail('检测到外部资源引用（铁律 1：全内联）');
else pass('无外部资源引用');

const badApi = [];
if (/new\s+Date\(\s*['"`]\d{4}-\d{2}-\d{2}/.test(html)) badApi.push("new Date('YYYY-MM-DD')  [Safari 时区坑]");
if (/crypto\.randomUUID/.test(html)) badApi.push('crypto.randomUUID  [iOS 15.4+]');
if (/structuredClone/.test(html)) badApi.push('structuredClone  [iOS 14.5+]');
if (/\.at\(/.test(html) && /Array|\]\.at\(/.test(html)) badApi.push('.at()  [iOS 15.4+]');
if (badApi.length) badApi.forEach(b => fail('禁用 API: ' + b));
else pass('无禁用 API 用法');

const containers = [['顶栏标题', /id="app-title"|<h1/], ['今日列表', /id="today-list"|today-list/]];
containers.forEach(([name, re]) => re.test(html) ? pass(`关键容器: ${name}`) : fail(`缺少关键容器: ${name}`));

/* ---------- 第 2 层：真机冒烟（可选） ---------- */
async function browserSmoke() {
  let chromium, exe;
  try { chromium = require('playwright').chromium; }
  catch { console.log('ℹ️ 未安装 playwright，跳过真机冒烟（静态检查已通过）'); return; }
  // 在 ms-playwright 缓存中找本机已有 Chromium 内核（避免联网下载）
  const cacheDir = path.join(process.env.LOCALAPPDATA || '', 'ms-playwright');
  if (fs.existsSync(cacheDir)) {
    for (const d of fs.readdirSync(cacheDir).sort().reverse()) {
      const candidates = [
        path.join(cacheDir, d, 'chrome-win', 'chrome.exe'),
        path.join(cacheDir, d, 'chrome-win64', 'chrome.exe'),
      ];
      exe = candidates.find(c => fs.existsSync(c));
      if (exe) break;
    }
  }
  if (!exe) { console.log('ℹ️ 未找到本机 Chromium 内核，跳过真机冒烟'); return; }

  const url = 'file:///' + path.resolve(target).replace(/\\/g, '/');
  const base = path.basename(target, '.html');
  const ctxOpts = { viewport: { width: 375, height: 812 }, isMobile: true, hasTouch: true };
  const desktopOpts = { viewport: { width: 1280, height: 800 } };

  for (const [label, opts] of [['mobile', ctxOpts], ['desktop', desktopOpts]]) {
    const browser = await chromium.launch({ headless: true, executablePath: exe });
    const ctx = await browser.newContext(opts);
    const page = await ctx.newPage();
    const errors = [];
    page.on('console', m => { if (m.type() === 'error') errors.push('[console] ' + m.text()); });
    page.on('pageerror', e => errors.push('[pageerror] ' + e.message));
    page.on('dialog', d => d.accept());
    await page.goto(url);
    await page.waitForTimeout(900);

    if (errors.length) { errors.forEach(e => fail(`[${label}] 运行时错误: ${e}`)); }
    else pass(`[${label}] 零运行时错误`);

    const overflow = await page.evaluate(() =>
      document.documentElement.scrollWidth > document.documentElement.clientWidth);
    overflow ? fail(`[${label}] 存在横向溢出`) : pass(`[${label}] 无横向溢出`);

    const ok = await page.evaluate(() => ({
      title: !!(document.getElementById('app-title') || document.querySelector('h1')),
      today: !!document.getElementById('today-list'),
      cards: document.querySelectorAll('.card').length,
    }));
    ok.title && ok.today && ok.cards >= 2
      ? pass(`[${label}] 结构完整（今日区 + ${ok.cards} 张卡片）`)
      : fail(`[${label}] 结构缺失 title=${ok.title} today=${ok.today} cards=${ok.cards}`);

    await page.screenshot({ path: `${base}.${label}.png`, fullPage: label === 'mobile' });
    await browser.close();
    console.log(`📷 截图: ${base}.${label}.png`);
  }
}

browserSmoke().then(() => {
  console.log(failed ? `\n结果: ${failed} 项失败，禁止交付` : '\n结果: 全部通过，可以交付');
  process.exit(failed ? 1 : 0);
}).catch(e => { fail('冒烟器自身异常: ' + e.message); process.exit(1); });
