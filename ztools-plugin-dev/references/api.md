# ZTools 插件 API 完整参考

ZTools 为插件提供了一套丰富的 API，通过全局对象 `window.ztools` 暴露。

## 基础 API

### ztools.getAppName()
获取应用名称。
- 返回: `string` - 固定返回 `'ZTools'`

### ztools.getPathForFile(file)
获取拖放文件的真实路径（基于 Electron `webUtils.getPathForFile`）。
- `file`: `File` - 拖放事件中的 File 对象
- 返回: `string` - 文件的本地路径

### ztools.isMacOs() / ztools.isMacOS()
检测当前是否为 macOS 系统。
- 返回: `boolean`

### ztools.isWindows()
检测当前是否为 Windows 系统。
- 返回: `boolean`

### ztools.isLinux()
检测当前是否为 Linux 系统。
- 返回: `boolean`

### ztools.getNativeId()
获取设备唯一标识符（32位字符串）。
- 返回: `string`

### ztools.getAppVersion()
获取应用版本号。
- 返回: `string`

### ztools.getWindowType()
获取当前窗口类型。
- 返回: `string`

### ztools.isDarkColors()
检测当前是否为深色主题。
- 返回: `boolean`

### ztools.isDev()
检查当前插件是否处于开发模式。
- 返回: `boolean`

### ztools.getWebContentsId()
获取当前 WebContents ID。
- 返回: `number`

### ztools.setExpendHeight(height)
设置插件视图的高度。
- `height`: `number` - 期望的高度（像素）

### ztools.showNotification(body)
显示系统通知。
- `body`: `string` - 通知内容

### ztools.sendInputEvent(event)
发送模拟输入事件。
- `event`: `MouseInputEvent | MouseWheelInputEvent | KeyboardInputEvent`

#### KeyboardInputEvent (键盘事件)
- `type`: `'keyDown' | 'keyUp' | 'char'`
- `keyCode`: `string` - 键盘代码
- `modifiers`: `string[]` - 修饰键数组 (例如 `['shift', 'control']`)

#### MouseInputEvent (鼠标事件)
- `type`: `'mouseDown' | 'mouseUp' | 'mouseEnter' | 'mouseLeave' | 'contextMenu' | 'mouseMove'`
- `x`: `number` - X 坐标
- `y`: `number` - Y 坐标
- `button`: `'left' | 'middle' | 'right'`
- `clickCount`: `number` - 点击次数

#### MouseWheelInputEvent (滚轮事件)
- `type`: `'mouseWheel'`
- `deltaX`, `deltaY`: `number`
- `wheelTicksX`, `wheelTicksY`: `number`
- `accelerationRatioX`, `accelerationRatioY`: `number`
- `hasPreciseScrollingDeltas`: `boolean`
- `canScroll`: `boolean`

### ztools.simulateKeyboardTap(key, ...modifiers)
模拟键盘按键。
- `key`: `string` - 要按下的键
- `modifiers`: `string[]` - 修饰键数组（可选）
- 返回: `boolean` - 是否成功

### ztools.showMainWindow()
显示主窗口。
- 返回: `Promise<boolean>`

### ztools.hideMainWindow(isRestorePreWindow)
隐藏主窗口，包括此时正在主窗口运行的插件应用。
- `isRestorePreWindow`: `boolean` - (可选) 是否焦点回归到前面的活动窗口，默认 `true`
- 返回: `Promise<boolean>`

### ztools.outPlugin(isKill)
退出插件应用，默认将插件应用隐藏后台。
- `isKill`: `boolean` - (可选) 为 `true` 时，将结束运行插件应用 (杀死进程)
- 返回: `Promise<boolean>`

## 事件 API

### ztools.onPluginEnter(callback)
监听插件进入事件。当用户打开插件时触发。
- `callback`: `(param: LaunchParam) => void`

#### LaunchParam 结构
- `payload`: `any` - 传递的数据（例如搜索框内容）
- `type`: `'text' | 'regex' | 'over'` - 命令类型
- `code`: `string` - 插件 Feature Code (如果是由 Feature 触发)

### ztools.onPluginOut(callback)
监听插件退出事件。
- `callback`: `(isKill: boolean) => void`

### ztools.onPluginDetach(callback)
监听插件被分离为独立窗口的事件。
- `callback`: `() => void`

### ztools.onMainPush(callback, selectCallback)
注册主搜索推送功能。插件可以在主搜索框中提供搜索结果。
- `callback`: `(queryData: any) => object[]` - 查询回调函数
- `selectCallback`: `(selectData: any) => boolean` - (可选) 用户选择搜索结果时的回调函数。返回 `true` 表示需要进入插件

### ztools.onPluginReady(callback)
兼容旧 API，功能与 `onPluginEnter` 相同。
- `callback`: `(param: LaunchParam) => void`

## 搜索框 API

