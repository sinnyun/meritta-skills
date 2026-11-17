// _revert.js — 恢复基准模板到 dev 默认数据（一次性，用完即删）
// 读取 dev.json 场景，用 data-overlay 的 regex 逻辑覆盖基准模板
const fs = require('fs'), path = require('path');
const { applyDataOverlay } = require('./data-overlay');

const SCENARIOS = path.join(__dirname, '..', 'templates', 'scenarios');
const TEMPLATES = path.join(__dirname, '..', 'templates');

for (const file of ['workbench-mobile.html', 'workbench-desktop.html']) {
  const f = path.join(TEMPLATES, file);
  if (!fs.existsSync(f)) { console.warn('skip (missing):', file); continue; }
  const content = fs.readFileSync(f, 'utf8');
  const dev = JSON.parse(fs.readFileSync(path.join(SCENARIOS, 'dev.json'), 'utf8'));
  const { content: out, changes } = applyDataOverlay(content, dev);
  fs.writeFileSync(f, out, 'utf8');
  console.log(`${file}: ${changes} fields restored to dev defaults`);
}
console.log('=== REVERT DONE ===');
