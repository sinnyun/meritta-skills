#!/usr/bin/env node

/**
 * PPT Expert - HTML 版本生成脚本
 * 根据内容 JSON 生成可编辑的 HTML 演示文稿
 * 视觉设计遵循 design-taste-frontend 原则
 */

const fs = require('fs');
const path = require('path');

// ─── 配色方案 ───
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

// ─── 布局模板生成器 ───
const LAYOUTS = {
  cover: function (data, palette) {
    return '<section class="slide slide-cover" data-layout="cover">\n' +
      '  <div>\n' +
      '    <h1>' + esc(data.title || '演示文稿') + '</h1>\n' +
      '    <p class="subtitle">' + esc(data.subtitle || '') + '</p>\n' +
      '  </div>\n' +
      '  <div class="visual" style="background: linear-gradient(135deg, ' + palette.primary + ', ' + palette.secondary + ');"></div>\n' +
      '</section>';
  },

  content: function (data, palette) {
    var items = (data.items || []).map(function (item) {
      return '    <li>' + esc(item) + '</li>';
    }).join('\n');

    return '<section class="slide slide-content" data-layout="content">\n' +
      '  <h2>' + esc(data.title || '') + '</h2>\n' +
      '  <ul>\n' + items + '\n  </ul>\n' +
      '</section>';
  },

  data: function (data, palette) {
    var metrics = (data.metrics || []).map(function (m) {
      return '  <div class="metric">\n' +
        '    <div class="metric-value" style="color: ' + palette.primary + ';">' + esc(m.value || '') + '</div>\n' +
        '    <div class="metric-label">' + esc(m.label || '') + '</div>\n' +
        '  </div>';
    }).join('\n');

    return '<section class="slide" data-layout="data">\n' +
      '  <h2 style="grid-column: 1 / -1; font-size: 48px; font-weight: 600; color: ' + palette.primary + '; margin-bottom: 20px;">' + esc(data.title || '') + '</h2>\n' +
      '  <div class="slide-data" style="grid-column: 1 / -1;">\n' + metrics + '\n  </div>\n' +
      '</section>';
  },

  split: function (data, palette) {
    var items = (data.items || []).map(function (item) {
      return '    <li>' + esc(item) + '</li>';
    }).join('\n');

    return '<section class="slide" data-layout="split" style="display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: center;">\n' +
      '  <div>\n' +
      '    <h2 style="font-size: 40px; font-weight: 600; color: ' + palette.primary + '; margin-bottom: 30px;">' + esc(data.title || '') + '</h2>\n' +
      '    <ul style="list-style: none; padding: 0;">\n' + items + '\n    </ul>\n' +
      '  </div>\n' +
      '  <div style="background: linear-gradient(135deg, ' + palette.secondary + ', ' + palette.primary + '33); border-radius: 20px; height: 400px;"></div>\n' +
      '</section>';
  },

  timeline: function (data, palette) {
    var steps = (data.steps || []).map(function (step, i) {
      return '  <div style="flex: 1; text-align: center; padding: 0 16px;">\n' +
        '    <div style="width: 40px; height: 40px; border-radius: 50%; background: ' + palette.primary + '; color: #fff; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px; font-weight: 600;">' + (i + 1) + '</div>\n' +
        '    <h3 style="font-size: 18px; color: ' + palette.primary + '; margin-bottom: 8px;">' + esc(step.title || '') + '</h3>\n' +
        '    <p style="font-size: 14px; color: ' + palette.textLight + ';">' + esc(step.desc || '') + '</p>\n' +
        '  </div>';
    }).join('\n');

    return '<section class="slide" data-layout="timeline">\n' +
      '  <h2 style="font-size: 48px; font-weight: 600; color: ' + palette.primary + '; margin-bottom: 50px; text-align: center;">' + esc(data.title || '') + '</h2>\n' +
      '  <div style="display: flex; gap: 20px;">\n' + steps + '\n  </div>\n' +
      '</section>';
  },

  comparison: function (data, palette) {
    var col = function (side) {
      var items = (side.items || []).map(function (item) {
        return '      <li style="margin-bottom: 12px;">' + esc(item) + '</li>';
      }).join('\n');
      return '  <div style="flex: 1; padding: 30px; border-radius: 16px; background: ' + (side.highlight ? palette.primary + '0D' : '#f9fafb') + ';">\n' +
        '    <h3 style="font-size: 24px; color: ' + palette.primary + '; margin-bottom: 20px;">' + esc(side.title || '') + '</h3>\n' +
        '    <ul style="list-style: none; padding: 0;">\n' + items + '\n    </ul>\n' +
        '  </div>';
    };

    return '<section class="slide" data-layout="comparison">\n' +
      '  <h2 style="font-size: 48px; font-weight: 600; color: ' + palette.primary + '; margin-bottom: 40px; text-align: center;">' + esc(data.title || '') + '</h2>\n' +
      '  <div style="display: flex; gap: 30px;">\n' + col(data.left || {}) + '\n' + col(data.right || {}) + '\n  </div>\n' +
      '</section>';
  },

  end: function (data, palette) {
    return '<section class="slide slide-end" data-layout="end">\n' +
      '  <h2>' + esc(data.title || '谢谢') + '</h2>\n' +
      '  <p>' + esc(data.subtitle || '') + '</p>\n' +
      '</section>';
  }
};

