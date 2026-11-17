/**
 * PPT Expert - 浏览器端编辑脚本
 * 支持内联编辑、导航、导出
 */
(function () {
  'use strict';

  let currentSlide = 0;
  let editMode = false;
  let totalSlides = 0;

  function init() {
    const slides = document.querySelectorAll('.slide');
    totalSlides = slides.length;

    // 显示第一页
    if (totalSlides > 0) {
      slides[0].classList.add('active');
    }

    updatePageInfo();
    bindNavigation();
    bindEditMode();
    bindExport();
    bindKeyboard();
  }

  function updatePageInfo() {
    const info = document.getElementById('page-info');
    if (info) {
      info.textContent = (currentSlide + 1) + ' / ' + totalSlides;
    }
  }

  function goToSlide(index) {
    if (index < 0 || index >= totalSlides) return;

    const slides = document.querySelectorAll('.slide');
    slides[currentSlide].classList.remove('active');
    currentSlide = index;
    slides[currentSlide].classList.add('active');
    updatePageInfo();
  }

  function bindNavigation() {
    const prev = document.getElementById('prev');
    const next = document.getElementById('next');

    if (prev) {
      prev.addEventListener('click', function () {
        goToSlide(currentSlide - 1);
      });
    }

    if (next) {
      next.addEventListener('click', function () {
        goToSlide(currentSlide + 1);
      });
    }
  }

  function bindKeyboard() {
    document.addEventListener('keydown', function (e) {
      if (editMode && e.target.getAttribute('contenteditable') === 'true') return;

      if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        e.preventDefault();
        goToSlide(currentSlide - 1);
      } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
        e.preventDefault();
        goToSlide(currentSlide + 1);
      } else if (e.key === 'Escape' && editMode) {
        toggleEditMode();
      }
    });
  }

  function bindEditMode() {
    const editBtn = document.getElementById('edit-mode');
    const toolbar = document.querySelector('.editor-toolbar');

    if (editBtn) {
      editBtn.addEventListener('click', toggleEditMode);
    }

    // 工具栏事件
    bindToolbar();
  }

  function toggleEditMode() {
    editMode = !editMode;
    const editBtn = document.getElementById('edit-mode');
    const toolbar = document.querySelector('.editor-toolbar');
    const slides = document.querySelectorAll('.slide');

    if (editMode) {
      document.body.classList.add('editing');
      if (editBtn) {
        editBtn.classList.add('active');
        editBtn.textContent = '预览模式';
      }
      if (toolbar) toolbar.style.display = 'flex';

      // 使所有文字区域可编辑
      slides.forEach(function (slide) {
        var editables = slide.querySelectorAll('h1, h2, h3, p, li, .metric-value, .metric-label, .subtitle');
        editables.forEach(function (el) {
          el.setAttribute('contenteditable', 'true');
        });
      });
    } else {
      document.body.classList.remove('editing');
      if (editBtn) {
        editBtn.classList.remove('active');
        editBtn.textContent = '编辑模式';
      }
      if (toolbar) toolbar.style.display = 'none';

      // 关闭编辑
      slides.forEach(function (slide) {
        var editables = slide.querySelectorAll('[contenteditable="true"]');
        editables.forEach(function (el) {
          el.removeAttribute('contenteditable');
        });
      });
    }
  }

  function bindToolbar() {
    var fontSize = document.getElementById('font-size');
    var textColor = document.getElementById('text-color');
    var bold = document.getElementById('bold');
    var italic = document.getElementById('italic');
    var underline = document.getElementById('underline');
    var alignLeft = document.getElementById('align-left');
    var alignCenter = document.getElementById('align-center');
    var alignRight = document.getElementById('align-right');

    if (fontSize) {
      fontSize.addEventListener('change', function () {
        var sel = window.getSelection();
        if (!sel.rangeCount) return;
        var el = findEditableParent(sel.anchorNode);
        if (!el) return;

        var sizes = { h1: '48px', h2: '36px', h3: '28px', p: '20px' };
        el.style.fontSize = sizes[this.value] || '20px';
      });
    }

    if (textColor) {
      textColor.addEventListener('input', function () {
        var sel = window.getSelection();
        if (!sel.rangeCount) return;
        var el = findEditableParent(sel.anchorNode);
        if (el) el.style.color = this.value;
      });
    }

    if (bold) {
      bold.addEventListener('click', function () { document.execCommand('bold'); });
    }
    if (italic) {
      italic.addEventListener('click', function () { document.execCommand('italic'); });
    }
    if (underline) {
      underline.addEventListener('click', function () { document.execCommand('underline'); });
    }

    if (alignLeft) {
      alignLeft.addEventListener('click', function () { document.execCommand('justifyLeft'); });
    }
    if (alignCenter) {
      alignCenter.addEventListener('click', function () { document.execCommand('justifyCenter'); });
    }
    if (alignRight) {
      alignRight.addEventListener('click', function () { document.execCommand('justifyRight'); });
    }
  }

  function findEditableParent(node) {
    while (node && node !== document.body) {
      if (node.nodeType === 1 && node.getAttribute('contenteditable') === 'true') {
        return node;
      }
      node = node.parentNode;
    }
    return null;
  }

  function bindExport() {
    var exportBtn = document.getElementById('export-pptx');
    if (exportBtn) {
      exportBtn.addEventListener('click', exportPptx);
    }
  }

  function exportPptx() {
    // 显示导出进度
    var overlay = document.createElement('div');
    overlay.className = 'export-overlay';
    overlay.innerHTML =
      '<div class="export-dialog">' +
      '<h3>正在导出 PPTX</h3>' +
      '<p>正在将各页转换为图片...</p>' +
      '<div class="progress-bar"><div class="progress-bar-fill" id="progress-fill"></div></div>' +
      '</div>';
    document.body.appendChild(overlay);

    // 调用后端导出接口
    fetch('/api/export-pptx', { method: 'POST' })
      .then(function (res) {
        if (!res.ok) throw new Error('Export failed');
        return res.json();
      })
      .then(function (data) {
        overlay.remove();
        if (data.downloadUrl) {
          window.location.href = data.downloadUrl;
        } else {
          alert('导出成功！文件: ' + (data.fileName || 'presentation.pptx'));
        }
      })
      .catch(function (err) {
        overlay.remove();
        alert('导出失败: ' + err.message);
      });
  }

  // DOM Ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
