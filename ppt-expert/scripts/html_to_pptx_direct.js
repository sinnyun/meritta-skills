#!/usr/bin/env node

/**
 * PPT Expert - HTML → PPTX 直接解析脚本
 * 读取微调后的 HTML，解析内容和样式，用 pptxgenjs 生成 PPTX
 * 保留用户在 HTML 上的文本和样式微调，不依赖 puppeteer
 *
 * 依赖: npm install cheerio pptxgenjs
 */

const fs = require('fs');
const path = require('path');

// ─── 工具函数 ───

/** 去掉 # 前缀，pptxgenjs 使用不带 # 的十六进制颜色 */
function stripHex(c) {
  if (!c) return undefined;
  return c.replace('#', '');
}

/** px → pt 转换（96 DPI 下 1px = 0.75pt） */
function pxToPt(px) {
  return Math.round(px * 0.75);
}

/** 检查元素是否有 radial-gradient 背景（装饰性光晕，应跳过） */
function hasRadialGradient(styleStr) {
  if (!styleStr) return false;
  return /radial-gradient/i.test(styleStr);
}

/** 检查元素或其祖先是否有 radial-gradient 背景（装饰性光晕，应跳过） */
function isDecorativeGlow($el, $) {
  if (!$el || !$el.length) return false;
  var current = $el;
  while (current && current.length) {
    if (hasRadialGradient(current.attr('style'))) return true;
    var parent = current.parent();
    if (!parent || !parent.length) break;
    // 到 section.slide 层级停止（不跨幻灯片）
    if (parent[0] && parent[0].tagName && parent[0].tagName.toLowerCase() === 'section') break;
    current = parent;
  }
  return false;
}

/** 解析内联 style 字符串，提取颜色、字号、粗细、对齐 */
function parseStyle(styleStr) {
  if (!styleStr) return {};
  var s = {};
  var colorMatch = styleStr.match(/(?:^|;)\s*color\s*:\s*(#[0-9a-fA-F]{3,8})/);
  if (colorMatch) s.color = colorMatch[1];
  var sizeMatch = styleStr.match(/font-size\s*:\s*(\d+)px/);
  if (sizeMatch) s.fontSize = parseInt(sizeMatch[1]);
  var weightMatch = styleStr.match(/font-weight\s*:\s*(bold|\d+)/);
  if (weightMatch) {
    var w = weightMatch[1];
    s.bold = (w === 'bold' || parseInt(w) >= 600);
  }
  var alignMatch = styleStr.match(/text-align\s*:\s*(left|center|right)/);
  if (alignMatch) s.align = alignMatch[1];
  return s;
}

/** 从 HTML 的 <style> 块中提取 :root CSS 变量，构建 palette */
function extractTheme(html) {
  var theme = {};
  var styleRegex = /<style[^>]*>([\s\S]*?)<\/style>/g;
  var match;
  while ((match = styleRegex.exec(html)) !== null) {
    var css = match[1];
    var rootMatch = css.match(/:root\s*\{([^}]+)\}/);
    if (rootMatch) {
      var vars = rootMatch[1];
      var varRegex = /--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})/g;
      var vm;
      while ((vm = varRegex.exec(vars)) !== null) {
        var key = vm[1];
        var val = vm[2];
        if (key === 'primary') theme.primary = val;
        else if (key === 'secondary') theme.secondary = val;
        else if (key === 'accent') theme.accent = val;
        else if (key === 'bg-light') theme.bgLight = val;
        else if (key === 'text') theme.text = val;
        else if (key === 'text-light') theme.textLight = val;
      }
    }
  }
  // 默认值
  theme.primary = theme.primary || '#1E2761';
  theme.secondary = theme.secondary || '#CADCFC';
  theme.accent = theme.accent || '#FFFFFF';
  theme.bgLight = theme.bgLight || '#FFFFFF';
  theme.text = theme.text || '#1E2761';
  theme.textLight = theme.textLight || '#6B7280';
  return theme;
}

// ─── HTML 解析（cheerio） ───