function esc(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ─── 生成主题 CSS ───
function generateThemeCSS(palette) {
  return '/* Auto-generated theme */\n' +
    ':root {\n' +
    '  --primary: ' + palette.primary + ';\n' +
    '  --secondary: ' + palette.secondary + ';\n' +
    '  --accent: ' + palette.accent + ';\n' +
    '  --bg-light: ' + palette.bgLight + ';\n' +
    '  --text: ' + palette.text + ';\n' +
    '  --text-light: ' + palette.textLight + ';\n' +
    '}\n\n' +
    'body {\n' +
    '  font-family: "Geist", "Outfit", "Satoshi", -apple-system, BlinkMacSystemFont, sans-serif;\n' +
    '  background: var(--bg-light);\n' +
    '  color: var(--text);\n' +
    '  margin: 0;\n' +
    '  padding: 0;\n' +
    '}\n\n' +
    '.slide {\n' +
    '  width: 1280px;\n' +
    '  height: 720px;\n' +
    '  padding: 80px;\n' +
    '  background: var(--bg-light);\n' +
    '  position: relative;\n' +
    '  overflow: hidden;\n' +
    '  display: none;\n' +
    '  box-sizing: border-box;\n' +
    '  box-shadow: none;\n' +
    '}\n\n' +
    '.slide.active { display: block; }\n\n' +
    '.slide h1 { font-size: 64px; font-weight: 700; color: var(--primary); line-height: 1.1; margin: 0; }\n' +
    '.slide h2 { font-size: 48px; font-weight: 600; color: var(--primary); margin-bottom: 40px; }\n' +
    '.slide h3 { font-size: 28px; font-weight: 600; color: var(--primary); }\n' +
    '.slide p, .slide li { font-size: 20px; line-height: 1.8; }\n' +
    '.slide .subtitle { font-size: 24px; color: var(--text-light); margin-top: 20px; }\n\n' +
    '.slide-cover { display: grid; grid-template-columns: 2fr 1fr; gap: 60px; align-items: center; }\n' +
    '.slide-cover .visual { border-radius: 20px; height: 400px; }\n\n' +
    '.slide-content ul { list-style: none; padding: 0; margin: 0; }\n' +
    '.slide-content li { margin-bottom: 20px; padding-left: 30px; position: relative; }\n' +
    '.slide-content li::before { content: ""; position: absolute; left: 0; top: 12px; width: 8px; height: 8px; background: var(--primary); border-radius: 50%; }\n\n' +
    '.slide-data { display: grid; grid-template-columns: repeat(3, 1fr); gap: 40px; }\n' +
    '.slide-data .metric { border: 2px solid var(--secondary); border-radius: 16px; padding: 40px; text-align: center; }\n' +
    '.slide-data .metric-value { font-size: 56px; font-weight: 700; margin-bottom: 10px; }\n' +
    '.slide-data .metric-label { font-size: 18px; color: var(--text-light); }\n\n' +
    '.slide-end { display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; }\n';
}

// ─── 主生成函数 ───
function generateHTML(options) {
  var title = options.title || '演示文稿';
  var theme = options.theme || 'midnight-executive';
  var slides = options.slides || [];
  var lang = options.lang || 'zh';

  var palette = COLOR_PALETTES[theme] || COLOR_PALETTES['midnight-executive'];

  // 生成每页 HTML
  var slidesHTML = slides.map(function (slide) {
    var layout = LAYOUTS[slide.layout] || LAYOUTS.content;
    return layout(slide.data || slide, palette);
  }).join('\n\n    ');

  // 生成主题 CSS
  var themeCSS = generateThemeCSS(palette);

  // 组装完整 HTML
  var html = '<!DOCTYPE html>\n' +
    '<html lang="' + lang + '">\n' +
    '<head>\n' +
    '  <meta charset="UTF-8">\n' +
    '  <meta name="viewport" content="width=device-width, initial-scale=1.0">\n' +
    '  <title>' + esc(title) + '</title>\n' +
    '  <style>\n' + themeCSS.split('\n').map(function (l) { return '    ' + l; }).join('\n') + '\n  </style>\n' +
    '  <style>\n' +
    '    /* 编辑器样式内联 */\n' +
    '    .controls { position: fixed; bottom: 0; left: 0; right: 0; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-top: 1px solid #e5e7eb; padding: 12px 24px; display: flex; align-items: center; justify-content: center; gap: 16px; z-index: 1000; }\n' +
    '    .control-btn { padding: 8px 20px; border: 1px solid #d1d5db; border-radius: 8px; background: #fff; color: #374151; font-size: 14px; font-weight: 500; cursor: pointer; }\n' +
    '    .control-btn:hover { background: #f3f4f6; }\n' +
    '    .control-btn:active { transform: translateY(1px); }\n' +
    '    .page-info { font-size: 14px; color: #6b7280; min-width: 60px; text-align: center; }\n' +
    '    .edit-btn { background: ' + palette.primary + '; color: #fff; border-color: ' + palette.primary + '; }\n' +
    '    .edit-btn:hover { opacity: 0.9; }\n' +
    '    .edit-btn.active { background: #F96167; border-color: #F96167; }\n' +
    '    .save-btn { background: #4CAF50; color: #fff; border-color: #4CAF50; }\n' +
    '    .save-btn:hover { opacity: 0.9; }\n' +
    '    .export-btn { background: #028090; color: #fff; border-color: #028090; }\n' +
    '    .editor-toolbar { position: fixed; top: 12px; left: 50%; transform: translateX(-50%); background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border: 1px solid #e5e7eb; border-radius: 12px; padding: 10px 20px; display: none; align-items: center; gap: 20px; z-index: 1000; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }\n' +
    '    .toolbar-group { display: flex; align-items: center; gap: 8px; }\n' +
    '    .toolbar-group label { font-size: 12px; color: #6b7280; }\n' +
    '    .toolbar-group select, .toolbar-group input[type="color"] { padding: 4px 8px; border: 1px solid #d1d5db; border-radius: 6px; }\n' +
    '    .toolbar-btn { width: 32px; height: 32px; border: 1px solid #d1d5db; border-radius: 6px; background: #fff; cursor: pointer; font-size: 14px; display: flex; align-items: center; justify-content: center; }\n' +
    '    .toolbar-btn:hover { background: #f3f4f6; }\n' +
    '    body.editing [contenteditable="true"] { outline: 2px dashed rgba(30,39,97,0.3); outline-offset: 4px; border-radius: 4px; cursor: text; }\n' +
    '    body.editing [contenteditable="true"]:focus { outline: 2px solid ' + palette.primary + '; }\n' +
    '    .deck { display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 40px; padding-bottom: 80px; }\n' +
    '    .slide { animation: slideIn 0.3s ease; }\n' +
    '    @keyframes slideIn { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }\n' +
    '  </style>\n' +
    '</head>\n' +
    '<body>\n' +
    '  <div class="deck">\n' +
    '    ' + slidesHTML + '\n' +
    '  </div>\n\n' +
    '  <div class="controls">\n' +
    '    <button id="prev" class="control-btn">← 上一页</button>\n' +
    '    <span id="page-info" class="page-info">1 / ' + slides.length + '</span>\n' +
    '    <button id="next" class="control-btn">下一页 →</button>\n' +
    '    <button id="edit-mode" class="control-btn edit-btn">编辑模式</button>\n' +
    '    <button id="save-html" class="control-btn save-btn">保存编辑</button>\n' +
    '    <button id="export-pptx" class="control-btn export-btn">导出 PPTX</button>\n' +
    '  </div>\n\n' +
    '  <div class="editor-toolbar">\n' +
    '    <div class="toolbar-group"><label>字号:</label><select id="font-size"><option value="h1">H1</option><option value="h2">H2</option><option value="h3">H3</option><option value="p" selected>正文</option></select></div>\n' +
    '    <div class="toolbar-group"><label>颜色:</label><input type="color" id="text-color" value="' + palette.primary + '"></div>\n' +
    '    <div class="toolbar-group"><button id="bold" class="toolbar-btn"><b>B</b></button><button id="italic" class="toolbar-btn"><i>I</i></button><button id="underline" class="toolbar-btn"><u>U</u></button></div>\n' +
    '    <div class="toolbar-group"><button id="align-left" class="toolbar-btn">⬅</button><button id="align-center" class="toolbar-btn">⬆</button><button id="align-right" class="toolbar-btn">➡</button></div>\n' +
    '  </div>\n\n' +
    '  <script>\n' +
    EDITOR_SCRIPT +
    '  </script>\n' +
    '</body>\n' +
    '</html>';

  return html;
}

// ─── 内联编辑器脚本 ───
var EDITOR_SCRIPT = [
  '(function(){',
  '  var currentSlide=0,editMode=false,slides=document.querySelectorAll(".slide"),total=slides.length;',
  '  if(total>0)slides[0].classList.add("active");',
  '  function updateInfo(){var e=document.getElementById("page-info");if(e)e.textContent=(currentSlide+1)+" / "+total;}',
  '  function go(i){if(i<0||i>=total)return;slides[currentSlide].classList.remove("active");currentSlide=i;slides[currentSlide].classList.add("active");updateInfo();}',
  '  var p=document.getElementById("prev"),n=document.getElementById("next");',
  '  if(p)p.onclick=function(){go(currentSlide-1);};',
  '  if(n)n.onclick=function(){go(currentSlide+1);};',
  '  document.addEventListener("keydown",function(e){',
  '    if(editMode&&e.target.getAttribute("contenteditable")==="true")return;',
  '    if(e.key==="ArrowLeft"||e.key==="ArrowUp"){e.preventDefault();go(currentSlide-1);}',
  '    else if(e.key==="ArrowRight"||e.key==="ArrowDown"||e.key===" "){e.preventDefault();go(currentSlide+1);}',
  '    else if(e.key==="Escape"&&editMode)toggle();',
  '  });',
  '  function toggle(){',
  '    editMode=!editMode;',
  '    var btn=document.getElementById("edit-mode"),tb=document.querySelector(".editor-toolbar");',
  '    if(editMode){',
  '      document.body.classList.add("editing");',
  '      if(btn){btn.classList.add("active");btn.textContent="预览模式";}',
  '      if(tb)tb.style.display="flex";',
  '      slides.forEach(function(s){s.querySelectorAll("h1,h2,h3,p,li,.metric-value,.metric-label,.subtitle").forEach(function(el){el.setAttribute("contenteditable","true");});});',
  '    }else{',
  '      document.body.classList.remove("editing");',
  '      if(btn){btn.classList.remove("active");btn.textContent="编辑模式";}',
  '      if(tb)tb.style.display="none";',
  '      slides.forEach(function(s){s.querySelectorAll("[contenteditable]").forEach(function(el){el.removeAttribute("contenteditable");});});',
  '    }',
  '  }',
  '  var eb=document.getElementById("edit-mode");if(eb)eb.onclick=toggle;',
  '  var fs=document.getElementById("font-size");',
  '  if(fs)fs.onchange=function(){var s=window.getSelection();if(!s.rangeCount)return;var el=s.anchorNode;while(el&&el.nodeType!==1)el=el.parentNode;if(!el||el.getAttribute("contenteditable")!=="true")return;var m={h1:"48px",h2:"36px",h3:"28px",p:"20px"};el.style.fontSize=m[this.value]||"20px";};',
  '  var tc=document.getElementById("text-color");',
  '  if(tc)tc.oninput=function(){var s=window.getSelection();if(!s.rangeCount)return;var el=s.anchorNode;while(el&&el.nodeType!==1)el=el.parentNode;if(el&&el.getAttribute("contenteditable")==="true")el.style.color=this.value;};',
  '  ["bold","italic","underline"].forEach(function(c){var b=document.getElementById(c);if(b)b.onclick=function(){document.execCommand(c);};});',
  '  ["align-left","align-center","align-right"].forEach(function(c,i){var b=document.getElementById(c);if(b)b.onclick=function(){document.execCommand(["justifyLeft","justifyCenter","justifyRight"][i]);};});',
  '  var sh=document.getElementById("save-html");',
  '  if(sh)sh.onclick=function(){',
  '    var cl=document.documentElement.cloneNode(true);',
  '    var c=cl.querySelector(".controls");if(c)c.remove();',
  '    var t=cl.querySelector(".editor-toolbar");if(t)t.remove();',
  '    cl.querySelectorAll("[contenteditable]").forEach(function(e){e.removeAttribute("contenteditable");});',
  '    var bd=cl.querySelector("body");if(bd)bd.classList.remove("editing");',
  '    var html=cl.outerHTML;',
  '    sh.textContent="保存中...";sh.disabled=true;',
  '    fetch("/api/save-html",{method:"POST",headers:{"Content-Type":"text/html"},body:html}).then(function(r){return r.json();}).then(function(d){',
  '      sh.textContent="保存编辑";sh.disabled=false;',
  '      if(d.success){alert("已保存！可以导出 PPTX 了。");}else{alert("保存失败："+d.message);}',
  '    }).catch(function(e){sh.textContent="保存编辑";sh.disabled=false;alert("保存失败："+e);});',
  '  };',
  '  var xp=document.getElementById("export-pptx");',
  '  if(xp)xp.onclick=function(){',
  '    var ov=document.createElement("div");ov.style.cssText="position:fixed;inset:0;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:2000;";',
  '    ov.innerHTML=\'<div style="background:#fff;border-radius:16px;padding:40px;text-align:center;"><h3 style="margin:0 0 12px;color:#1E2761;">正在导出 PPTX...</h3></div>\';',
  '    document.body.appendChild(ov);',
  '    fetch("/api/export-pptx",{method:"POST"}).then(function(r){return r.json();}).then(function(d){',
  '      ov.remove();',
  '      if(d.success){alert("PPTX 已导出："+d.fileName);window.open("/download/"+d.fileName,"_blank");}else{alert("导出失败："+d.message);}',
  '    }).catch(function(e){ov.remove();alert("导出失败："+e);});',
  '  };',
  '})();'
].join('\n');

// ─── CLI 入口 ───
if (require.main === module) {
  var args = process.argv.slice(2);
  var inputFile = null;
  var outputFile = null;
  var theme = 'midnight-executive';

  for (var i = 0; i < args.length; i++) {
    if (args[i] === '--input' || args[i] === '-i') inputFile = args[++i];
    else if (args[i] === '--output' || args[i] === '-o') outputFile = args[++i];
    else if (args[i] === '--theme' || args[i] === '-t') theme = args[++i];
  }

  if (!inputFile) {
    console.error('Usage: node generate_html.js --input <content.json> [--output <output.html>] [--theme <theme>]');
    process.exit(1);
  }

  var content = JSON.parse(fs.readFileSync(inputFile, 'utf-8'));
  content.theme = content.theme || theme;

  var html = generateHTML(content);

  if (!outputFile) {
    outputFile = path.join(path.dirname(inputFile), 'presentation.html');
  }

  fs.writeFileSync(outputFile, html, 'utf-8');
  console.log('HTML 演示文稿已生成: ' + outputFile);
}

module.exports = { generateHTML: generateHTML, COLOR_PALETTES: COLOR_PALETTES, LAYOUTS: LAYOUTS };
