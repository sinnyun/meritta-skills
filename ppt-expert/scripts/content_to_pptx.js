#!/usr/bin/env node

/**
 * PPT Expert - content.json → PPTX 直接生成脚本
 * 不依赖 puppeteer，直接用 pptxgenjs 构建原生 PPTX 元素
 * 快速、准确、生成效果好
 *
 * 依赖: npm install pptxgenjs
 */

const fs = require('fs');
const path = require('path');

// ─── 配色方案（与 generate_html.js 保持一致）───
const COLOR_PALETTES = {
  'midnight-executive': {
    name: '午夜商务', primary: '#1E2761', secondary: '#CADCFC',
    accent: '#FFFFFF', bgLight: '#FFFFFF', text: '#1E2761', textLight: '#6B7280'
  },
  'tech-dark': {
    name: '科技深空', primary: '#58A6FF', secondary: '#161B22',
    accent: '#58A6FF', bgLight: '#0D1117', text: '#F0F6FC', textLight: '#8B949E'
  },
  'coral-energy': {
    name: '珊瑚活力', primary: '#F96167', secondary: '#F9E795',
    accent: '#2F3C7E', bgLight: '#FFFFFF', text: '#1F2937', textLight: '#6B7280'
  },
  'warm-terracotta': {
    name: '暖陶简约', primary: '#B85042', secondary: '#E7E8D1',
    accent: '#A7BEAE', bgLight: '#FDFBF7', text: '#3D3D3D', textLight: '#6B7280'
  },
  'ocean-gradient': {
    name: '海洋渐变', primary: '#065A82', secondary: '#1C7293',
    accent: '#21295C', bgLight: '#FFFFFF', text: '#065A82', textLight: '#6B7280'
  },
  'charcoal-minimal': {
    name: '炭灰极简', primary: '#36454F', secondary: '#F2F2F2',
    accent: '#212121', bgLight: '#FFFFFF', text: '#36454F', textLight: '#8B949E'
  },
  'teal-trust': {
    name: '青绿信任', primary: '#028090', secondary: '#00A896',
    accent: '#02C39A', bgLight: '#FFFFFF', text: '#065A60', textLight: '#374151'
  },
  'berry-cream': {
    name: '莓果奶油', primary: '#6D2E46', secondary: '#A26769',
    accent: '#ECE2D0', bgLight: '#FFFFFF', text: '#6D2E46', textLight: '#8B949E'
  }
};

// ─── PPTX 布局生成器 ───
// 每个布局函数接收 (pptx, slide, data, palette)，直接在 pptx slide 上添加元素

