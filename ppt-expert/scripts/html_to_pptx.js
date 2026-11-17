#!/usr/bin/env node

/**
 * PPT Expert - HTML → PPTX 转换脚本
 * 使用 puppeteer 截图每页 → pptxgenjs 组合成 PPTX
 *
 * 依赖: npm install puppeteer pptxgenjs
 */

const fs = require('fs');
const path = require('path');

async function htmlToPptx(htmlFile, outputFile, options) {
  options = options || {};
  var width = options.width || 1280;
  var height = options.height || 720;

  var puppeteer, PptxGenJS;

  try {
    puppeteer = require('puppeteer');
  } catch (e) {
    console.error('缺少 puppeteer，请运行: npm install puppeteer');
    process.exit(1);
  }

  try {
    PptxGenJS = require('pptxgenjs');
  } catch (e) {
    console.error('缺少 pptxgenjs，请运行: npm install pptxgenjs');
    process.exit(1);
  }

  var absHtml = path.resolve(htmlFile);
  var absOutput = path.resolve(outputFile || absHtml.replace(/\.html$/, '.pptx'));

  console.log('启动浏览器...');
  var browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  var page = await browser.newPage();
  await page.setViewport({ width: width, height: height });
  await page.goto('file://' + absHtml, { waitUntil: 'networkidle0' });

  // 获取所有幻灯片
  var slideCount = await page.evaluate(function () {
    return document.querySelectorAll('.slide').length;
  });

  console.log('共 ' + slideCount + ' 页幻灯片');

  var pptx = new PptxGenJS();
  pptx.defineLayout({ name: 'CUSTOM', width: 13.33, height: 7.5 }); // 16:9
  pptx.layout = 'CUSTOM';

  for (var i = 0; i < slideCount; i++) {
    console.log('处理第 ' + (i + 1) + '/' + slideCount + ' 页...');

    // 显示当前页，隐藏其他页
    await page.evaluate(function (index) {
      var slides = document.querySelectorAll('.slide');
      slides.forEach(function (s, idx) {
        s.classList.toggle('active', idx === index);
        s.style.display = idx === index ? 'block' : 'none';
        // 移除幻灯片的所有阴影和边框
        if (idx === index) {
          s.style.boxShadow = 'none';
          s.style.border = 'none';
          s.style.outline = 'none';
        }
      });
      // 隐藏控制栏
      var controls = document.querySelector('.controls');
      var toolbar = document.querySelector('.editor-toolbar');
      if (controls) controls.style.display = 'none';
      if (toolbar) toolbar.style.display = 'none';
      // 移除 deck 容器的 flex 居中
      var deck = document.querySelector('.deck');
      if (deck) {
        deck.style.padding = '0';
        deck.style.minHeight = 'auto';
        deck.style.background = 'transparent';
      }
      document.body.style.margin = '0';
      document.body.style.padding = '0';
      document.body.style.background = '#ffffff';
    }, i);

    // 截图
    var slideEl = await page.$('.slide.active');
    if (!slideEl) {
      console.error('找不到活动的幻灯片元素');
      continue;
    }

    // 确保幻灯片没有阴影
    await page.evaluate(function() {
      var slide = document.querySelector('.slide.active');
      if (slide) {
        slide.style.boxShadow = 'none';
        slide.style.filter = 'none';
      }
    });

    var screenshot = await slideEl.screenshot({ type: 'png' });

    // 添加到 PPTX
    var slide = pptx.addSlide();
    slide.addImage({
      data: 'data:image/png;base64,' + screenshot.toString('base64'),
      x: 0,
      y: 0,
      w: '100%',
      h: '100%'
    });
  }

  await browser.close();

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
    console.error('Usage: node html_to_pptx.js --input <presentation.html> [--output <output.pptx>]');
    process.exit(1);
  }

  htmlToPptx(inputFile, outputFile).catch(function (err) {
    console.error('转换失败:', err.message);
    process.exit(1);
  });
}

module.exports = { htmlToPptx: htmlToPptx };
