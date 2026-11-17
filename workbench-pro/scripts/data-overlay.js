/**
 * data-overlay.js — Scenario data overlay engine
 * ================================================
 * Applies a scenario JSON (owner/slogan/quotes/seeds/labels/etc.) onto
 * template HTML content using regex. Works regardless of the template's
 * current data values — no need to match exact strings.
 *
 * Used by generate.js (--scenario/--data) and _revert.js.
 *
 * Scenario JSON schema: see templates/scenarios/*.json
 */

// ─── Seed entry → JS source converter ───────────────────────────

function seedToJS(moduleKey, seeds) {
  const idBase = { todo: 10, checkin: 20, learn: 30, note: 60 }[moduleKey] || 0;
  const indent = '        '; // 8 spaces (matches template formatting)
  const lines = seeds.map((s, i) => {
    const id = idBase + i + 1;
    switch (moduleKey) {
      case 'todo':
        return `${indent}{ id: ${id}, title: ${JSON.stringify(s.title)}, priority: ${JSON.stringify(s.priority)}, done: ${s.done}, note: ${JSON.stringify(s.note || '')} }`;
      case 'checkin': {
        const days = s.logDays || [];
        const logParts = days.map(d => `[${d === 0 ? 'isoToday()' : `daysAgo(${d})`}]: 1`).join(', ');
        return `${indent}{ id: ${id}, title: ${JSON.stringify(s.title)}, log: { ${logParts} } }`;
      }
      case 'learn':
        return `${indent}{ id: ${id}, title: ${JSON.stringify(s.title)}, current: ${s.current}, target: ${s.target}, unit: ${JSON.stringify(s.unit)}, note: ${JSON.stringify(s.note || '')} }`;
      case 'note': {
        const dateExpr = s.dateDaysAgo !== undefined ? `daysAgo(${s.dateDaysAgo})` : 'isoToday()';
        return `${indent}{ id: ${id}, title: ${JSON.stringify(s.title)}, content: ${JSON.stringify(s.content)}, mood: ${JSON.stringify(s.mood)}, date: ${dateExpr} }`;
      }
      default:
        throw new Error(`Unknown module key: ${moduleKey}`);
    }
  });
  return lines.join(',\n') + ',';
}

// ─── Main overlay function ───────────────────────────────────────

function applyDataOverlay(content, data) {
  if (!data) return content;
  let s = content;
  let changes = 0;

  function patch(regex, replacement, label) {
    if (regex.test(s)) { s = s.replace(regex, replacement); changes++; }
    else if (label) console.warn('  ⚠ data miss:', label);
  }

  // 1. Simple string fields (owner/slogan/brand)
  if (data.owner)  patch(/(owner:\s*)"[^"]*"/, `$1"${data.owner}"`, 'owner');
  if (data.slogan) patch(/(slogan:\s*)"[^"]*"/, `$1"${data.slogan}"`, 'slogan');
  if (data.brand)  patch(/(brand:\s*)"[^"]*"/, `$1"${data.brand}"`, 'brand');

  // 2. Quotes array (7 daily quotes with day-of-week comments)
  if (data.quotes && data.quotes.length === 7) {
    const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    const quotesStr = data.quotes.map((q, i) => `    "${q}",       // ${days[i]}`).join('\n');
    patch(/(quotes:\s*\[)\n[\s\S]*?(\n\s+\],)/, `$1\n${quotesStr}$2`, 'quotes');
  }

  // 3. Trend title + unit + default seed
  if (data.trend) {
    if (data.trend.title) {
      patch(/(title:\s*)"[^"]*",\s*unit:\s*"[^"]*"/, `title: "${data.trend.title}", unit: "${data.trend.unit}"`, 'trend title');
    }
    if (data.trend.seed) {
      patch(/d\.__trend\s*=\s*\[[\d.\s,]*\];/, `d.__trend = [${data.trend.seed.join(', ')}];`, 'trend seed');
    }
  }

  // 4. Overview ring labels (key+label pairs in overview array)
  if (data.overviewLabels) {
    for (const [key, label] of Object.entries(data.overviewLabels)) {
      patch(
        new RegExp(`(key:\\s*"${key}",\\s*label:\\s*)"([^"]*)"`),
        `$1"${label}"`,
        `overview-${key}`
      );
    }
  }

  // 5. QuickAdd button labels (label+module pairs)
  if (data.quickAddLabels) {
    for (const [key, label] of Object.entries(data.quickAddLabels)) {
      patch(
        new RegExp(`(\\{\\s*label:\\s*)"([^"]*)"(,\\s*icon:[^}]*?module:\\s*"${key}")`),
        `$1"${label}"$3`,
        `quickAdd-${key}`
      );
    }
  }

  // 6. Module fields (name/desc/unit/moods/seed)
  if (data.modules) {
    // type field differs from key for 'learn' (type="progress")
    const typeMap = { todo: 'todo', checkin: 'checkin', learn: 'progress', note: 'note' };

    for (const [key, mod] of Object.entries(data.modules)) {
      // 6a. Module name
      if (mod.name) {
        patch(
          new RegExp(`(key:\\s*"${key}",\\s*name:\\s*)"([^"]*)"`),
          `$1"${mod.name}"`,
          `name-${key}`
        );
      }

      // 6b. Module desc (anchored by type to stay within the right module)
      if (mod.desc) {
        const type = typeMap[key] || key;
        patch(
          new RegExp(`(type:\\s*"${type}"[^\\n]*?desc:\\s*)"([^"]*)"`),
          `$1"${mod.desc}"`,
          `desc-${key}`
        );
      }

      // 6c. Learn module unit
      if (mod.unit && key === 'learn') {
        patch(
          /(type:\s*"progress",\s*unit:\s*)"([^"]*)"/,
          `$1"${mod.unit}"`,
          'learn-unit'
        );
      }

      // 6d. Note module moods
      if (mod.moods && key === 'note') {
        patch(
          /moods:\s*\[[^\]]*\]/,
          `moods: [${mod.moods.map(m => `"${m}"`).join(', ')}]`,
          'note-moods'
        );
      }

      // 6e. Seed array — find by module key, replace entries
      if (mod.seed) {
        const newSeed = seedToJS(key, mod.seed);
        const seedRegex = new RegExp(
          `(key:\\s*"${key}",\\s*name:[\\s\\S]*?seed:\\s*\\[)\\s*([\\s\\S]*?)(\\s+\\][^,]*,)`
        );
        if (seedRegex.test(s)) {
          s = s.replace(seedRegex, `$1\n${newSeed}$3`);
          changes++;
        } else {
          console.warn(`  ⚠ data miss: seed-${key}`);
        }
      }
    }
  }

  return { content: s, changes };
}

module.exports = { applyDataOverlay, seedToJS };