/** 解析 HTML，返回 { palette, slides } */
function parseHTML(html) {
  var cheerio;
  try {
    cheerio = require('cheerio');
  } catch (e) {
    console.error('缺少 cheerio，请运行: npm install cheerio');
    process.exit(1);
  }

  var $ = cheerio.load(html);
  var theme = extractTheme(html);

  // 构建 palette（去掉 # 前缀）
  var palette = {
    primary: stripHex(theme.primary),
    secondary: stripHex(theme.secondary),
    accent: stripHex(theme.accent),
    bgLight: stripHex(theme.bgLight),
    text: stripHex(theme.text),
    textLight: stripHex(theme.textLight)
  };

  var slides = [];
  $('.slide').each(function (i, el) {
    var $slide = $(el);
    var layout = $slide.attr('data-layout') || detectLayout($slide, $);
    var data = extractSlideData($slide, layout, $);
    slides.push({ layout: layout, data: data });
  });

  return { palette: palette, slides: slides };
}

/** 当没有 data-layout 时，从结构推断布局类型 */
function detectLayout($slide, $) {
  if ($slide.hasClass('slide-cover')) return 'cover';
  if ($slide.hasClass('slide-content')) return 'content';
  if ($slide.hasClass('slide-end')) return 'end';
  if ($slide.find('.metric').length > 0) return 'data';
  var style = $slide.attr('style') || '';
  if (style.indexOf('grid-template-columns') >= 0) return 'split';
  var h3s = $slide.find('h3');
  if (h3s.length > 2) return 'timeline';
  if (h3s.length === 2) return 'comparison';
  return 'content';
}

/** 根据布局类型分发到对应的提取函数 */
function extractSlideData($slide, layout, $) {
  switch (layout) {
    case 'cover': return extractCover($slide, $);
    case 'content': return extractContent($slide, $);
    case 'data': return extractData($slide, $);
    case 'split': return extractSplit($slide, $);
    case 'timeline': return extractTimeline($slide, $);
    case 'comparison': return extractComparison($slide, $);
    case 'end': return extractEnd($slide, $);
    default: return extractContent($slide, $);
  }
}

function extractCover($slide, $) {
  var $h1 = $slide.find('h1').first();
  // 若标题处于装饰性光晕内，跳过（避免提取光晕文字）
  if (isDecorativeGlow($h1, $)) $h1 = $slide.find('h1').not(function (_, el) {
    return isDecorativeGlow($(el), $);
  }).first();
  var $sub = $slide.find('.subtitle').first();
  if (isDecorativeGlow($sub, $)) $sub = $();
  return {
    title: $h1.text().trim(),
    titleStyles: parseStyle($h1.attr('style')),
    subtitle: $sub.text().trim(),
    subtitleStyles: parseStyle($sub.attr('style'))
  };
}

function extractContent($slide, $) {
  var $h2 = $slide.find('h2').first();
  var items = [];
  $slide.find('li').each(function (j, li) {
    var $li = $(li);
    // 跳过带有 radial-gradient 背景的装饰性元素（含祖先链检查）
    if (isDecorativeGlow($li, $)) return;
    items.push({ text: $li.text().trim(), styles: parseStyle($li.attr('style')) });
  });
  return {
    title: $h2.text().trim(),
    titleStyles: parseStyle($h2.attr('style')),
    items: items
  };
}

function extractData($slide, $) {
  var $h2 = $slide.find('h2').first();
  var metrics = [];
  $slide.find('.metric').each(function (j, m) {
    var $m = $(m);
    // 跳过装饰性光晕内的 metric
    if (isDecorativeGlow($m, $)) return;
    var $val = $m.find('.metric-value');
    var $label = $m.find('.metric-label');
    metrics.push({
      value: $val.text().trim(),
      label: $label.text().trim(),
      valueStyles: parseStyle($val.attr('style')),
      labelStyles: parseStyle($label.attr('style'))
    });
  });
  return {
    title: $h2.text().trim(),
    titleStyles: parseStyle($h2.attr('style')),
    metrics: metrics
  };
}

function extractSplit($slide, $) {
  var $h2 = $slide.find('h2').first();
  var items = [];
  $slide.find('li').each(function (j, li) {
    var $li = $(li);
    // 跳过装饰性光晕内的 li
    if (isDecorativeGlow($li, $)) return;
    items.push({ text: $li.text().trim(), styles: parseStyle($li.attr('style')) });
  });
  return {
    title: $h2.text().trim(),
    titleStyles: parseStyle($h2.attr('style')),
    items: items
  };
}

