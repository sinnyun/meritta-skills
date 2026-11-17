#!/usr/bin/env node

/**
 * PPT Expert - 本地预览服务器
 * 提供 HTML 预览 + 导出 API
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

const SKILL_ROOT = path.resolve(__dirname, '..');

function startServer(htmlFile, port) {
  port = port || 0;

  // 存储 SSE 客户端
  const sseClients = new Set();

  // 监听 HTML 文件变化
  let lastMtime = fs.statSync(htmlFile).mtime;
  fs.watch(htmlFile, (eventType) => {
    if (eventType === 'change') {
      const newMtime = fs.statSync(htmlFile).mtime;
      if (newMtime > lastMtime) {
        lastMtime = newMtime;
        console.log('检测到文件变化，通知浏览器刷新...');
        // 通知所有 SSE 客户端
        sseClients.forEach(client => {
          client.write('data: reload\n\n');
        });
      }
    }
  });

  var server = http.createServer(function (req, res) {
    var url = req.url.split('?')[0];

    // SSE 端点 - 用于实时推送刷新通知
    if (url === '/events' && req.method === 'GET') {
      res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*'
      });
      res.write('data: connected\n\n');
      sseClients.add(res);
      req.on('close', () => sseClients.delete(res));
      return;
    }

    // 保存编辑 API - 接收浏览器编辑后的 HTML，写回 HTML 文件
    if (url === '/api/save-html' && req.method === 'POST') {
      handleSaveHtml(htmlFile, req, res);
      return;
    }

    // 导出 API
    if (url === '/api/export-pptx' && req.method === 'POST') {
      handleExport(htmlFile, res);
      return;
    }

    // 下载 API - 提供生成的 PPTX 文件下载
    if (url.indexOf('/download/') === 0 && req.method === 'GET') {
      var fileName = url.replace('/download/', '');
      var pptxFile = path.join(path.dirname(htmlFile), fileName);
      if (fs.existsSync(pptxFile)) {
        fs.readFile(pptxFile, function (err, data) {
          if (err) {
            res.writeHead(500);
            res.end('读取文件失败');
            return;
          }
          res.writeHead(200, {
            'Content-Type': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'Content-Disposition': 'attachment; filename="' + encodeURIComponent(fileName) + '"'
          });
          res.end(data);
        });
        return;
      }
      res.writeHead(404);
      res.end('文件不存在');
      return;
    }

    // 主页 - 注入自动刷新脚本
    if (url === '/' || url === '/index.html') {
      const htmlContent = fs.readFileSync(htmlFile, 'utf-8');
      // 在 </body> 前注入 SSE 监听脚本
      const reloadScript = `
<script>
(function() {
  const evtSource = new EventSource('/events');
  evtSource.onmessage = function(event) {
    if (event.data === 'reload') {
      console.log('文件已更新，正在刷新...');
      window.location.reload();
    }
  };
  evtSource.onerror = function() {
    console.log('连接断开，5秒后重连...');
    setTimeout(() => window.location.reload(), 5000);
  };
})();
</script>
`;
      const injectedHtml = htmlContent.replace('</body>', reloadScript + '</body>');
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(injectedHtml);
      return;
    }

    // 静态文件 (editor.js, editor.css)
    var filePath = path.join(SKILL_ROOT, 'public', url);
    if (fs.existsSync(filePath)) {
      var ext = path.extname(filePath);
      var mime = { '.js': 'application/javascript', '.css': 'text/css', '.png': 'image/png' }[ext] || 'text/plain';
      serveFile(filePath, res, mime);
      return;
    }

    res.writeHead(404);
    res.end('Not found');
  });

  server.listen(port, '127.0.0.1', function () {
    var addr = server.address();
    console.log('预览服务已启动: http://127.0.0.1:' + addr.port);
    console.log('✓ 支持热更新：编辑 HTML 文件后浏览器自动刷新');
    console.log('按 Ctrl+C 停止');
  });

  return server;
}

function serveFile(filePath, res, contentType) {
  fs.readFile(filePath, function (err, data) {
    if (err) {
      res.writeHead(404);
      res.end('Not found');
      return;
    }
    res.writeHead(200, { 'Content-Type': contentType + '; charset=utf-8' });
    res.end(data);
  });
}

function handleSaveHtml(htmlFile, req, res) {
  // 接收浏览器编辑后的 HTML 内容，写回 HTML 文件
  var chunks = [];
  req.on('data', function (chunk) { chunks.push(chunk); });
  req.on('end', function () {
    var htmlContent = Buffer.concat(chunks).toString('utf-8');
    if (!htmlContent) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: false, message: '未收到 HTML 内容' }));
      return;
    }
    fs.writeFile(htmlFile, htmlContent, 'utf-8', function (err) {
      if (err) {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, message: '写入失败: ' + err.message }));
        return;
      }
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, message: '已保存到 ' + htmlFile }));
    });
  });
}

function handleExport(htmlFile, res) {
  // 从微调后的 HTML 文件直接生成 PPTX（样式感知，不依赖 puppeteer）
  // 解析 HTML 中的 data-layout、内联 style、CSS :root 变量
  var outputFile = htmlFile.replace(/\.html$/, '.pptx');
  var script = path.join(SKILL_ROOT, 'scripts', 'html_to_pptx_direct.js');
  var scriptPy = path.join(SKILL_ROOT, 'scripts', 'html_to_pptx_direct.py');

  // 优先使用 Node 版本（cheerio + pptxgenjs），降级到 Python 版本
  var usePython = !fs.existsSync(script) && fs.existsSync(scriptPy);
  var cmd, usedScript;

  if (usePython) {
    cmd = 'python "' + scriptPy + '" --input "' + htmlFile + '" --output "' + outputFile + '"';
    usedScript = scriptPy;
  } else {
    cmd = 'node "' + script + '" --input "' + htmlFile + '" --output "' + outputFile + '"';
    usedScript = script;
  }

  if (!fs.existsSync(usedScript)) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      success: false,
      message: '导出脚本不存在: ' + usedScript
    }));
    return;
  }

  if (!fs.existsSync(htmlFile)) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      success: false,
      message: 'HTML 文件不存在: ' + htmlFile
    }));
    return;
  }

  var exec = require('child_process').exec;
  exec(cmd, { timeout: 60000 }, function (error, stdout, stderr) {
    if (error) {
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        success: false,
        message: '导出失败: ' + (stderr || error.message)
      }));
      return;
    }

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      success: true,
      fileName: path.basename(outputFile),
      downloadUrl: '/download/' + path.basename(outputFile)
    }));
  });
}

// CLI
if (require.main === module) {
  var args = process.argv.slice(2);
  var htmlFile = null;
  var port = 3000;

  for (var i = 0; i < args.length; i++) {
    if (args[i] === '--html' || args[i] === '-f') htmlFile = args[++i];
    else if (args[i] === '--port' || args[i] === '-p') port = parseInt(args[++i]);
  }

  if (!htmlFile) {
    console.error('Usage: node serve_preview.js --html <presentation.html> [--port 3000]');
    process.exit(1);
  }

  startServer(path.resolve(htmlFile), port);
}

module.exports = { startServer: startServer };