### ztools.setSubInput(onChange, placeholder, isFocus)
设置主窗口搜索框的行为（当插件处于活动状态时）。
- `onChange`: `(text: string) => void` - 当用户在搜索框输入时触发的回调函数
- `placeholder`: `string` - 搜索框的占位符文本
- `isFocus`: `boolean` - (可选) 是否自动聚焦搜索框，默认 `true`

### ztools.setSubInputValue(text)
设置子输入框的值。
- `text`: `string` - 要设置的值

### ztools.subInputFocus()
聚焦子输入框。
- 返回: `boolean`

### ztools.subInputBlur()
子输入框失去焦点，插件应用获得焦点。
- 返回: `boolean`

### ztools.subInputSelect()
子输入框获得焦点并选中全部内容。
- 返回: `boolean`

### ztools.removeSubInput()
移除（隐藏）子输入框。
- 返回: `Promise<boolean>`

## 数据库 API

插件拥有独立的数据库存储空间（Bucket），以插件名称隔离。

### ztools.db.put(doc)
保存数据。
- `doc`: `object` - 文档对象（必须包含 `_id` 字段）
- 返回: `object` - 保存后的文档对象（包含 `_id` 和 `_rev`）

### ztools.db.get(id)
获取数据。
- `id`: `string` - 文档 ID
- 返回: `object | null`

### ztools.db.remove(docOrId)
删除数据。
- `docOrId`: `object | string` - 要删除的文档对象或文档 ID
- 返回: `object`

### ztools.db.bulkDocs(docs)
批量操作文档。
- `docs`: `object[]` - 文档数组
- 返回: `object[]`

### ztools.db.allDocs(key)
获取所有文档或按 key 前缀查询。
- `key`: `string` - (可选) 文档 ID 前缀，用于过滤
- 返回: `object[]`

### ztools.db.postAttachment(id, attachment, type)
为文档添加附件。
- `id`: `string` - 文档 ID
- `attachment`: `string | Buffer` - 附件内容（base64 字符串或 Buffer）
- `type`: `string` - 附件 MIME 类型
- 返回: `object`

### ztools.db.getAttachment(id)
获取文档附件。
- `id`: `string` - 文档 ID
- 返回: `Buffer`

### ztools.db.getAttachmentType(id)
获取文档附件的 MIME 类型。
- `id`: `string` - 文档 ID
- 返回: `string`

### Promise API
数据库 API 还提供了 Promise 版本，位于 `window.ztools.db.promises` 下，所有方法签名与同步版本相同，但返回 Promise。

## dbStorage API

类似 `localStorage` 的简化接口，用于简单的键值对存储。

### ztools.dbStorage.setItem(key, value)
保存数据。
- `key`: `string` - 键名
- `value`: `any` - 要保存的数据（会自动序列化为 JSON）

### ztools.dbStorage.getItem(key)
获取数据。
- `key`: `string` - 键名
- 返回: `any`

### ztools.dbStorage.removeItem(key)
删除数据。
- `key`: `string` - 键名

## 动态 Feature API

### ztools.getFeatures(codes)
获取动态添加的 features。
- `codes`: `string[]` - (可选) 指定要获取的 feature codes，不传则返回所有
- 返回: `object[]`

### ztools.setFeature(feature)
设置动态 feature（如果已存在则更新）。
- `feature`: `object` - Feature 对象
- 返回: `boolean`

### ztools.removeFeature(code)
删除指定的动态 feature。
- `code`: `string` - Feature code
- 返回: `boolean`

## 剪贴板 API

### ztools.clipboard.getHistory(page, pageSize, filter)
获取剪贴板历史记录。
- `page`: `number` - 页码，从 1 开始
- `pageSize`: `number` - 每页数量
- `filter`: `string` - (可选) 过滤条件
- 返回: `Promise<object>`

### ztools.clipboard.search(keyword)
搜索剪贴板历史。
- `keyword`: `string` - 搜索关键词
- 返回: `Promise<object[]>`

### ztools.clipboard.delete(id)
删除剪贴板记录。
- `id`: `string` - 记录 ID
- 返回: `Promise<boolean>`

### ztools.clipboard.clear(type)
清空剪贴板历史。
- `type`: `string` - (可选) 类型过滤
- 返回: `Promise<boolean>`

### ztools.clipboard.getStatus()
获取剪贴板状态。
- 返回: `Promise<object>`

### ztools.clipboard.write(id, shouldPaste)
将指定记录写入剪贴板。
- `id`: `string` - 记录 ID
- `shouldPaste`: `boolean` - (可选) 是否同时模拟粘贴操作，默认 `true`
- 返回: `Promise<boolean>`

### ztools.clipboard.writeContent(data, shouldPaste)
写入内容到剪贴板。
- `data`: `object` - 数据对象，包含 `type` (`'text' | 'image'`) 和 `content`
- `shouldPaste`: `boolean` - (可选) 是否同时模拟粘贴操作，默认 `true`
- 返回: `Promise<boolean>`

