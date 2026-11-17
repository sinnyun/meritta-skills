#!/usr/bin/env node
import { mkdirSync, readFileSync, unlinkSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { spawnSync } from 'node:child_process'

const cli = process.env.FIGCRAFT_CLI || 'C:\\Program Files\\FigCraft\\figcraft-cli.exe'
const output = resolve(process.argv[2] || 'DeskSuite-FigCraft-界面复刻.figcraft')
const planPath = resolve(dirname(output), 'artifacts', 'figcraft-reference', 'figcraft-build-plan.json')
const metricsPath = resolve(dirname(output), 'artifacts', 'figcraft-reference', 'desksuite-ui-metrics.json')
const steps = []
let next = 0

function add(command, params = {}) { steps.push({ command, params }) }
function key() { return `n${next++}` }
function ref(name) { return { $ref: name } }

function cssColor(value) {
  if (!value || value === 'transparent' || value.includes('0, 0, 0, 0')) return null
  const match = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/)
  if (!match) return null
  return `#${match.slice(1, 4).map(part => Number(part).toString(16).padStart(2, '0')).join('')}`
}

function fontStyle(weight) {
  const number = Number.parseInt(weight, 10)
  if (number >= 700) return 'Bold'
  if (number >= 600) return 'SemiBold'
  if (number >= 500) return 'Medium'
  return 'Regular'
}

function textAlign(value) {
  if (value === 'start') return 'left'
  if (value === 'end') return 'right'
  return ['left', 'center', 'right', 'justified'].includes(value) ? value : 'left'
}

function measuredPage(name) {
  const metrics = JSON.parse(readFileSync(metricsPath, 'utf8'))
  if (metrics.viewport.width !== 1600 || metrics.viewport.height !== 1000) {
    throw new Error(`Expected a 1600×1000 CSS viewport, got ${metrics.viewport.width}×${metrics.viewport.height}`)
  }
  const commands = []
  let serial = 0
  const id = () => `m${serial++}`
  const root = id()
  commands.push({ command: 'node.create', as: root, params: { type: 'frame', name, x: 0, y: 0, width: 1600, height: 1000, props: { fill: '#f2f4f8' }, select: false } })
  const regionColors = ['#ffffff', '#fafbfd', '#ffffff', '#f2f4f8', '#ffffff', '#ffffff', '#ffffff']
  const regionNames = ['应用标题栏', '活动入口栏', '文件快捷导航侧栏', '文件列表与工作区', '属性与版本侧栏', '底部调试控制台', '运行状态栏']
  const regionRects = [
    { x: 0, y: 0, w: 1600, h: 44 }, { x: 0, y: 44, w: 48, h: 924 },
    { x: 48, y: 44, w: 268, h: 924 }, { x: 322, y: 44, w: 952, h: 698 },
    { x: 1280, y: 44, w: 320, h: 924 }, { x: 322, y: 742, w: 952, h: 226 },
    { x: 0, y: 968, w: 1600, h: 32 }
  ]
  regionRects.forEach((rect, i) => commands.push({ command: 'node.create', as: id(), params: {
    type: 'frame', name: regionNames[i], parent: ref(root), ...rect,
    props: { fill: regionColors[i], stroke: i === 3 || i === 5 ? '#e2e8f0' : 'none', strokeWeight: i === 3 || i === 5 ? 1 : 0 }, select: false
  } }))
  // The two six-pixel bars are the real draggable panel splitters.
  for (const [label, x, y, h] of [['左侧栏分隔条', 316, 44, 924], ['右侧栏分隔条', 1274, 44, 924]]) {
    commands.push({ command: 'node.create', as: id(), params: { type: 'rectangle', name: label, parent: ref(root), x, y, width: 6, height: h, props: { fill: '#e2e8f0' }, select: false } })
  }
  metrics.controls.forEach((item, index) => {
    const r = item.rect
    const fill = cssColor(item.bg)
    const border = item.borderStyle !== 'none' && Number.parseFloat(item.borderWidth) > 0 ? cssColor(item.border) : null
    if (!fill && !border) return
    const radiusValue = Number.parseFloat(item.radius) || 0
    const radius = Math.min(radiusValue, r.w / 2, r.h / 2, 20)
    commands.push({ command: 'node.create', as: id(), params: {
      type: 'frame', name: `控件 ${String(index + 1).padStart(3, '0')} ${item.text || item.title || item.tag}`,
      parent: ref(root), x: r.x, y: r.y, width: r.w, height: r.h,
      props: { fill: fill ?? 'none', stroke: border ?? 'none', strokeWeight: border ? Math.max(0.5, Number.parseFloat(item.borderWidth) || 1) : 0, cornerRadius: radius }, select: false
    } })
  })
  metrics.text.forEach((item, index) => {
    const r = item.rect
    const color = cssColor(item.color) ?? '#334155'
    const fontSize = Number.parseFloat(item.font) || 12
    commands.push({ command: 'node.create', as: id(), params: {
      type: 'text', name: `文字 ${String(index + 1).padStart(3, '0')} ${item.text.slice(0, 32)}`,
      text: item.text, parent: ref(root), x: r.x, y: r.y, width: Math.max(r.w, 1), height: Math.max(r.h, fontSize),
      props: { fontFamily: 'Segoe UI', fontStyle: fontStyle(item.weight), fontSize, fill: color, textAlign: textAlign(item.textAlign), textAlignVertical: 'middle', textAutoResize: 'widthAndHeight' }, select: false
    } })
  })
  metrics.controls.filter(item => item.tag === 'select' || item.tag === 'input').forEach((item, index) => {
    const value = item.tag === 'select' ? item.value : item.placeholder
    if (!value) return
    const r = item.rect
    commands.push({ command: 'node.create', as: id(), params: {
      type: 'text', name: `字段占位 ${index + 1} ${value.slice(0, 24)}`, text: value,
      parent: ref(root), x: r.x + 8, y: r.y + 1, width: Math.max(1, r.w - 16), height: Math.max(1, r.h - 2),
      props: { fontFamily: 'Segoe UI', fontStyle: fontStyle(item.weight), fontSize: Number.parseFloat(item.font) || 12, fill: cssColor(item.color) ?? '#64748b', textAlign: textAlign(item.textAlign), textAlignVertical: 'middle', textAutoResize: 'widthAndHeight' }, select: false
    } })
  })
  const rows = [
    ['Desktop', '文件夹', '—', '今天 18:22'], ['Documents', '文件夹', '—', '今天 16:05'],
    ['Downloads', '文件夹', '—', '今天 15:48'], ['Pictures', '文件夹', '—', '昨天 21:13'],
    ['Projects', '文件夹', '—', '昨天 19:37'], ['Videos', '文件夹', '—', '10 月 28 日'],
    ['Design brief.md', 'Markdown', '8 KB', '10 月 28 日'], ['FigCraft 界面参考.figcraft', 'FigCraft', '2.4 MB', '10 月 27 日'],
    ['Project notes.md', 'Markdown', '12 KB', '10 月 26 日'], ['workspace-preview.png', 'PNG 图像', '640 KB', '10 月 25 日'],
    ['WorkCrate', '文件夹', '—', '10 月 24 日'], ['whiteboard-scenes', '文件夹', '—', '10 月 23 日'],
    ['readme.txt', '文本文件', '3 KB', '10 月 22 日'], ['Components', '文件夹', '—', '10 月 21 日'],
    ['FigCraft', '文件夹', '—', '10 月 20 日'], ['Notes', '文件夹', '—', '10 月 19 日'],
    ['Resources', '文件夹', '—', '10 月 18 日'], ['Settings.json', 'JSON 文件', '2 KB', '10 月 17 日']
  ]
  rows.forEach((row, index) => {
    const y = 158 + index * 32
    if (index === 4) commands.push({ command: 'node.create', as: id(), params: { type: 'rectangle', name: '当前选中的 Projects 行', parent: ref(root), x: 322, y, width: 952, height: 32, props: { fill: '#eef0ff' }, select: false } })
    commands.push({ command: 'node.create', as: id(), params: { type: 'text', name: `文件名 ${index + 1}`, text: row[0], parent: ref(root), x: 380, y: y + 8, width: 350, height: 16, props: { fontFamily: 'Segoe UI', fontStyle: index === 4 ? 'SemiBold' : 'Medium', fontSize: 12, fill: '#46566c', textAlignVertical: 'middle', textAutoResize: 'widthAndHeight' }, select: false } })
    commands.push({ command: 'node.create', as: id(), params: { type: 'text', name: `文件类型 ${index + 1}`, text: row[1], parent: ref(root), x: 946, y: y + 8, width: 80, height: 16, props: { fontFamily: 'Segoe UI', fontSize: 11, fill: '#7b899c', textAlignVertical: 'middle', textAutoResize: 'widthAndHeight' }, select: false } })
    commands.push({ command: 'node.create', as: id(), params: { type: 'text', name: `文件大小 ${index + 1}`, text: row[2], parent: ref(root), x: 1026, y: y + 8, width: 96, height: 16, props: { fontFamily: 'Segoe UI', fontSize: 11, fill: '#7b899c', textAlign: 'right', textAlignVertical: 'middle', textAutoResize: 'widthAndHeight' }, select: false } })
    commands.push({ command: 'node.create', as: id(), params: { type: 'text', name: `修改时间 ${index + 1}`, text: row[3], parent: ref(root), x: 1122, y: y + 8, width: 144, height: 16, props: { fontFamily: 'Segoe UI', fontSize: 10, fill: '#8290a3', textAlign: 'right', textAlignVertical: 'middle', textAutoResize: 'widthAndHeight' }, select: false } })
    commands.push({ command: 'node.create', as: id(), params: { type: 'rectangle', name: `文件行分隔 ${index + 1}`, parent: ref(root), x: 322, y: y + 31, width: 952, height: 1, props: { fill: '#eef1f5' }, select: false } })
  })
  add('command.batch', { label: '从 DeskSuite DOM 像素数据重建主工作台', commands })
}