function extractTimeline($slide, $) {
  var $h2 = $slide.find('h2').first();
  var steps = [];
  $slide.find('h3').each(function (j, h3) {
    var $h3 = $(h3);
    // 跳过装饰性光晕内的 h3
    if (isDecorativeGlow($h3, $)) return;
    var $stepDiv = $h3.parent();
    var $p = $stepDiv.find('p');
    steps.push({
      title: $h3.text().trim(),
      desc: $p.text().trim(),
      titleStyles: parseStyle($h3.attr('style')),
      descStyles: parseStyle($p.attr('style'))
    });
  });
  return {
    title: $h2.text().trim(),
    titleStyles: parseStyle($h2.attr('style')),
    steps: steps
  };
}

function extractComparison($slide, $) {
  var $h2 = $slide.find('h2').first();
  var $h3s = $slide.find('h3');
  var $leftCol = $($h3s[0]).parent();
  var $rightCol = $($h3s[1]).parent();

  function extractCol($col) {
    var $h3 = $col.find('h3').first();
    var items = [];
    $col.find('li').each(function (j, li) {
      var $li = $(li);
      // 跳过装饰性光晕内的 li
      if (isDecorativeGlow($li, $)) return;
      items.push({ text: $li.text().trim(), styles: parseStyle($li.attr('style')) });
    });
    return {
      title: $h3.text().trim(),
      titleStyles: parseStyle($h3.attr('style')),
      items: items
    };
  }

  return {
    title: $h2.text().trim(),
    titleStyles: parseStyle($h2.attr('style')),
    left: extractCol($leftCol),
    right: extractCol($rightCol)
  };
}

function extractEnd($slide, $) {
  var $h2 = $slide.find('h2').first();
  // 若主标题处于装饰性光晕内，尝试找下一个不在光晕内的 h2
  if (isDecorativeGlow($h2, $)) {
    var $alt = $slide.find('h2').filter(function (_, el) {
      return !isDecorativeGlow($(el), $);
    }).first();
    if ($alt.length) $h2 = $alt;
  }
  var $p = $slide.find('p').first();
  if (isDecorativeGlow($p, $)) {
    var $altP = $slide.find('p').filter(function (_, el) {
      return !isDecorativeGlow($(el), $);
    }).first();
    if ($altP.length) $p = $altP;
  }
  return {
    title: $h2.text().trim(),
    titleStyles: parseStyle($h2.attr('style')),
    subtitle: $p.text().trim(),
    subtitleStyles: parseStyle($p.attr('style'))
  };
}

// ─── 样式辅助：从 styles 对象获取覆盖值，否则返回默认 ───

function getColor(styles, defaultColor) {
  if (styles && styles.color) return stripHex(styles.color);
  return defaultColor;
}

function getSize(styles, defaultSize) {
  if (styles && styles.fontSize) return pxToPt(styles.fontSize);
  return defaultSize;
}

function getBold(styles, defaultBold) {
  if (styles && styles.bold !== undefined) return styles.bold;
  return defaultBold;
}

function getAlign(styles, defaultAlign) {
  if (styles && styles.align) return styles.align;
  return defaultAlign;
}

// ─── PPTX 布局生成器（样式感知）───

