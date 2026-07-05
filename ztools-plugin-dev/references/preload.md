# preload.js 配置参考

## 为什么需要 preload

在传统的 web 开发中，JavaScript 被做了很强的沙箱限制（不能访问本地文件、跨域网络资源、本地存储等）。

ZTools 基于 Electron 构建，通过 preload 机制，在渲染线程中释放了沙箱限制，使得用户可以通过调用 Node.js 的 API 来访问本地文件、跨域网络资源、本地存储等。

## preload 的定义

- preload 是完全独立于前端项目的一个特殊文件
- 应当与 `plugin.json` 位于同一目录或其子目录下
- 遵循 CommonJS 规范，使用 `require` 引入 Node.js 模块

## 前端使用 preload

只需给 `window` 对象自定义一个属性，前端就可直接访问该属性。

```javascript
// preload.js
const fs = require("fs");
window.customApis = {
  readFile: (path) => {
    return fs.readFileSync(path, "utf8");
  },
};
```

```html
<!-- 前端 HTML/JS 中直接使用 -->
<script>
  const content = window.customApis.readFile("/path/to/file.txt");
</script>
```

## preload js 规范

由于 preload js 文件可使用本地原生能力，ZTools 规定：

1. preload js 文件代码**不能进行打包/压缩/混淆**等操作，要保证每一行代码清晰可读
2. 引入的第三方模块也必须清晰可读，在提交时将源码一同提交，同样不允许压缩/混淆

## 引入 Node.js 原生模块

```javascript
// preload.js
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const { execSync } = require("node:child_process");

window.services = {
  readFile: (filename) => {
    return fs.readFileSync(filename, { encoding: "utf-8" });
  },
  getFolder: (filepath) => {
    return path.dirname(filepath);
  },
  getOSInfo: () => {
    return { arch: os.arch(), cpus: os.cpus(), release: os.release() };
  },
  execCommand: (command) => {
    execSync(command);
  },
};
```

## 引入自己编写的模块

```javascript
// preload.js
const writeText = require("./libs/writeText.js");
window.services = { writeText };
```

```javascript
// libs/writeText.js
const fs = require("fs");
const path = require("path");

module.exports = function writeText(text, filePath) {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(filePath, text);
    return true;
  }
  return false;
};
```

## 引入第三方模块

### 通过 npm 安装

1. 在 `preload.js` 同级目录下创建 `package.json`，设置 `type` 为 `commonjs`：

```json
{
  "type": "commonjs",
  "dependencies": {}
}
```

2. 在 `preload.js` 同级目录下执行 `npm install` 安装第三方模块

```bash
npm install colord
```

3. 在 preload.js 中引入使用：

```javascript
const { getFormat, colord } = require("colord");

window.services = {
  colord: {
    darken(text) {
      const fmt = getFormat(text);
      if (!fmt) {
        return [null, "请输入一个有效的颜色值，比如 #000 或 rgb(0,0,0)"];
      } else {
        const darkColor = colord(text).darken(0.1);
        return [darkColor, null];
      }
    },
  },
};
```

### 通过源码引入

```bash
git clone https://github.com/nodemailer/nodemailer.git
```

```javascript
const nodemailer = require("./nodemailer");

const _setImmediate = setImmediate;
process.once("loaded", function () {
  global.setImmediate = _setImmediate;
});

const sendMail = () => {
  let transporter = require("./nodemailer").createTransport({
    host: "smtp.qq.com",
    port: 465,
    secure: true,
    auth: { user: "aaa@qq.com", pass: "xxx" },
  });
  // ...
};

window.services = { sendMail: () => sendMail() };
```

## 引入 Electron 渲染进程 API

```javascript
const { clipboard, nativeImage } = require("electron");

window.services = {
  copyImage: (imageFilePath) => {
    clipboard.writeImage(nativeImage.createFromPath(imageFilePath));
  },
};
```