const LAYOUTS = {
  // 封面：左侧标题+副标题，右侧装饰色块
  cover: function (pptx, slide, data, palette) {
    // 背景
    slide.background = { color: palette.bgLight.replace('#', '') };

    // 右侧装饰色块
    slide.addShape(pptx.ShapeType.rect, {
      x: 8.5, y: 0, w: 4.83, h: 7.5,
      fill: { color: palette.primary.replace('#', '') }
    });

    // 装饰色块上的渐变层
    slide.addShape(pptx.ShapeType.rect, {
      x: 8.5, y: 0, w: 4.83, h: 7.5,
      fill: { color: palette.secondary.replace('#', ''), transparency: 60 }
    });

    // 标题
    slide.addText(data.title || '演示文稿', {
      x: 0.8, y: 2.2, w: 7.2, h: 2.0,
      fontSize: 44, bold: true, color: palette.primary.replace('#', ''),
      fontFace: 'Geist', align: 'left', valign: 'middle'
    });

    // 副标题
    slide.addText(data.subtitle || '', {
      x: 0.8, y: 4.3, w: 7.2, h: 0.8,
      fontSize: 20, color: palette.textLight.replace('#', ''),
      fontFace: 'Geist', align: 'left', valign: 'top'
    });
  },

  // 内容页：标题 + 要点列表
  content: function (pptx, slide, data, palette) {
    slide.background = { color: palette.bgLight.replace('#', '') };

    // 标题
    slide.addText(data.title || '', {
      x: 0.8, y: 0.5, w: 11.73, h: 1.0,
      fontSize: 32, bold: true, color: palette.primary.replace('#', ''),
      fontFace: 'Geist', align: 'left', valign: 'middle'
    });

    // 标题下分隔线
    slide.addShape(pptx.ShapeType.line, {
      x: 0.8, y: 1.5, w: 2.0, h: 0,
      line: { color: palette.primary.replace('#', ''), width: 3 }
    });

    // 要点列表
    var items = (data.items || []).map(function (item) {
      return { text: item, options: { bullet: { code: '2022' }, breakLine: true, fontSize: 18, color: palette.text.replace('#', ''), paraSpaceAfter: 12 } };
    });
    if (items.length > 0) {
      slide.addText(items, {
        x: 0.8, y: 1.8, w: 11.73, h: 5.0,
        fontFace: 'Geist', align: 'left', valign: 'top'
      });
    }
  },

  // 数据页：标题 + 指标卡片
  data: function (pptx, slide, data, palette) {
    slide.background = { color: palette.bgLight.replace('#', '') };

    // 标题
    slide.addText(data.title || '', {
      x: 0.8, y: 0.5, w: 11.73, h: 1.0,
      fontSize: 32, bold: true, color: palette.primary.replace('#', ''),
      fontFace: 'Geist', align: 'left', valign: 'middle'
    });

    // 指标卡片
    var metrics = data.metrics || [];
    var cardWidth = 3.5;
    var gap = 0.4;
    var totalWidth = metrics.length * cardWidth + (metrics.length - 1) * gap;
    var startX = (13.33 - totalWidth) / 2;

    metrics.forEach(function (m, i) {
      var x = startX + i * (cardWidth + gap);

      // 卡片背景
      slide.addShape(pptx.ShapeType.roundRect, {
        x: x, y: 2.2, w: cardWidth, h: 3.5,
        fill: { color: palette.bgLight.replace('#', '') },
        line: { color: palette.secondary.replace('#', ''), width: 2 },
        rectRadius: 0.1
      });

      // 指标值
      slide.addText(m.value || '', {
        x: x, y: 2.6, w: cardWidth, h: 1.5,
        fontSize: 40, bold: true, color: palette.primary.replace('#', ''),
        fontFace: 'Geist', align: 'center', valign: 'middle'
      });

      // 指标标签
      slide.addText(m.label || '', {
        x: x, y: 4.2, w: cardWidth, h: 0.8,
        fontSize: 16, color: palette.textLight.replace('#', ''),
        fontFace: 'Geist', align: 'center', valign: 'top'
      });
    });
  },

  // 分屏：左侧标题+列表，右侧装饰色块
  split: function (pptx, slide, data, palette) {
    slide.background = { color: palette.bgLight.replace('#', '') };

    // 右侧装饰色块
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 6.67, y: 1.0, w: 5.87, h: 5.5,
      fill: { color: palette.secondary.replace('#', '') },
      line: { color: palette.primary.replace('#', ''), width: 0 },
      rectRadius: 0.15
    });

    // 装饰色块上的渐变层
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 6.67, y: 1.0, w: 5.87, h: 5.5,
      fill: { color: palette.primary.replace('#', ''), transparency: 80 },
      line: { width: 0 },
      rectRadius: 0.15
    });

    // 左侧标题
    slide.addText(data.title || '', {
      x: 0.8, y: 1.0, w: 5.5, h: 1.2,
      fontSize: 28, bold: true, color: palette.primary.replace('#', ''),
      fontFace: 'Geist', align: 'left', valign: 'middle'
    });

    // 左侧要点
    var items = (data.items || []).map(function (item) {
      return { text: item, options: { bullet: { code: '2022' }, breakLine: true, fontSize: 16, color: palette.text.replace('#', ''), paraSpaceAfter: 10 } };
    });
    if (items.length > 0) {
      slide.addText(items, {
        x: 0.8, y: 2.5, w: 5.5, h: 4.0,
        fontFace: 'Geist', align: 'left', valign: 'top'
      });
    }
  },

  // 时间线：标题 + 横向步骤
  timeline: function (pptx, slide, data, palette) {
    slide.background = { color: palette.bgLight.replace('#', '') };

    // 标题
    slide.addText(data.title || '', {
      x: 0.8, y: 0.5, w: 11.73, h: 1.0,
      fontSize: 32, bold: true, color: palette.primary.replace('#', ''),
      fontFace: 'Geist', align: 'center', valign: 'middle'
    });

    // 步骤
    var steps = data.steps || [];
    var stepWidth = 11.0 / steps.length;

    steps.forEach(function (step, i) {
      var cx = 1.16 + i * stepWidth + stepWidth / 2;

      // 连接线（非最后一个）
      if (i < steps.length - 1) {
        slide.addShape(pptx.ShapeType.line, {
          x: cx + 0.2, y: 3.0, w: stepWidth - 0.4, h: 0,
          line: { color: palette.secondary.replace('#', ''), width: 2 }
        });
      }

      // 步骤圆圈
      slide.addShape(pptx.ShapeType.ellipse, {
        x: cx - 0.3, y: 2.7, w: 0.6, h: 0.6,
        fill: { color: palette.primary.replace('#', '') },
        line: { width: 0 }
      });

      // 步骤编号
      slide.addText(String(i + 1), {
        x: cx - 0.3, y: 2.7, w: 0.6, h: 0.6,
        fontSize: 14, bold: true, color: 'FFFFFF',
        fontFace: 'Geist', align: 'center', valign: 'middle'
      });

      // 步骤标题
      slide.addText(step.title || '', {
        x: cx - stepWidth / 2 + 0.1, y: 3.6, w: stepWidth - 0.2, h: 0.6,
        fontSize: 18, bold: true, color: palette.primary.replace('#', ''),
        fontFace: 'Geist', align: 'center', valign: 'top'
      });

      // 步骤描述
      slide.addText(step.desc || '', {
        x: cx - stepWidth / 2 + 0.1, y: 4.3, w: stepWidth - 0.2, h: 1.5,
        fontSize: 14, color: palette.textLight.replace('#', ''),
        fontFace: 'Geist', align: 'center', valign: 'top'
      });
    });
  },

  // 对比页：标题 + 左右对比
  comparison: function (pptx, slide, data, palette) {
    slide.background = { color: palette.bgLight.replace('#', '') };

    // 标题
    slide.addText(data.title || '', {
      x: 0.8, y: 0.5, w: 11.73, h: 1.0,
      fontSize: 32, bold: true, color: palette.primary.replace('#', ''),
      fontFace: 'Geist', align: 'center', valign: 'middle'
    });

    var left = data.left || {};
    var right = data.right || {};
    var colWidth = 5.5;
    var gap = 0.33;
    var startX = (13.33 - colWidth * 2 - gap) / 2;

    // 左侧卡片
    slide.addShape(pptx.ShapeType.roundRect, {
      x: startX, y: 1.8, w: colWidth, h: 5.0,
      fill: { color: 'F9FAFB' },
      line: { color: palette.secondary.replace('#', ''), width: 1 },
      rectRadius: 0.1
    });

    slide.addText(left.title || '', {
      x: startX, y: 2.0, w: colWidth, h: 0.8,
      fontSize: 22, bold: true, color: palette.primary.replace('#', ''),
      fontFace: 'Geist', align: 'center', valign: 'middle'
    });

    var leftItems = (left.items || []).map(function (item) {
      return { text: item, options: { bullet: { code: '2022' }, breakLine: true, fontSize: 16, color: palette.text.replace('#', ''), paraSpaceAfter: 10 } };
    });
    if (leftItems.length > 0) {
      slide.addText(leftItems, {
        x: startX + 0.3, y: 3.0, w: colWidth - 0.6, h: 3.5,
        fontFace: 'Geist', align: 'left', valign: 'top'
      });
    }

    // 右侧卡片（高亮）
    var rightX = startX + colWidth + gap;
    slide.addShape(pptx.ShapeType.roundRect, {
      x: rightX, y: 1.8, w: colWidth, h: 5.0,
      fill: { color: palette.primary.replace('#', ''), transparency: 92 },
      line: { color: palette.primary.replace('#', ''), width: 2 },
      rectRadius: 0.1
    });

    slide.addText(right.title || '', {
      x: rightX, y: 2.0, w: colWidth, h: 0.8,
      fontSize: 22, bold: true, color: palette.primary.replace('#', ''),
      fontFace: 'Geist', align: 'center', valign: 'middle'
    });

    var rightItems = (right.items || []).map(function (item) {
      return { text: item, options: { bullet: { code: '2022' }, breakLine: true, fontSize: 16, color: palette.text.replace('#', ''), paraSpaceAfter: 10 } };
    });
    if (rightItems.length > 0) {
      slide.addText(rightItems, {
        x: rightX + 0.3, y: 3.0, w: colWidth - 0.6, h: 3.5,
        fontFace: 'Geist', align: 'left', valign: 'top'
      });
    }
  },

  // 结尾页：居中感谢
  end: function (pptx, slide, data, palette) {
    slide.background = { color: palette.bgLight.replace('#', '') };

    // 装饰色块（顶部细条）
    slide.addShape(pptx.ShapeType.rect, {
      x: 0, y: 0, w: 13.33, h: 0.15,
      fill: { color: palette.primary.replace('#', '') },
      line: { width: 0 }
    });

    // 标题
    slide.addText(data.title || '谢谢', {
      x: 0, y: 2.5, w: 13.33, h: 1.5,
      fontSize: 48, bold: true, color: palette.primary.replace('#', ''),
      fontFace: 'Geist', align: 'center', valign: 'middle'
    });

    // 副标题
    slide.addText(data.subtitle || '', {
      x: 0, y: 4.2, w: 13.33, h: 0.8,
      fontSize: 22, color: palette.textLight.replace('#', ''),
      fontFace: 'Geist', align: 'center', valign: 'top'
    });
  }
};