var LAYOUTS = {
  cover: function (pptx, slide, data, palette) {
    slide.background = { color: palette.bgLight };

    slide.addShape(pptx.ShapeType.rect, {
      x: 8.5, y: 0, w: 4.83, h: 7.5,
      fill: { color: palette.primary }
    });

    slide.addShape(pptx.ShapeType.rect, {
      x: 8.5, y: 0, w: 4.83, h: 7.5,
      fill: { color: palette.secondary, transparency: 60 }
    });

    slide.addText(data.title || '演示文稿', {
      x: 0.8, y: 2.2, w: 7.2, h: 2.0,
      fontSize: getSize(data.titleStyles, 44),
      bold: getBold(data.titleStyles, true),
      color: getColor(data.titleStyles, palette.primary),
      fontFace: 'Geist', align: 'left', valign: 'middle'
    });

    slide.addText(data.subtitle || '', {
      x: 0.8, y: 4.3, w: 7.2, h: 0.8,
      fontSize: getSize(data.subtitleStyles, 20),
      color: getColor(data.subtitleStyles, palette.textLight),
      fontFace: 'Geist', align: 'left', valign: 'top'
    });
  },

  content: function (pptx, slide, data, palette) {
    slide.background = { color: palette.bgLight };

    slide.addText(data.title || '', {
      x: 0.8, y: 0.5, w: 11.73, h: 1.0,
      fontSize: getSize(data.titleStyles, 32),
      bold: getBold(data.titleStyles, true),
      color: getColor(data.titleStyles, palette.primary),
      fontFace: 'Geist', align: getAlign(data.titleStyles, 'left'), valign: 'middle'
    });

    slide.addShape(pptx.ShapeType.line, {
      x: 0.8, y: 1.5, w: 2.0, h: 0,
      line: { color: palette.primary, width: 3 }
    });

    var items = (data.items || []).map(function (item) {
      return {
        text: item.text,
        options: {
          bullet: { code: '2022' },
          breakLine: true,
          fontSize: getSize(item.styles, 18),
          color: getColor(item.styles, palette.text),
          bold: getBold(item.styles, false),
          paraSpaceAfter: 12
        }
      };
    });
    if (items.length > 0) {
      slide.addText(items, {
        x: 0.8, y: 1.8, w: 11.73, h: 5.0,
        fontFace: 'Geist', align: 'left', valign: 'top'
      });
    }
  },

  data: function (pptx, slide, data, palette) {
    slide.background = { color: palette.bgLight };

    slide.addText(data.title || '', {
      x: 0.8, y: 0.5, w: 11.73, h: 1.0,
      fontSize: getSize(data.titleStyles, 32),
      bold: getBold(data.titleStyles, true),
      color: getColor(data.titleStyles, palette.primary),
      fontFace: 'Geist', align: getAlign(data.titleStyles, 'left'), valign: 'middle'
    });

    var metrics = data.metrics || [];
    var cardWidth = 3.5;
    var gap = 0.4;
    var totalWidth = metrics.length * cardWidth + (metrics.length - 1) * gap;
    var startX = (13.33 - totalWidth) / 2;

    metrics.forEach(function (m, i) {
      var x = startX + i * (cardWidth + gap);

      slide.addShape(pptx.ShapeType.roundRect, {
        x: x, y: 2.2, w: cardWidth, h: 3.5,
        fill: { color: palette.bgLight },
        line: { color: palette.secondary, width: 2 },
        rectRadius: 0.1
      });

      slide.addText(m.value || '', {
        x: x, y: 2.6, w: cardWidth, h: 1.5,
        fontSize: getSize(m.valueStyles, 40),
        bold: getBold(m.valueStyles, true),
        color: getColor(m.valueStyles, palette.primary),
        fontFace: 'Geist', align: 'center', valign: 'middle'
      });

      slide.addText(m.label || '', {
        x: x, y: 4.2, w: cardWidth, h: 0.8,
        fontSize: getSize(m.labelStyles, 16),
        color: getColor(m.labelStyles, palette.textLight),
        fontFace: 'Geist', align: 'center', valign: 'top'
      });
    });
  },

  split: function (pptx, slide, data, palette) {
    slide.background = { color: palette.bgLight };

    slide.addShape(pptx.ShapeType.roundRect, {
      x: 6.67, y: 1.0, w: 5.87, h: 5.5,
      fill: { color: palette.secondary },
      line: { color: palette.primary, width: 0 },
      rectRadius: 0.15
    });

    slide.addShape(pptx.ShapeType.roundRect, {
      x: 6.67, y: 1.0, w: 5.87, h: 5.5,
      fill: { color: palette.primary, transparency: 80 },
      line: { width: 0 },
      rectRadius: 0.15
    });

    slide.addText(data.title || '', {
      x: 0.8, y: 1.0, w: 5.5, h: 1.2,
      fontSize: getSize(data.titleStyles, 28),
      bold: getBold(data.titleStyles, true),
      color: getColor(data.titleStyles, palette.primary),
      fontFace: 'Geist', align: 'left', valign: 'middle'
    });

    var items = (data.items || []).map(function (item) {
      return {
        text: item.text,
        options: {
          bullet: { code: '2022' },
          breakLine: true,
          fontSize: getSize(item.styles, 16),
          color: getColor(item.styles, palette.text),
          bold: getBold(item.styles, false),
          paraSpaceAfter: 10
        }
      };
    });
    if (items.length > 0) {
      slide.addText(items, {
        x: 0.8, y: 2.5, w: 5.5, h: 4.0,
        fontFace: 'Geist', align: 'left', valign: 'top'
      });
    }
  },

  timeline: function (pptx, slide, data, palette) {
    slide.background = { color: palette.bgLight };

    slide.addText(data.title || '', {
      x: 0.8, y: 0.5, w: 11.73, h: 1.0,
      fontSize: getSize(data.titleStyles, 32),
      bold: getBold(data.titleStyles, true),
      color: getColor(data.titleStyles, palette.primary),
      fontFace: 'Geist', align: getAlign(data.titleStyles, 'center'), valign: 'middle'
    });

    var steps = data.steps || [];
    var stepWidth = 11.0 / Math.max(steps.length, 1);

    steps.forEach(function (step, i) {
      var cx = 1.16 + i * stepWidth + stepWidth / 2;

      if (i < steps.length - 1) {
        slide.addShape(pptx.ShapeType.line, {
          x: cx + 0.2, y: 3.0, w: stepWidth - 0.4, h: 0,
          line: { color: palette.secondary, width: 2 }
        });
      }

      slide.addShape(pptx.ShapeType.ellipse, {
        x: cx - 0.3, y: 2.7, w: 0.6, h: 0.6,
        fill: { color: palette.primary },
        line: { width: 0 }
      });

      slide.addText(String(i + 1), {
        x: cx - 0.3, y: 2.7, w: 0.6, h: 0.6,
        fontSize: 14, bold: true, color: 'FFFFFF',
        fontFace: 'Geist', align: 'center', valign: 'middle'
      });

      slide.addText(step.title || '', {
        x: cx - stepWidth / 2 + 0.1, y: 3.6, w: stepWidth - 0.2, h: 0.6,
        fontSize: getSize(step.titleStyles, 18),
        bold: getBold(step.titleStyles, true),
        color: getColor(step.titleStyles, palette.primary),
        fontFace: 'Geist', align: 'center', valign: 'top'
      });

      slide.addText(step.desc || '', {
        x: cx - stepWidth / 2 + 0.1, y: 4.3, w: stepWidth - 0.2, h: 1.5,
        fontSize: getSize(step.descStyles, 14),
        color: getColor(step.descStyles, palette.textLight),
        fontFace: 'Geist', align: 'center', valign: 'top'
      });
    });
  },

  comparison: function (pptx, slide, data, palette) {
    slide.background = { color: palette.bgLight };

    slide.addText(data.title || '', {
      x: 0.8, y: 0.5, w: 11.73, h: 1.0,
      fontSize: getSize(data.titleStyles, 32),
      bold: getBold(data.titleStyles, true),
      color: getColor(data.titleStyles, palette.primary),
      fontFace: 'Geist', align: getAlign(data.titleStyles, 'center'), valign: 'middle'
    });

    var left = data.left || {};
    var right = data.right || {};
    var colWidth = 5.5;
    var gap = 0.33;
    var startX = (13.33 - colWidth * 2 - gap) / 2;

    // 左侧
    slide.addShape(pptx.ShapeType.roundRect, {
      x: startX, y: 1.8, w: colWidth, h: 5.0,
      fill: { color: 'F9FAFB' },
      line: { color: palette.secondary, width: 1 },
      rectRadius: 0.1
    });

    slide.addText(left.title || '', {
      x: startX, y: 2.0, w: colWidth, h: 0.8,
      fontSize: getSize(left.titleStyles, 22),
      bold: getBold(left.titleStyles, true),
      color: getColor(left.titleStyles, palette.primary),
      fontFace: 'Geist', align: 'center', valign: 'middle'
    });

    var leftItems = (left.items || []).map(function (item) {
      return {
        text: item.text,
        options: {
          bullet: { code: '2022' }, breakLine: true,
          fontSize: getSize(item.styles, 16),
          color: getColor(item.styles, palette.text),
          bold: getBold(item.styles, false),
          paraSpaceAfter: 10
        }
      };
    });
    if (leftItems.length > 0) {
      slide.addText(leftItems, {
        x: startX + 0.3, y: 3.0, w: colWidth - 0.6, h: 3.5,
        fontFace: 'Geist', align: 'left', valign: 'top'
      });
    }

    // 右侧（高亮）
    var rightX = startX + colWidth + gap;
    slide.addShape(pptx.ShapeType.roundRect, {
      x: rightX, y: 1.8, w: colWidth, h: 5.0,
      fill: { color: palette.primary, transparency: 92 },
      line: { color: palette.primary, width: 2 },
      rectRadius: 0.1
    });

    slide.addText(right.title || '', {
      x: rightX, y: 2.0, w: colWidth, h: 0.8,
      fontSize: getSize(right.titleStyles, 22),
      bold: getBold(right.titleStyles, true),
      color: getColor(right.titleStyles, palette.primary),
      fontFace: 'Geist', align: 'center', valign: 'middle'
    });

    var rightItems = (right.items || []).map(function (item) {
      return {
        text: item.text,
        options: {
          bullet: { code: '2022' }, breakLine: true,
          fontSize: getSize(item.styles, 16),
          color: getColor(item.styles, palette.text),
          bold: getBold(item.styles, false),
          paraSpaceAfter: 10
        }
      };
    });
    if (rightItems.length > 0) {
      slide.addText(rightItems, {
        x: rightX + 0.3, y: 3.0, w: colWidth - 0.6, h: 3.5,
        fontFace: 'Geist', align: 'left', valign: 'top'
      });
    }
  },

  end: function (pptx, slide, data, palette) {
    slide.background = { color: palette.bgLight };

    slide.addShape(pptx.ShapeType.rect, {
      x: 0, y: 0, w: 13.33, h: 0.15,
      fill: { color: palette.primary },
      line: { width: 0 }
    });

    slide.addText(data.title || '谢谢', {
      x: 0, y: 2.5, w: 13.33, h: 1.5,
      fontSize: getSize(data.titleStyles, 48),
      bold: getBold(data.titleStyles, true),
      color: getColor(data.titleStyles, palette.primary),
      fontFace: 'Geist', align: getAlign(data.titleStyles, 'center'), valign: 'middle'
    });

    slide.addText(data.subtitle || '', {
      x: 0, y: 4.2, w: 13.33, h: 0.8,
      fontSize: getSize(data.subtitleStyles, 22),
      color: getColor(data.subtitleStyles, palette.textLight),
      fontFace: 'Geist', align: 'center', valign: 'top'
    });
  }
};

