# 插件应用目录结构参考

## 基本结构

插件应用至少要有一个 `plugin.json` 作为入口，并配置 `logo` 字段以及 `main` 或者 `preload` 字段。

```
/{plugin}
├── plugin.json
├── preload.js
├── index.html
├── index.js
├── index.css
└── logo.png
```

## CLI 模板项目结构

使用 `@ztools-center/plugin-cli` 创建的项目结构：

```
my-first-plugin/
├── plugin.json          # 插件配置文件
├── package.json         # 项目依赖配置
├── tsconfig.json        # TypeScript 配置
├── vite.config.js       # Vite 构建配置（如果使用 Vite 模板）
├── src/                 # 源代码目录
│   ├── preload.ts       # Preload 脚本
│   └── ...              # 其他源文件
├── public/              # 静态资源
│   └── logo.png         # 插件 Logo
└── dist/                # 构建输出目录（构建后生成）
```

## 模板类型

ZTools 插件 CLI 工具提供以下模板：

| 模板 | 说明 |
|------|------|
| Vue + TypeScript + Vite | 使用 Vue 3 开发插件 UI |
| React + TypeScript + Vite | 使用 React 开发插件 UI |
| Preload Only (TypeScript) | 仅使用 Preload API，无 UI 界面 |

## 源码编译

ZTools 仅识别 `html + css + javascript`。

开发过程中可能使用 vite、webpack 等工具，也可能引入 vue、react 等框架。打包前应先将框架代码编译成普通的 html、css、js 文件。

通常将源码编译输出到 `dist` 文件夹，然后将 `dist` 文件夹打包成插件应用。切勿将整个项目的根目录打包成插件应用。

## 第三方依赖

### 前端依赖

在项目根目录下安装即可，对前端项目进行正常的编译，输出到 `dist` 文件夹。

### Node.js 第三方依赖

应当保证模块存在于 `preload.js` 同级目录，并且不要对它们进行编译操作。保证提交插件应用时的目录结构不变，并且源码清晰可读。

## 开发流程

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建
npm run build
```

构建产物会输出到 `dist/` 目录，这个目录就是你的插件应用，可以打包提交。