### ztools.clipboard.updateConfig(config)
更新剪贴板配置。
- `config`: `object` - 配置对象
- 返回: `Promise<boolean>`

### ztools.clipboard.onChange(callback)
监听剪贴板变化事件。
- `callback`: `(item: object) => void`

### ztools.copyText(text)
复制文本到剪贴板。
- `text`: `string` - 要复制的文本
- 返回: `boolean`

### ztools.copyImage(image)
复制图片到剪贴板。
- `image`: `string` - 图片 base64 Data URL 或文件路径
- 返回: `boolean`

### ztools.copyFile(filePath)
复制文件到剪贴板。
- `filePath`: `string` - 文件路径
- 返回: `boolean`

## 文件操作 API

### ztools.getPath(name)
获取系统路径。
- `name`: `string` - 路径名称（如 `'home'`, `'desktop'`, `'documents'` 等）
- 返回: `string`

### ztools.showSaveDialog(options)
弹出文件保存对话框。
- `options`: `SaveDialogOptions` - 与 Electron `showSaveDialogSync` 保持一致
- 返回: `string | undefined`

### ztools.showOpenDialog(options)
弹出文件打开对话框。
- `options`: `OpenDialogOptions` - 与 Electron `showOpenDialogSync` 保持一致
- 返回: `string[] | undefined`

### ztools.screenCapture(callback)
屏幕截图，会进入截图模式。
- `callback`: `(image: string) => void` - 截图完的回调函数，`image` 为 base64 Data Url

## 窗口 API

### ztools.createBrowserWindow(url, options, callback)
创建独立窗口。
- `url`: `string` - 窗口加载的 URL
- `options`: `object` - 与 Electron `BrowserWindow` 构造函数选项保持一致
- `callback`: `() => void` - (可选) 窗口加载完成后的回调函数
- 返回: `Proxy<BrowserWindow> | null`

### ztools.sendToParent(channel, ...args)
发送消息到父窗口。
- `channel`: `string` - 通道名称
- `args`: `any[]` - 要传递的参数

## 显示器 API

### ztools.getPrimaryDisplay()
获取主显示器信息。
- 返回: `object`

### ztools.getAllDisplays()
获取所有显示器。
- 返回: `object[]`

### ztools.getCursorScreenPoint()
获取鼠标光标的屏幕坐标。
- 返回: `{ x: number, y: number }`

### ztools.getDisplayNearestPoint(point)
获取最接近指定点的显示器。
- `point`: `{ x: number, y: number }`
- 返回: `object`

### ztools.desktopCaptureSources(options)
获取桌面捕获源。
- `options`: `object`
- 返回: `Promise<object[]>`

### ztools.dipToScreenPoint(point)
DIP 坐标转屏幕物理坐标。
- 返回: `{ x: number, y: number }`

### ztools.screenToDipPoint(point)
屏幕物理坐标转 DIP 坐标。
- 返回: `{ x: number, y: number }`

### ztools.dipToScreenRect(rect)
DIP 区域转屏幕物理区域。
- `rect`: `{ x: number, y: number, width: number, height: number }`
- 返回: 同结构

## Shell API

### ztools.shellOpenExternal(url)
使用系统默认程序打开 URL。
- `url`: `string`
- 返回: `boolean`

### ztools.shellOpenPath(fullPath)
使用系统默认方式打开文件或文件夹。
- `fullPath`: `string`
- 返回: `boolean`

### ztools.shellShowItemInFolder(fullPath)
在文件管理器中显示文件。
- `fullPath`: `string`
- 返回: `boolean`

## 其他 API

### ztools.redirect(label, payload)
插件跳转。
- `label`: `string` - 目标插件的 label
- `payload`: `any` - 传递的数据
- 返回: `boolean`

### ztools.http.setHeaders(headers)
设置 HTTP 请求头。
- `headers`: `object`
- 返回: `boolean`

### ztools.http.getHeaders()
获取当前请求头配置。
- 返回: `object`

### ztools.http.clearHeaders()
清除请求头配置。
- 返回: `boolean`

## AI API

### ztools.ai(option, streamCallback)
调用 AI 模型。支持流式和非流式两种模式。
- `option`: `object` - AI 调用配置
- `streamCallback`: `(chunk: any) => void` - (可选) 流式回调函数
- 返回: `PromiseLike & { abort: () => void }`

```javascript
// 非流式调用
const result = await ztools.ai({ prompt: '你好' })

// 流式调用
const request = ztools.ai({ prompt: '你好' }, (chunk) => {
  console.log('收到数据:', chunk)
})
await request

// 中断请求
request.abort()
```

### ztools.allAiModels()
获取所有可用的 AI 模型列表。
- 返回: `Promise<object[]>`