// ─── 主生成函数 ───

async function htmlToPptx(htmlFile, outputFile) {
  var PptxGenJS;
  try {
    PptxGenJS = require('pptxgenjs');
  } catch (e) {
    console.error('缺少 pptxgenjs，请运行: npm install pptxgenjs');
    process.exit(1);
  }

  var absHtml = path.resolve(htmlFile);
  var absOutput = path.resolve(outputFile || absHtml.replace(/\.html$/, '.pptx'));

  var html = fs.readFileSync(absHtml, 'utf-8');
  var parsed = parseHTML(html);
  var palette = parsed.palette;
  var slides = parsed.slides;

  console.log('共 ' + slides.length + ' 页幻灯片');

  var pptx = new PptxGenJS();
  pptx.defineLayout({ name: 'CUSTOM', width: 13.33, height: 7.5 });
  pptx.layout = 'CUSTOM';
  pptx.author = 'PPT Expert';
  pptx.company = 'PPT Expert';
  pptx.subject = '演示文稿';

  for (var i = 0; i < slides.length; i++) {
    console.log('处理第 ' + (i + 1) + '/' + slides.length + ' 页...');
    var slide = pptx.addSlide();
    var layout = LAYOUTS[slides[i].layout] || LAYOUTS.content;
    layout(pptx, slide, slides[i].data, palette);
  }

  await pptx.writeFile({ fileName: absOutput });
  console.log('PPTX 已导出: ' + absOutput);
  return absOutput;
}

// CLI
if (require.main === module) {
  var args = process.argv.slice(2);
  var inputFile = null;
  var outputFile = null;

  for (var i = 0; i < args.length; i++) {
    if (args[i] === '--input' || args[i] === '-i') inputFile = args[++i];
    else if (args[i] === '--output' || args[i] === '-o') outputFile = args[++i];
  }

  if (!inputFile) {
    console.error('Usage: node html_to_pptx_direct.js --input <presentation.html> [--output <output.pptx>]');
    process.exit(1);
  }

  htmlToPptx(inputFile, outputFile).catch(function (err) {
    console.error('转换失败:', err.message);
    process.exit(1);
  });
}

module.exports = { htmlToPptx: htmlToPptx, parseHTML: parseHTML };