// ─── 主生成函数 ───
async function contentToPptx(inputFile, outputFile, options) {
  options = options || {};

  var PptxGenJS;
  try {
    PptxGenJS = require('pptxgenjs');
  } catch (e) {
    console.error('缺少 pptxgenjs，请运行: npm install pptxgenjs');
    process.exit(1);
  }

  var absInput = path.resolve(inputFile);
  var absOutput = path.resolve(outputFile || absInput.replace(/\.json$/, '.pptx'));

  // 读取 content.json
  var content;
  try {
    content = JSON.parse(fs.readFileSync(absInput, 'utf-8'));
  } catch (e) {
    console.error('读取 content.json 失败:', e.message);
    process.exit(1);
  }

  var title = content.title || '演示文稿';
  var theme = content.theme || 'midnight-executive';
  var slides = content.slides || [];
  var palette = COLOR_PALETTES[theme] || COLOR_PALETTES['midnight-executive'];

  console.log('主题: ' + palette.name + ' (' + theme + ')');
  console.log('共 ' + slides.length + ' 页幻灯片');

  // 创建 PPTX
  var pptx = new PptxGenJS();
  pptx.defineLayout({ name: 'CUSTOM', width: 13.33, height: 7.5 });
  pptx.layout = 'CUSTOM';
  pptx.author = 'PPT Expert';
  pptx.company = 'PPT Expert';
  pptx.subject = title;

  // 生成每页
  for (var i = 0; i < slides.length; i++) {
    console.log('处理第 ' + (i + 1) + '/' + slides.length + ' 页...');
    var slide = pptx.addSlide();
    var layout = LAYOUTS[slides[i].layout] || LAYOUTS.content;
    layout(pptx, slide, slides[i].data || slides[i], palette);
  }

  // 导出
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
    console.error('Usage: node content_to_pptx.js --input <content.json> [--output <output.pptx>]');
    process.exit(1);
  }

  contentToPptx(inputFile, outputFile).catch(function (err) {
    console.error('转换失败:', err.message);
    process.exit(1);
  });
}

module.exports = { contentToPptx: contentToPptx };