function page(name) {
  const view = name.slice(0, 2)
  if (!steps.length) {
    add('file.new', { name: 'DeskSuite 界面复刻' })
    add('page.rename', { name })
    measuredPage(name)
    return
  }
  if (steps.length) add('page.add', { name })
  else {
    add('file.new', { name: 'DeskSuite 界面复刻' })
    add('page.rename', { name })
  }
  const commands = []
  let serial = 0
  const id = () => `p${serial++}`
  const box = (parent, name, x, y, width, height, fill, radius = 0, stroke) => {
    const token = id()
    const props = { fill, cornerRadius: radius }
    if (stroke) { props.stroke = stroke; props.strokeWeight = 1 }
    commands.push({ command: 'node.create', as: token, params: { type: 'frame', name, parent: ref(parent), x, y, width, height, props, select: false } })
    return token
  }
  const text = (parent, name, value, x, y, width, height, fontSize = 13, color = '#334155', weight = 'Regular', align = 'left') => {
    const token = id()
    commands.push({ command: 'node.create', as: token, params: { type: 'text', name, text: value, parent: ref(parent), x, y, width, height, props: { fontFamily: 'Inter', fontStyle: weight, fontSize, fill: color, textAlign: align, textAlignVertical: 'middle', textAutoResize: 'none' }, select: false } })
    return token
  }
  const button = (parent, name, value, x, y, width, height, selected = false, fill = '#ffffff') => {
    const token = box(parent, `${name} control`, x, y, width, height, selected ? '#eef0ff' : fill, 8, selected ? '#bfc4ff' : '#e3e8f0')
    text(token, `${name} label`, value, 7, 0, width - 14, height, 12, selected ? '#5149d6' : '#475569', selected ? 'Medium' : 'Regular', 'center')
    return token
  }
  const line = (parent, name, x, y, width, color = '#e7ebf2') => box(parent, name, x, y, width, 1, color)
  const commandsBefore = commands.length
  const root = id()
  commands.push({ command: 'node.create', as: root, params: { type: 'frame', name, x: 0, y: 0, width: 1600, height: 1000, props: { fill: '#f6f7fb', stroke: '#cbd3df', strokeWeight: 1 }, select: false } })

  const header = box(root, '应用标题栏', 0, 0, 1600, 46, '#ffffff')
  box(header, 'DeskSuite 图标底', 14, 9, 28, 28, '#635bdf', 8)
  text(header, 'DeskSuite 标识', '▧', 16, 8, 24, 28, 17, '#ffffff', 'Bold', 'center')
  text(header, '应用名称', 'DeskSuite', 52, 0, 86, 46, 15, '#202939', 'Bold')
  line(header, '品牌分隔线', 150, 11, 1, '#e4e8ef')
  const menus = ['文件(F)', '编辑(E)', '视图(V)', '插件(P)', '帮助(H)']
  menus.forEach((label, index) => text(header, `${label} 菜单`, label, 166 + index * 88, 0, 76, 46, 13, '#536176'))
  text(header, '顶部搜索', '⌕', 1220, 0, 34, 46, 22, '#738198', 'Regular', 'center')
  button(header, '悬浮面板入口', '☷  悬浮面板', 1262, 8, 112, 30, true)
  text(header, '撤销按钮', '↶', 1390, 0, 34, 46, 21, '#65748a', 'Regular', 'center')
  button(header, '外观主题', '☾', 1440, 8, 34, 30)
  text(header, '最小化', '−', 1490, 0, 34, 46, 18, '#526074', 'Regular', 'center')
  text(header, '最大化', '□', 1526, 0, 34, 46, 15, '#526074', 'Regular', 'center')
  text(header, '关闭窗口', '×', 1562, 0, 30, 46, 20, '#526074', 'Regular', 'center')
  line(root, '标题栏下边线', 0, 45, 1600)

  const workspace = box(root, '工作区主体', 0, 46, 1600, 926, '#f4f6fa')
  const activity = box(workspace, '活动栏', 0, 0, 48, 926, '#fbfcfe')
  line(activity, '活动栏分隔', 47, 0, 1)
  const activityItems = [
    ['▱', '文件'], ['▥', '统计'], ['▣', '暂存'], ['›_', '控制台'], ['▦', '白板'], ['⌁', '资源'], ['▤', '笔记'], ['▣', '剪贴板'], ['▣', '启动台'], ['▣', '工程箱']
  ]
  const activeActivity = view === '02' ? '白板' : view === '03' ? '笔记' : view === '04' ? '资源' : '文件'
  activityItems.forEach(([icon, label], index) => {
    const active = label === activeActivity
    const y = 12 + index * 66
    if (active) box(activity, '活动入口选中底', 4, y, 39, 48, '#edf0ff', 10)
    text(activity, `${label} 图标`, icon, 7, y + 2, 34, 24, 18, active ? '#625ce5' : '#77869b', 'Medium', 'center')
    text(activity, `${label} 标签`, label, 4, y + 26, 40, 16, 9, active ? '#5c57d9' : '#718097', 'Medium', 'center')
  })
  text(activity, '设置入口图标', '⚙', 8, 858, 32, 28, 17, '#75849a', 'Regular', 'center')
  text(activity, '设置入口文字', '设置', 5, 886, 38, 18, 9, '#77869b', 'Regular', 'center')

  const sidebar = box(workspace, '资源管理侧栏', 48, 0, 270, 926, '#ffffff')
  button(sidebar, '资源管理标签', '▱ 资源管理', 12, 10, 120, 30, true)
  text(sidebar, '标签页入口', '◇  标签', 145, 10, 74, 30, 12, '#66758a')
  text(sidebar, '收起侧栏', '‹', 238, 8, 24, 32, 20, '#8491a4', 'Regular', 'center')
  line(sidebar, '侧栏头部分隔', 0, 48, 270)
  if (view === '01') {
  text(sidebar, '快速访问标题', '⌄　快速访问', 16, 58, 154, 24, 12, '#526176', 'SemiBold')
  text(sidebar, '快速访问刷新', '⟳', 235, 58, 24, 24, 15, '#8390a4', 'Regular', 'center')
  const quick = ['⌂　主目录', '▱　桌面', '▤　文档', '↓　下载', '▧　图片']
  quick.forEach((label, i) => text(sidebar, `快速访问 ${i + 1}`, label, 20, 88 + i * 32, 190, 28, 12, '#607087'))
  line(sidebar, '快速访问分隔', 14, 256, 242)
  text(sidebar, '驱动器标题', '⌄　驱动器', 16, 266, 160, 26, 12, '#526176', 'SemiBold')
  ;[['C:', '55.6 GB 可用', 220], ['D:', '138 GB 可用', 188], ['E:', '3.1 TB 可用', 126], ['V:', '3.5 TB 可用', 40]].forEach(([drive, free, fillWidth], i) => {
    const y = 299 + i * 54
    text(sidebar, `驱动器 ${drive}`, `▱  ${drive}`, 22, y, 56, 22, 12, '#526176', 'SemiBold')
    text(sidebar, `${drive} 可用空间`, String(free), 128, y, 119, 20, 10, '#8794a7', 'Regular', 'right')
    box(sidebar, `${drive} 容量底轨`, 18, y + 27, 238, 5, '#e8ebf2', 4)
    box(sidebar, `${drive} 容量已用`, 18, y + 27, Number(fillWidth), 5, '#7168eb', 4)
  })
  line(sidebar, '驱动器分隔', 14, 522, 242)
  text(sidebar, '快捷收藏标题', '快捷收藏', 16, 532, 128, 24, 12, '#526176', 'SemiBold')
  text(sidebar, '收藏说明', '选中文件夹后，点击星号可加入收藏', 18, 566, 235, 32, 10, '#a0aabc')
  text(sidebar, '常用收藏', '⌄　常用　0', 18, 610, 154, 26, 11, '#637189', 'SemiBold')
  text(sidebar, '新建收藏按钮', '＋', 234, 610, 24, 24, 15, '#6e67e9', 'Medium', 'center')
  button(sidebar, '新建分组', '＋  新建分组', 16, 852, 238, 34)
  } else {
    const sectionTitle = view === '02' ? '页面与图层' : view === '03' ? '笔记目录' : '资源文件夹'
    text(sidebar, `${sectionTitle} 标题`, `⌄　${sectionTitle}`, 16, 58, 190, 26, 12, '#526176', 'SemiBold')
    text(sidebar, `${sectionTitle} 操作`, '＋　•••', 214, 58, 42, 26, 11, '#7b899d', 'Medium', 'right')
    if (view === '02') {
      ;['⌄　Pages', '　▧　Board', '⌄　图层', '　▣　路线图白板', '　　▤　标题与说明', '　　▦　进行中', '　　　▢　文件索引优化', '　　　▢　统一资源预览', '　　▦　待设计', '　　　▢　新手引导流程', '　　　▢　标签管理体验', '　　▦　已完成'].forEach((label, i) => text(sidebar, `画布图层 ${i + 1}`, label, 18, 94 + i * 32, 235, 28, 11, i === 3 ? '#5f59dc' : '#637189', i === 3 ? 'SemiBold' : 'Regular'))
    } else if (view === '03') {
      ;['⌄　最近打开', '　▤　项目计划.md', '　▤　设计规范.md', '　▤　会议记录.md', '⌄　文件夹', '　▱　产品设计', '　▤　用户流程.md', '　▤　工作台改版.md', '　▱　参考资料', '　▤　FigCraft 界面.md'].forEach((label, i) => text(sidebar, `笔记目录 ${i + 1}`, label, 18, 94 + i * 34, 235, 30, 11, i === 1 ? '#5f59dc' : '#637189', i === 1 ? 'SemiBold' : 'Regular'))
      button(sidebar, '新建笔记', '＋　新建笔记', 16, 852, 238, 34)
    } else {
      ;['⌄　图片', '　▱　产品截图', '　▱　插画', '　▱　界面草图', '⌄　视频', '　▱　录屏素材', '⌄　文档', '　▤　项目计划', '　▤　需求说明', '⌄　最近使用', '　▧　alpine-trail.jpg'].forEach((label, i) => text(sidebar, `资源目录 ${i + 1}`, label, 18, 94 + i * 34, 235, 30, 11, i === 10 ? '#5f59dc' : '#637189', i === 10 ? 'SemiBold' : 'Regular'))
      button(sidebar, '添加资源', '＋　添加资源', 16, 852, 238, 34)
    }
  }

  const center = box(workspace, '中央工作区', 318, 0, 962, 926, '#f5f7fb')
  const address = box(center, '路径与导航工具栏', 0, 0, 962, 48, '#ffffff')
  ;['‹', '›', '↑', '⟳', '▱'].forEach((glyph, i) => text(address, `导航按钮 ${i + 1}`, glyph, 14 + i * 38, 0, 28, 48, 17, '#66758a', 'Regular', 'center'))
  const pathbox = box(address, '路径地址栏', 204, 7, 492, 34, '#f8faff', 16, '#e4e9f1')
  const pathLabel = view === '02' ? '▱　工作区　›　白板　›　产品路线图' : view === '03' ? '▤　工作区　›　Notes　›　项目计划.md' : view === '04' ? '▧　资源库　›　图片　›　预览' : '▱　C: 　›　 Users　 ›　 Administrator'
  text(pathbox, '当前路径', pathLabel, 14, 0, 440, 34, 12, '#5e6d84')
  box(address, '当前目录搜索框', 706, 7, 238, 34, '#ffffff', 16, '#e4e9f1')
  text(address, '目录搜索占位', '⌕　在当前目录搜索', 718, 7, 184, 34, 11, '#97a2b3')
  if (view === '01') {
  const filters = box(center, '工作区筛选工具栏', 0, 48, 962, 48, '#ffffff')
  text(filters, '工作区标签', '工作区', 16, 0, 50, 48, 11, '#68768b')
  button(filters, '工作区下拉框', '全部工作区　⌄', 68, 8, 140, 32)
  button(filters, '布局下拉框', '单栏　⌄', 214, 8, 80, 32)
  button(filters, '新建菜单', '＋ 新建', 302, 8, 80, 32)
  button(filters, '选择计数', '1', 390, 8, 30, 32, true, '#625de5')
  button(filters, '类型筛选', '▽ 全部类型　⌄', 430, 8, 126, 32)
  button(filters, '评分筛选', '全部评分　⌄', 566, 8, 118, 32)
  text(filters, '收藏过滤', '☆', 694, 8, 34, 32, 19, '#748198', 'Regular', 'center')
  button(filters, '排序规则', '按名称　⌄', 734, 8, 102, 32)
  text(filters, '升序按钮', '↑', 842, 8, 26, 32, 14, '#62718a', 'Medium', 'center')
  button(filters, '列表视图', '☷', 874, 8, 34, 32, true)
  button(filters, '网格视图', '▦', 912, 8, 34, 32)
  } else if (view === '02') {
    const controls = box(center, '画布文档工具栏', 0, 48, 962, 48, '#ffffff')
    text(controls, '画布文件名', '产品路线图', 16, 0, 150, 48, 12, '#46566c', 'SemiBold')
    button(controls, '画布页面选择', 'Board　⌄', 166, 8, 96, 32)
    text(controls, '画布保存状态', '● 已保存', 278, 8, 88, 32, 10, '#53a77b')
    button(controls, '画布版本历史', '◷ 版本历史', 720, 8, 108, 32)
    button(controls, '画布演示', '▷ 演示', 838, 8, 76, 32)
    button(controls, '画布分享', '分享', 920, 8, 34, 32, true)
  } else if (view === '03') {
    const controls = box(center, '笔记文档工具栏', 0, 48, 962, 48, '#ffffff')
    text(controls, '当前笔记名称', '项目计划.md', 16, 0, 180, 48, 12, '#46566c', 'SemiBold')
    button(controls, '笔记模式选择', '源码 + 阅读　⌄', 204, 8, 128, 32)
    text(controls, '笔记保存状态', '● 已保存', 350, 8, 86, 32, 10, '#53a77b')
    button(controls, '笔记搜索', '⌕ 查找', 748, 8, 70, 32)
    button(controls, '笔记版本', '◷ 版本', 826, 8, 72, 32)
    button(controls, '笔记更多', '•••', 908, 8, 44, 32)
  } else {
    const controls = box(center, '资源库筛选工具栏', 0, 48, 962, 48, '#ffffff')
    button(controls, '资源类型筛选', '全部资源类型　⌄', 14, 8, 144, 32)
    button(controls, '资源排序', '最近使用　⌄', 168, 8, 120, 32)
    button(controls, '资源视图', '▦ 网格', 298, 8, 84, 32, true)
    button(controls, '资源列表视图', '☷ 列表', 390, 8, 84, 32)
    text(controls, '资源项目数', '128 个资源', 510, 8, 110, 32, 10, '#8996a8')
    button(controls, '资源导入', '＋ 添加资源', 818, 8, 124, 32)
  }
  if (view === '01') {
  const table = box(center, '文件列表区域', 0, 96, 962, 612, '#ffffff', 0, '#dfe5ed')
  const tableHead = box(table, '列表表头', 0, 0, 962, 38, '#fbfcfe')
  text(tableHead, '全选框', '□', 16, 0, 24, 38, 16, '#8794a7', 'Regular', 'center')
  text(tableHead, '名称列标题', '名称 ↑', 46, 0, 330, 38, 12, '#5d67d8', 'SemiBold')
  text(tableHead, '标签列标题', '标签', 426, 0, 100, 38, 11, '#65748a', 'SemiBold')
  text(tableHead, '类型列标题', '类型', 552, 0, 96, 38, 11, '#65748a', 'SemiBold')
  text(tableHead, '大小列标题', '大小', 674, 0, 90, 38, 11, '#65748a', 'SemiBold')
  text(tableHead, '修改时间标题', '修改时间', 792, 0, 150, 38, 11, '#65748a', 'SemiBold')
  line(table, '表头下边线', 0, 37, 962)
  const fileRows = [
    ['▱', 'Desktop', '文件夹', '—', '今天 18:22'], ['▱', 'Documents', '文件夹', '—', '今天 16:05'],
    ['▱', 'Downloads', '文件夹', '—', '今天 15:48'], ['▱', 'Pictures', '文件夹', '—', '昨天 21:13'],
    ['▱', 'Projects', '文件夹', '—', '昨天 19:37'], ['▱', 'Videos', '文件夹', '—', '10 月 28 日'],
    ['▤', 'Design brief.md', 'Markdown', '8 KB', '10 月 28 日'], ['▧', 'FigCraft 界面参考.figcraft', 'FigCraft', '2.4 MB', '10 月 27 日'],
    ['▤', 'Project notes.md', 'Markdown', '12 KB', '10 月 26 日'], ['▧', 'workspace-preview.png', 'PNG 图像', '640 KB', '10 月 25 日'],
    ['▱', 'WorkCrate', '文件夹', '—', '10 月 24 日'], ['▱', 'whiteboard-scenes', '文件夹', '—', '10 月 23 日'],
    ['▤', 'readme.txt', '文本文件', '3 KB', '10 月 22 日']
  ]
  fileRows.forEach((row, i) => {
    const y = 39 + i * 43
    if (i === 4) box(table, '选中文件行', 1, y, 960, 42, '#f0f1ff')
    text(table, `行 ${i + 1} 收藏`, '☆', 9, y, 25, 42, 15, '#bcc6d5', 'Regular', 'center')
    text(table, `行 ${i + 1} 图标`, row[0], 34, y, 25, 42, 17, i === 4 ? '#f1a33a' : '#f3a13a', 'Regular', 'center')
    text(table, `文件行 ${i + 1} 名称`, row[1], 62, y, 336, 42, 12, '#46566c', i === 4 ? 'SemiBold' : 'Medium')
    text(table, `文件行 ${i + 1} 标签`, i === 4 ? '项目' : '', 426, y, 106, 42, 10, '#79889c')
    text(table, `文件行 ${i + 1} 类型`, row[2], 552, y, 106, 42, 11, '#7b899c')
    text(table, `文件行 ${i + 1} 大小`, row[3], 674, y, 88, 42, 11, '#7b899c')
    text(table, `文件行 ${i + 1} 修改时间`, row[4], 790, y, 154, 42, 10, '#8290a3')
    line(table, `文件行 ${i + 1} 分隔`, 0, y + 42, 962, '#eef1f5')
  })
  } else if (view === '02') {
    const tools = box(center, '白板工具栏', 0, 96, 962, 46, '#ffffff', 0, '#e2e7ef')
    ;['↖', '▧', '▭', '◯', 'T', '⌁', '→', '☷'].forEach((glyph, i) => button(tools, `白板工具 ${i + 1}`, glyph, 10 + i * 42, 7, 34, 32, i === 0))
    text(tools, '白板工具分隔', '│', 356, 7, 20, 32, 15, '#d4dbe6', 'Regular', 'center')
    button(tools, '白板缩放', '75%　⌄', 822, 7, 82, 32)
    button(tools, '白板分享', '↗ 分享', 906, 7, 48, 32)
    const stage = box(center, '白板画布', 0, 142, 962, 566, '#eef1f7')
    for (let x = 20; x < 962; x += 24) box(stage, `画布网格竖线 ${x}`, x, 0, 1, 566, '#e7eaf1')
    for (let y = 18; y < 566; y += 24) box(stage, `画布网格横线 ${y}`, 0, y, 962, 1, '#e7eaf1')
    const board = box(stage, '路线图白板区域', 112, 54, 728, 432, '#ffffff', 18, '#d9dfeb')
    text(board, '白板标题', '产品路线图', 26, 20, 400, 36, 23, '#263449', 'Bold')
    text(board, '白板副标题', 'DeskSuite  ·  2026 Q4 规划', 28, 58, 420, 24, 12, '#8491a4')
    ;[['进行中', '#fff3cf', '#db9c27', ['文件索引优化', '统一资源预览', 'WorkCrate 同步']], ['待设计', '#eeeaff', '#655ce2', ['新手引导流程', '标签管理体验', '启动台布局']], ['已完成', '#e6f6ed', '#339565', ['MCP 工具目录', '剪贴板历史']]].forEach(([heading, fill, ink, cards], col) => {
      const x = 24 + col * 232
      const lane = box(board, `${heading} 卡片列`, x, 104, 216, 294, '#f8f9fc', 12, '#e8ecf3')
      box(lane, `${heading} 标题底`, 10, 10, 196, 34, fill, 8)
      text(lane, `${heading} 标题`, heading, 18, 10, 156, 34, 13, ink, 'SemiBold')
      ;cards.forEach((card, i) => {
        const task = box(lane, `${card} 卡片`, 10, 54 + i * 72, 196, 62, '#ffffff', 9, '#e6eaf1')
        text(task, `${card} 文案`, card, 12, 8, 170, 24, 12, '#415168', 'Medium')
        text(task, `${card} 描述`, i === 0 ? '设计与实现持续推进' : '待评审 · 产品体验', 12, 34, 170, 18, 10, '#9aa6b7')
      })
      text(lane, `${heading} 添加卡片`, '＋ 添加便签', 14, 264, 188, 22, 10, '#8996a8')
    })
    text(stage, '白板缩放提示', '按住空格拖动画布　　滚轮缩放', 650, 530, 286, 22, 10, '#8c98a9', 'Regular', 'right')
  } else if (view === '03') {
    const toolbar = box(center, '笔记编辑工具栏', 0, 96, 962, 46, '#ffffff', 0, '#e2e7ef')
    ;[['B', 32], ['I', 32], ['⌁', 32], ['H', 42], ['☷', 36], ['▤', 36], ['↗', 36]].forEach(([glyph, width], i) => button(toolbar, `笔记格式工具 ${i + 1}`, glyph, 10 + i * 42, 7, width, 32, i === 0))
    text(toolbar, 'Markdown 模式', 'Markdown　⌄', 454, 7, 120, 32, 11, '#67758a')
    text(toolbar, '自动保存提示', '● 已保存', 824, 7, 84, 32, 10, '#53a77b')
    button(toolbar, '笔记更多菜单', '•••', 912, 7, 40, 32)
    const editor = box(center, '笔记分屏编辑器', 0, 142, 962, 566, '#ffffff', 0, '#e2e7ef')
    const source = box(editor, 'Markdown 源码编辑区', 0, 0, 476, 566, '#ffffff')
    const preview = box(editor, 'Markdown 阅读预览区', 480, 0, 482, 566, '#ffffff')
    line(editor, '编辑预览分隔线', 478, 0, 1, '#e1e6ee')
    text(source, '行号', '1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n11\n12', 12, 18, 26, 320, 11, '#b0bac8')
    text(source, 'Markdown 正文', '# 项目计划\n\n## 本周目标\n\n完成工作台的主要界面整理，统一资源浏览与画布编辑流程。\n\n### 设计事项\n\n- 梳理文件列表和属性面板\n- 完成白板快捷工具栏\n- 补齐笔记目录与搜索\n\n> 先明确层级，再逐步打磨细节。\n\n```ts\nconst workspace = "DeskSuite"\n```', 54, 18, 398, 510, 12, '#475569', 'Regular')
    text(preview, '阅读预览标题', '项目计划', 34, 28, 400, 46, 28, '#273449', 'Bold')
    text(preview, '阅读预览小标题', '本周目标', 34, 94, 400, 32, 19, '#34445c', 'SemiBold')
    text(preview, '阅读预览正文', '完成工作台的主要界面整理，统一资源浏览与画布编辑流程。', 34, 132, 410, 62, 13, '#526176')
    text(preview, '设计事项标题', '设计事项', 34, 208, 400, 30, 18, '#34445c', 'SemiBold')
    text(preview, '设计事项列表', '•  梳理文件列表和属性面板\n•  完成白板快捷工具栏\n•  补齐笔记目录与搜索', 34, 248, 420, 98, 13, '#526176')
    box(preview, '引用块', 34, 370, 3, 60, '#736bed', 2)
    text(preview, '引用文字', '先明确层级，再逐步打磨细节。', 48, 370, 390, 60, 13, '#69788d')
    const code = box(preview, '代码示例区', 34, 458, 408, 50, '#f5f6fa', 8)
    text(code, '代码示例', 'const workspace = "DeskSuite"', 14, 6, 380, 38, 11, '#6359c9', 'Medium')
  } else {
    const tabs = box(center, '资源预览标签栏', 0, 96, 962, 46, '#ffffff', 0, '#e2e7ef')
    ;['全部资源', '图片', '视频', '音频', '文档'].forEach((tab, i) => button(tabs, `${tab}分类`, tab, 10 + i * 84, 7, 78, 32, i === 1))
    button(tabs, '预览比例选择', '适应窗口　⌄', 816, 7, 130, 32)
    const preview = box(center, '资源预览主区域', 0, 142, 962, 566, '#f1f3f8')
    const image = box(preview, '山野图片预览', 54, 30, 574, 430, '#d9e8df', 12)
    box(image, '图片天空', 0, 0, 574, 214, '#c8dfdc', 12)
    box(image, '远山剪影', 0, 182, 574, 248, '#8baba4', 120)
    box(image, '前景山峦', 0, 256, 574, 174, '#526f67', 100)
    box(image, '草坡前景', 0, 334, 574, 96, '#35594e', 80)
    box(image, '阳光', 430, 50, 54, 54, '#f5d98f', 30)
    text(preview, '预览画面文件名', 'alpine-trail.jpg', 54, 472, 400, 28, 13, '#405067', 'SemiBold')
    text(preview, '预览画面分辨率', '3840 × 2560 px　·　JPEG　·　8.4 MB', 54, 502, 430, 22, 10, '#8491a4')
    button(preview, '打开所在文件夹', '⌕ 打开所在位置', 752, 478, 166, 34)
  }

  const inspector = box(workspace, '右侧属性信息面板', 1280, 0, 320, 926, '#ffffff')
  button(inspector, '属性信息页签', 'ⓘ 属性信息', 12, 10, 118, 30, true)
  text(inspector, '版本历史页签', '◷ 版本历史', 142, 10, 112, 30, 11, '#738198')
  text(inspector, '属性栏收起', '›', 285, 10, 22, 30, 17, '#8491a4', 'Regular', 'center')
  line(inspector, '属性栏顶部分隔', 0, 48, 320)
  if (view === '01') {
  text(inspector, '未选择条目图标', '▱', 18, 64, 28, 30, 18, '#f0a13c')
  text(inspector, '未选择条目标题', '未选择条目', 52, 64, 220, 30, 13, '#334155', 'SemiBold')
  const summary = box(inspector, '目录统计卡片', 16, 108, 288, 166, '#ffffff', 12, '#e4e9f1')
  ;[['当前目录', 'C:\\Users\\Administrator'], ['条目总数', '167'], ['文件夹', '126'], ['文件', '41']].forEach(([label, value], i) => {
    text(summary, `摘要 ${label}`, label, 14, 12 + i * 34, 94, 28, 11, '#9aa6b8')
    text(summary, `摘要数值 ${label}`, value, 108, 12 + i * 34, 164, 28, 11, '#526176', 'Medium', 'right')
  })
  text(inspector, '属性面板帮助说明', '在文件列表中选择条目以查看属性、元数据与内容预览。按住 Ctrl 或 Shift 可多选。', 18, 292, 278, 64, 11, '#a0aabc')
  box(inspector, '元数据折叠项', 14, 378, 292, 42, '#fbfcfe', 8, '#e6eaf0')
  text(inspector, '元数据折叠标题', '›　元数据', 26, 378, 240, 42, 12, '#65748a', 'Medium')
  box(inspector, '快速预览折叠项', 14, 430, 292, 42, '#fbfcfe', 8, '#e6eaf0')
  text(inspector, '快速预览折叠标题', '›　快速预览', 26, 430, 240, 42, 12, '#65748a', 'Medium')
  } else if (view === '02') {
    text(inspector, '所选图层标题', '▣　路线图白板', 18, 62, 250, 32, 12, '#405067', 'SemiBold')
    line(inspector, '图层属性分隔', 14, 102, 292)
    text(inspector, '图层布局标题', '⌄　布局', 16, 110, 150, 24, 11, '#596980', 'SemiBold')
    ;[['X', '112'], ['Y', '54'], ['W', '728'], ['H', '432']].forEach(([label, value], i) => {
      const x = 16 + (i % 2) * 145, y = 144 + Math.floor(i / 2) * 54
      text(inspector, `画布属性 ${label}`, label, x, y, 28, 18, 9, '#9aa6b7')
      button(inspector, `画布属性值 ${label}`, value, x, y + 18, 130, 28)
    })
    text(inspector, '图层外观标题', '⌄　外观', 16, 260, 150, 24, 11, '#596980', 'SemiBold')
    button(inspector, '图层不透明度', '不透明度　100%', 16, 290, 138, 30)
    button(inspector, '图层混合模式', '混合模式　正常　⌄', 160, 290, 144, 30)
    text(inspector, '图层填充标题', '填充', 18, 336, 80, 30, 10, '#708097')
    button(inspector, '图层填充颜色', '　#FFFFFF', 78, 336, 148, 30)
    button(inspector, '图层填充添加', '＋', 268, 336, 34, 30)
    text(inspector, '图层描边标题', '描边', 18, 374, 80, 30, 10, '#708097')
    button(inspector, '图层描边添加', '＋　添加描边', 78, 374, 224, 30)
    text(inspector, '图层效果标题', '效果', 18, 412, 80, 30, 10, '#708097')
    button(inspector, '图层效果添加', '＋　添加效果', 78, 412, 224, 30)
    line(inspector, '导出分隔', 14, 462, 292)
    text(inspector, '导出设置标题', '⌄　导出设置', 16, 476, 160, 24, 11, '#596980', 'SemiBold')
    button(inspector, '导出格式选择', 'PNG　⌄', 16, 510, 88, 30)
    button(inspector, '导出缩放选择', '1×　⌄', 112, 510, 76, 30)
    button(inspector, '导出按钮', '导出图层', 196, 510, 108, 30, true)
  } else if (view === '03') {
    text(inspector, '笔记属性标题', '▤　项目计划.md', 18, 62, 260, 32, 12, '#405067', 'SemiBold')
    line(inspector, '笔记属性分隔', 14, 102, 292)
    text(inspector, '笔记元数据标题', '⌄　笔记属性', 16, 110, 160, 24, 11, '#596980', 'SemiBold')
    ;[['类型', 'Markdown'], ['字数', '248'], ['创建时间', '2026-10-28'], ['最后修改', '刚刚']].forEach(([label, value], i) => {
      text(inspector, `笔记属性 ${label}`, label, 18, 146 + i * 34, 88, 26, 10, '#9aa6b7')
      text(inspector, `笔记属性值 ${label}`, value, 112, 146 + i * 34, 178, 26, 10, '#5b6b81', 'Medium', 'right')
    })
    line(inspector, '笔记标签分隔', 14, 292, 292)
    text(inspector, '笔记标签标题', '⌄　标签', 16, 304, 150, 24, 11, '#596980', 'SemiBold')
    button(inspector, '笔记产品标签', '产品设计', 16, 338, 88, 26, true)
    button(inspector, '笔记计划标签', '规划', 110, 338, 70, 26)
    button(inspector, '笔记加标签', '＋', 186, 338, 34, 26)
    line(inspector, '笔记版本分隔', 14, 382, 292)
    text(inspector, '笔记版本标题', '⌄　版本历史', 16, 394, 180, 24, 11, '#596980', 'SemiBold')
    ;[['今天 18:20', '自动保存'], ['今天 16:42', '整理章节'], ['昨天 20:05', '初稿']].forEach(([time, description], i) => {
      text(inspector, `笔记版本 ${i + 1}`, `◷　${time}　${description}`, 18, 430 + i * 36, 280, 28, 10, '#64738a')
    })
    button(inspector, '创建笔记版本', '＋　创建版本', 16, 554, 288, 32)
  } else {
    text(inspector, '资源属性标题', '▧　alpine-trail.jpg', 18, 62, 270, 32, 12, '#405067', 'SemiBold')
    line(inspector, '资源属性分隔', 14, 102, 292)
    text(inspector, '资源基本信息标题', '⌄　基本信息', 16, 110, 160, 24, 11, '#596980', 'SemiBold')
    ;[['文件类型', 'JPEG 图像'], ['尺寸', '3840 × 2560 px'], ['文件大小', '8.4 MB'], ['色彩空间', 'sRGB'], ['修改时间', '2026-10-29 14:32'], ['文件夹', '图片 / 户外']].forEach(([label, value], i) => {
      text(inspector, `资源信息 ${label}`, label, 18, 146 + i * 34, 88, 26, 10, '#9aa6b7')
      text(inspector, `资源信息值 ${label}`, value, 104, 146 + i * 34, 200, 26, 10, '#5b6b81', 'Medium', 'right')
    })
    line(inspector, '资源颜色分隔', 14, 366, 292)
    text(inspector, '资源颜色信息标题', '⌄　主色调', 16, 378, 140, 24, 11, '#596980', 'SemiBold')
    ;[['#35594E', '#35594e'], ['#8BAB A4', '#8baba4'], ['#C8DFDC', '#c8dfdc']].forEach(([label, color], i) => {
      box(inspector, `资源主色 ${i + 1}`, 18 + i * 52, 416, 42, 32, color, 6, '#e1e6ed')
      text(inspector, `资源色值 ${i + 1}`, label, 12 + i * 52, 450, 54, 20, 8, '#8491a4', 'Regular', 'center')
    })
    button(inspector, '在文件夹中显示', '⌕　在文件夹中显示', 16, 504, 288, 32)
    button(inspector, '复制资源链接', '▢　复制资源链接', 16, 544, 288, 32)
  }

  const dock = box(center, '底部调试控制台', 0, 708, 962, 218, '#ffffff', 0, '#dfe5ed')
  const dockHead = box(dock, '控制台工具栏', 0, 0, 962, 44, '#fbfcfe')
  button(dockHead, '控制台当前面板', '›_ 调试控制台', 12, 7, 120, 30, true)
  text(dockHead, '复制日志按钮', '▢ 复制', 695, 0, 74, 44, 11, '#738198')
  text(dockHead, '导出日志按钮', '↓ 导出', 773, 0, 72, 44, 11, '#738198')
  text(dockHead, '清空日志按钮', '⌫ 清空', 850, 0, 68, 44, 11, '#738198')
  text(dockHead, '控制台收起按钮', '⌄', 924, 0, 26, 44, 16, '#738198', 'Regular', 'center')
  const counters = ['信息  1', '警告  0', '错误  0', '事件  1', '启动  10']
  counters.forEach((item, i) => button(dock, `日志过滤 ${i + 1}`, item, 12 + i * 92, 54, 82, 30, i === 0, '#625de5'))
  button(dock, '日志搜索框', '⌕ 搜索日志、来源或数据…', 678, 54, 242, 30)
  const logs = ['18:23:42.030　 EVENT　MCP　调用工具 capture_window', '18:23:38.327　 INFO　 Explorer　打开目录 C:\\Users\\Administrator', '18:23:37.195　 BOOT　 Runtime　主进程服务已就绪', '18:23:37.594　 BOOT　 Launcher　启动台插件已加载']
  logs.forEach((item, i) => text(dock, `日志记录 ${i + 1}`, item, 14, 92 + i * 27, 924, 26, 10, i === 0 ? '#74829a' : '#536982', 'Regular'))

  const status = box(root, '状态栏', 0, 972, 1600, 28, '#fbfcfe')
  box(status, '运行状态绿点', 14, 11, 7, 7, '#61c692', 4)
  text(status, '运行状态', '核心引擎就绪', 28, 0, 96, 28, 10, '#7c899c')
  text(status, '当前目录状态', '▱ C:\\Users\\Administrator　　126 个文件夹 / 41 个文件　　共 52.6 MB', 130, 0, 520, 28, 10, '#748198')
  text(status, '滚动状态', '⚡ 虚拟滚动', 660, 0, 100, 28, 10, '#f1a135')
  text(status, '日志总数', '›_　12', 1510, 0, 76, 28, 10, '#728096', 'Medium', 'right')

  if (commands.length <= commandsBefore) throw new Error('No design commands were generated')
  add('command.batch', { label: `绘制：${name}`, commands })
}

page('01 主工作台 · 文件浏览')
page('02 白板 · 画布工作区')
page('03 笔记 · Markdown 编辑')
page('04 资源 · 文件预览')

mkdirSync(dirname(output), { recursive: true })
writeFileSync(planPath, JSON.stringify(steps, null, 2), 'utf8')
const result = spawnSync(cli, ['run', planPath, '--out', output], { encoding: 'utf8', windowsHide: true, maxBuffer: 64 * 1024 * 1024 })
if (result.status !== 0) {
  if (result.stdout) process.stdout.write(result.stdout)
  if (result.stderr) process.stderr.write(result.stderr)
  process.exit(result.status ?? 1)
}
const outputLines = (result.stdout || '').trim().split(/\r?\n/)
if (outputLines.at(-1)) console.log(outputLines.at(-1))
unlinkSync(planPath)
console.log(`Saved ${output}`)
