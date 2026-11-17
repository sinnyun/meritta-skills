#!/usr/bin/env node
import { mkdirSync, unlinkSync, writeFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { spawnSync } from 'node:child_process'

const cli = process.env.FIGCRAFT_CLI || 'C:\\Program Files\\FigCraft\\figcraft-cli.exe'
const source = resolve(process.argv[2] || 'DeskSuite-FigCraft-界面复刻.figcraft')
const output = resolve(process.argv[3] || 'artifacts/figcraft-reference/DeskSuite-componentized.figcraft')
const planPath = resolve(dirname(output), 'componentized-build-plan.json')
const steps = []
let serial = 0
const id = (prefix = 'n') => `${prefix}${serial++}`
const ref = name => ({ $ref: name })
const add = (command, params = {}, as) => steps.push({ command, ...(as ? { as } : {}), params })

const C = {
  ink: '#263246', text: '#475569', muted: '#718096', faint: '#94a3b8',
  border: '#e2e8f0', softBorder: '#eef1f5', surface: '#ffffff',
  subtle: '#fafbfd', canvas: '#f2f4f8', selected: '#eef2ff',
  accent: '#5b5ce6', accentText: '#5b5ce6', green: '#4d9f78', amber: '#ee9a35'
}
const font = 'Segoe UI'

add('page.add', { name: '00 通用组件库' }, 'componentsPage')
add('node.create', { type: 'frame', name: 'DeskSuite UI 通用组件', x: 0, y: 0, width: 1600, height: 1000, props: { fill: '#f5f7fb' }, select: false }, 'componentsRoot')

function text(parent, name, value, x, y, width, height, size = 12, color = C.text, weight = 'Regular', align = 'left') {
  const token = id('t')
  add('node.create', { type: 'text', name, text: value, parent: ref(parent), x, y, width, height, props: {
    fontFamily: font, fontStyle: weight, fontSize: size, fill: color, textAlign: align,
    textAlignVertical: 'middle', textAutoResize: 'none'
  }, select: false }, token)
  return token
}

function box(parent, name, x, y, width, height, fill, radius = 0, stroke = null) {
  const token = id('b')
  const props = { fill, cornerRadius: radius }
  if (stroke) { props.stroke = stroke; props.strokeWeight = 1 }
  add('node.create', { type: 'frame', name, parent: ref(parent), x, y, width, height, props, select: false }, token)
  return token
}

const grid = {
  primary: [58, 152], secondary: [212, 152], quiet: [366, 152], icon: [520, 152],
  select: [590, 152], search: [764, 152], tabOn: [1010, 152], tabOff: [1120, 152],
  activityOn: [58, 350], activityOff: [126, 350], quick: [210, 350], section: [500, 350],
  drive: [760, 350], badge: [1020, 350], checkbox: [1100, 350],
  table: [58, 520], file: [58, 548], selectedFile: [58, 590],
  info: [58, 660], log: [58, 708], status: [58, 756]
}

function component({ name, x, y, width, height, fill = 'none', stroke = null, radius = 0, parts }) {
  const comp = id('c')
  const props = { fill, cornerRadius: radius }
  if (stroke) { props.stroke = stroke; props.strokeWeight = 1 }
  add('node.create', { type: 'component', name, parent: ref('componentsRoot'), x, y, width, height, props, select: false }, comp)
  for (const part of parts) {
    const layer = id('l')
    if (part.type === 'shape') {
      add('node.create', { type: 'rectangle', name: part.layer, parent: ref(comp), x: part.x, y: part.y, width: part.width, height: part.height, props: { fill: part.fill, cornerRadius: part.radius || 0 }, select: false }, layer)
      continue
    }
    // FigCraft stores many text layers at the font's natural height and does not
    // apply textAlignVertical consistently. Offset the layer inside its intended
    // slot so its visible glyphs stay centered in each reusable component.
    const centeredY = part.y + Math.max(0, (part.height - (part.size || 12)) / 2)
    add('node.create', { type: 'text', name: part.layer, text: part.default, parent: ref(comp), x: part.x, y: centeredY, width: part.width, height: part.height, props: {
      fontFamily: font, fontStyle: part.weight || 'Regular', fontSize: part.size || 12,
      fill: part.color || C.text, textAlign: part.align || 'left',
      textAlignVertical: part.vAlign || 'middle', textAutoResize: 'none'
    }, select: false }, layer)
    add('component.addProperty', { id: ref(comp), name: part.property, type: 'text', default: part.default, layer: ref(layer) })
  }
  return comp
}

const labelPart = (value, width, size = 12, color = C.text, weight = 'Medium', align = 'center') => ({ layer: 'Label', property: 'Label', default: value, x: 8, y: 0, width: width - 16, height: 32, size, color, weight, align })
const glyphPart = (value, width, height, size = 15, color = C.text) => ({ layer: 'Glyph', property: 'Glyph', default: value, x: 0, y: 0, width, height, size, color, weight: 'Regular', align: 'center' })

const comps = {}
comps.brand = component({ name: '品牌 / DeskSuite 标识', x: 1284, y: 244, width: 102, height: 32, fill: 'none', parts: [
  { type: 'shape', layer: 'Logo background', x: 0, y: 2, width: 28, height: 28, fill: C.accent, radius: 8 },
  { layer: 'Logo glyph', property: 'Glyph', default: '▱', x: 0, y: 2, width: 28, height: 26, size: 16, color: '#ffffff', weight: 'Bold', align: 'center' },
  { layer: 'Wordmark', property: 'Label', default: 'DeskSuite', x: 36, y: 0, width: 66, height: 32, size: 14, color: C.ink, weight: 'Bold' }
] })
comps.primary = component({ name: '按钮 / 主操作', x: grid.primary[0], y: grid.primary[1], width: 120, height: 32, fill: C.accent, radius: 9, parts: [labelPart('＋ 新建', 120, 12, '#ffffff')] })
comps.headerAction = component({ name: '按钮 / 顶栏主操作', x: 220, y: 244, width: 96, height: 26, fill: C.accent, radius: 13, parts: [{ layer: 'Label', property: 'Label', default: '☷  悬浮面板', x: 8, y: 0, width: 80, height: 26, size: 11, color: '#ffffff', weight: 'SemiBold', align: 'center' }] })
comps.secondary = component({ name: '按钮 / 次操作', x: grid.secondary[0], y: grid.secondary[1], width: 120, height: 32, fill: '#ffffff', stroke: C.border, radius: 9, parts: [labelPart('选择文件', 120, 12)] })
comps.secondaryWide = component({ name: '按钮 / 次操作宽版', x: 338, y: 244, width: 238, height: 34, fill: '#ffffff', stroke: C.border, radius: 9, parts: [labelPart('＋  新建分组', 238, 12)] })
comps.secondaryCompact = component({ name: '按钮 / 次操作紧凑版', x: 582, y: 244, width: 72, height: 32, fill: '#ffffff', stroke: C.border, radius: 9, parts: [labelPart('＋ 新建', 72, 11)] })
comps.quiet = component({ name: '按钮 / 静默菜单', x: grid.quiet[0], y: grid.quiet[1], width: 60, height: 24, fill: 'none', radius: 7, parts: [labelPart('文件(F)', 60, 12, C.text, 'Medium')] })
comps.iconButton = component({ name: '按钮 / 图标', x: grid.icon[0], y: grid.icon[1], width: 32, height: 32, fill: '#ffffff', stroke: C.border, radius: 9, parts: [glyphPart('⌕', 32, 32, 15, C.muted)] })
comps.ghostIcon = component({ name: '按钮 / 图标静默态', x: 670, y: 244, width: 32, height: 32, fill: 'none', radius: 8, parts: [glyphPart('⌕', 32, 32, 15, C.muted)] })
comps.activeIcon = component({ name: '按钮 / 图标选中态', x: 708, y: 244, width: 32, height: 32, fill: C.selected, stroke: '#d8dcff', radius: 9, parts: [glyphPart('☷', 32, 32, 14, C.accent)] })
comps.select = component({ name: '控件 / 下拉选择', x: grid.select[0], y: grid.select[1], width: 150, height: 32, fill: '#ffffff', stroke: C.border, radius: 16, parts: [
  { layer: 'Value', property: 'Value', default: '全部类型', x: 12, y: 0, width: 112, height: 32, size: 12, color: C.text },
  { layer: 'Chevron', property: 'Chevron', default: '⌄', x: 124, y: 0, width: 22, height: 32, size: 13, color: C.muted, align: 'center' }
] })
comps.selectMedium = component({ name: '控件 / 下拉选择中版', x: 746, y: 244, width: 128, height: 32, fill: '#ffffff', stroke: C.border, radius: 16, parts: [
  { layer: 'Value', property: 'Value', default: '工作区', x: 10, y: 0, width: 92, height: 32, size: 12, color: C.text },
  { layer: 'Chevron', property: 'Chevron', default: '⌄', x: 102, y: 0, width: 20, height: 32, size: 13, color: C.muted, align: 'center' }
] })
comps.selectSmall = component({ name: '控件 / 下拉选择紧凑版', x: 882, y: 244, width: 112, height: 32, fill: '#ffffff', stroke: C.border, radius: 16, parts: [
  { layer: 'Value', property: 'Value', default: '全部类型', x: 10, y: 0, width: 76, height: 32, size: 11, color: C.text },
  { layer: 'Chevron', property: 'Chevron', default: '⌄', x: 88, y: 0, width: 18, height: 32, size: 12, color: C.muted, align: 'center' }
] })
comps.selectCompact = component({ name: '控件 / 下拉选择窄版', x: 1002, y: 244, width: 86, height: 32, fill: '#ffffff', stroke: C.border, radius: 16, parts: [
  { layer: 'Value', property: 'Value', default: '单栏', x: 9, y: 0, width: 50, height: 32, size: 11, color: C.text },
  { layer: 'Chevron', property: 'Chevron', default: '⌄', x: 60, y: 0, width: 18, height: 32, size: 12, color: C.muted, align: 'center' }
] })
comps.address = component({ name: '控件 / 路径地址栏', x: 58, y: 548, width: 554, height: 34, fill: '#ffffff', stroke: C.border, radius: 17, parts: [
  { layer: 'Path', property: 'Path', default: '▱   C:   ›   Users   ›   User', x: 14, y: 0, width: 526, height: 34, size: 12, color: C.text }
] })
comps.search = component({ name: '控件 / 搜索输入框', x: grid.search[0], y: grid.search[1], width: 220, height: 32, fill: '#ffffff', stroke: C.border, radius: 16, parts: [
  { layer: 'Search glyph', property: 'Glyph', default: '⌕', x: 10, y: 0, width: 22, height: 32, size: 16, color: C.faint, align: 'center' },
  { layer: 'Placeholder', property: 'Placeholder', default: '在当前目录搜索', x: 36, y: 0, width: 172, height: 32, size: 12, color: C.faint }
] })
comps.topSearch = component({ name: '控件 / 顶栏搜索框', x: 1094, y: 244, width: 180, height: 32, fill: '#ffffff', stroke: C.border, radius: 16, parts: [
  { layer: 'Search glyph', property: 'Glyph', default: '⌕', x: 8, y: 0, width: 22, height: 32, size: 15, color: C.faint, align: 'center' },
  { layer: 'Placeholder', property: 'Placeholder', default: '在当前目录搜索', x: 32, y: 0, width: 138, height: 32, size: 11, color: C.faint }
] })
comps.tabOn = component({ name: '页签 / 选中', x: grid.tabOn[0], y: grid.tabOn[1], width: 94, height: 26, fill: C.selected, radius: 16, parts: [labelPart('资源管理', 94, 12, C.accentText, 'SemiBold')] })
comps.tabOff = component({ name: '页签 / 默认', x: grid.tabOff[0], y: grid.tabOff[1], width: 88, height: 26, fill: 'none', radius: 16, parts: [labelPart('标签', 88, 12, C.muted, 'Medium')] })
comps.activityOn = component({ name: '导航 / 活动项选中', x: grid.activityOn[0], y: grid.activityOn[1], width: 44, height: 44, fill: 'none', parts: [
  { type: 'shape', layer: '选中背景', x: 4, y: 0, width: 36, height: 36, fill: C.selected, radius: 10 },
  { layer: 'Icon', property: 'Icon', default: '▱', x: 4, y: 2, width: 36, height: 25, size: 18, color: C.accent, align: 'center' },
  { layer: 'Label', property: 'Label', default: '文件', x: 1, y: 26, width: 42, height: 15, size: 9, color: C.accent, weight: 'SemiBold', align: 'center' }
] })
comps.activityOff = component({ name: '导航 / 活动项默认', x: grid.activityOff[0], y: grid.activityOff[1], width: 44, height: 44, fill: 'none', parts: [
  { layer: 'Icon', property: 'Icon', default: '▤', x: 4, y: 2, width: 36, height: 25, size: 18, color: C.muted, align: 'center' },
  { layer: 'Label', property: 'Label', default: '笔记', x: 1, y: 26, width: 42, height: 15, size: 9, color: C.muted, align: 'center' }
] })
comps.quick = component({ name: '导航 / 快捷入口行', x: grid.quick[0], y: grid.quick[1], width: 232, height: 28, fill: 'none', radius: 6, parts: [
  { layer: 'Icon', property: 'Icon', default: '⌂', x: 8, y: 0, width: 20, height: 28, size: 15, color: C.muted, align: 'center' },
  { layer: 'Label', property: 'Label', default: '主目录', x: 34, y: 0, width: 186, height: 28, size: 12, color: C.text }
] })
comps.section = component({ name: '导航 / 分区标题', x: grid.section[0], y: grid.section[1], width: 236, height: 28, fill: 'none', parts: [
  { layer: 'Chevron', property: 'Chevron', default: '⌄', x: 4, y: 0, width: 16, height: 28, size: 13, color: C.muted, align: 'center' },
  { layer: 'Title', property: 'Title', default: '快速访问', x: 23, y: 0, width: 160, height: 28, size: 12, color: C.text, weight: 'SemiBold' },
  { layer: 'Action', property: 'Action', default: '', x: 196, y: 0, width: 32, height: 28, size: 13, color: C.muted, align: 'center' }
] })
function driveVariant(value, x, y, barWidth) {
  return component({ name: `容量=${value}`, x, y, width: 238, height: 46, fill: 'none', parts: [
    { layer: 'Drive', property: 'Drive', default: 'C:', x: 10, y: 0, width: 42, height: 22, size: 12, color: C.text, weight: 'SemiBold' },
    { layer: 'Available', property: 'Available', default: '55.6 GB 可用', x: 104, y: 0, width: 124, height: 22, size: 10, color: C.faint, align: 'right' },
    { type: 'shape', layer: '容量轨道', x: 4, y: 29, width: 230, height: 4, fill: '#e6eaf1', radius: 2 },
    { type: 'shape', layer: '容量进度', x: 4, y: 29, width: barWidth, height: 4, fill: C.accent, radius: 2 }
  ] })
}
const driveVariants = [
  driveVariant('高', grid.drive[0], grid.drive[1], 198),
  driveVariant('中', grid.drive[0], grid.drive[1], 156),
  driveVariant('低', grid.drive[0], grid.drive[1], 78),
  driveVariant('较低', grid.drive[0], grid.drive[1], 42)
]
add('component.combineVariants', { ids: driveVariants.map(ref) }, 'driveSet')
add('node.set', { ids: [ref('driveSet')], name: '数据 / 驱动器条目' })
comps.drive = 'driveSet'
comps.badge = component({ name: '状态 / 数字徽标', x: grid.badge[0], y: grid.badge[1], width: 28, height: 20, fill: C.accent, radius: 10, parts: [labelPart('1', 28, 10, '#ffffff', 'Bold')] })
comps.checkbox = component({ name: '控件 / 复选框', x: grid.checkbox[0], y: grid.checkbox[1], width: 16, height: 16, fill: '#ffffff', stroke: '#cbd5e1', radius: 3, parts: [] })
comps.tableHeader = component({ name: '数据 / 文件列表表头', x: grid.table[0], y: grid.table[1], width: 952, height: 32, fill: '#ffffff', stroke: '#e7ebf2', radius: 0, parts: [
  { layer: 'Name', property: 'Name', default: '名称 ↑', x: 44, y: 0, width: 380, height: 32, size: 12, color: C.accentText, weight: 'SemiBold' },
  { layer: 'Tags', property: 'Tags', default: '标签', x: 464, y: 0, width: 132, height: 32, size: 11, color: C.muted, weight: 'SemiBold' },
  { layer: 'Type', property: 'Type', default: '类型', x: 632, y: 0, width: 120, height: 32, size: 11, color: C.muted, weight: 'SemiBold' },
  { layer: 'Size', property: 'Size', default: '大小', x: 752, y: 0, width: 80, height: 32, size: 11, color: C.muted, weight: 'SemiBold' },
  { layer: 'Modified', property: 'Modified', default: '修改时间', x: 832, y: 0, width: 104, height: 32, size: 11, color: C.muted, weight: 'SemiBold', align: 'right' }
] })

function fileRow(name, x, y, fill) {
  return component({ name, x, y, width: 952, height: 32, fill, parts: [
    { layer: 'Favorite', property: 'Favorite', default: '☆', x: 9, y: 0, width: 20, height: 32, size: 15, color: '#b9c4d3', align: 'center' },
    { layer: 'File icon', property: 'Icon', default: '▱', x: 32, y: 0, width: 24, height: 32, size: 16, color: C.amber, align: 'center' },
    { layer: 'File name', property: 'Name', default: 'Design Assets', x: 62, y: 0, width: 386, height: 32, size: 12, color: C.text, weight: 'Medium' },
    { layer: 'Tags', property: 'Tags', default: '', x: 464, y: 0, width: 132, height: 32, size: 10, color: C.accentText },
    { layer: 'File type', property: 'Type', default: '文件夹', x: 632, y: 0, width: 120, height: 32, size: 11, color: C.muted },
    { layer: 'File size', property: 'Size', default: '—', x: 752, y: 0, width: 80, height: 32, size: 11, color: C.muted },
    { layer: 'Modified time', property: 'Modified', default: '今天 14:32', x: 832, y: 0, width: 104, height: 32, size: 10, color: C.faint, align: 'right' },
    { type: 'shape', layer: '行底分隔线', x: 0, y: 31, width: 952, height: 1, fill: C.softBorder }
  ] })
}
comps.fileRow = fileRow('数据 / 文件行', ...grid.file, '#ffffff')
comps.fileRowSelected = fileRow('数据 / 文件行选中', ...grid.selectedFile, C.selected)
comps.infoPair = component({ name: '属性 / 标签值行', x: grid.info[0], y: grid.info[1], width: 274, height: 23, fill: 'none', parts: [
  { layer: 'Property', property: 'Property', default: '当前目录', x: 0, y: 0, width: 128, height: 23, size: 11, color: C.faint },
  { layer: 'Value', property: 'Value', default: 'C:\\Users\\User', x: 130, y: 0, width: 144, height: 23, size: 11, color: C.text, align: 'right' }
] })
comps.logRow = component({ name: '控制台 / 日志行', x: grid.log[0], y: grid.log[1], width: 952, height: 26, fill: 'none', parts: [
  { layer: 'Time', property: 'Time', default: '18:42:30.447', x: 10, y: 0, width: 110, height: 26, size: 10, color: C.faint },
  { layer: 'Level', property: 'Level', default: 'INFO', x: 124, y: 0, width: 46, height: 26, size: 10, color: C.accent, weight: 'SemiBold' },
  { layer: 'Source', property: 'Source', default: 'Workbench', x: 176, y: 0, width: 86, height: 26, size: 10, color: C.text, weight: 'Medium' },
  { layer: 'Message', property: 'Message', default: '工作台界面已就绪', x: 270, y: 0, width: 660, height: 26, size: 10, color: C.text }
] })
comps.pill = component({ name: '状态 / 控制台筛选胶囊', x: 1040, y: 756, width: 64, height: 28, fill: C.accent, radius: 14, parts: [{ layer: 'Label', property: 'Label', default: '信息 10', x: 4, y: 0, width: 56, height: 28, size: 10, color: '#ffffff', weight: 'SemiBold', align: 'center' }] })
comps.status = component({ name: '状态 / 底栏文字', x: grid.status[0], y: grid.status[1], width: 220, height: 24, fill: 'none', parts: [
  { layer: 'Label', property: 'Label', default: '核心引擎就绪', x: 0, y: 0, width: 220, height: 24, size: 10, color: C.muted }
] })

// Component page labels and preview descriptions are documentation only; the controls above are the editable main components.
text('componentsRoot', '组件库总标题', 'DeskSuite · 通用界面组件', 58, 42, 640, 42, 24, C.ink, 'Bold')
text('componentsRoot', '组件库说明', '统一颜色、圆角、字体与控件尺寸；主工作台通过组件实例拼装。', 60, 84, 720, 28, 13, C.muted)
for (const [title, y, width, height] of [['基础交互', 124, 1500, 188], ['导航与侧栏', 326, 1500, 170], ['列表与状态', 510, 1500, 446]]) {
  box('componentsRoot', `${title} 分区背景`, 48, y, width, height, '#ffffff', 14, '#e7ebf2')
  text('componentsRoot', `${title} 分区标题`, title, 68, y + 10, 300, 26, 13, C.ink, 'SemiBold')
}
for (const [name, x, y, caption] of [
  ['Primary button', 58, 190, '主操作按钮'], ['Secondary button', 212, 190, '次操作按钮'], ['Quiet menu', 366, 190, '静默菜单'], ['Icon button', 520, 190, '图标按钮'], ['Select', 590, 190, '下拉选择'], ['Search', 764, 190, '搜索输入框'], ['Selected tab', 1010, 190, '选中页签'], ['Default tab', 1120, 190, '默认页签'],
  ['Primary header action', 58, 260, '顶栏操作按钮'], ['Wide secondary action', 212, 260, '宽版次操作按钮'], ['Compact secondary action', 460, 260, '紧凑次操作按钮'], ['Ghost icon', 604, 260, '静默图标按钮'], ['Selected icon', 650, 260, '选中图标按钮'], ['Medium select', 698, 260, '中版选择框'], ['Small select', 842, 260, '紧凑选择框'], ['Compact select', 966, 260, '窄版选择框'], ['Top search', 1284, 190, '顶栏搜索框'], ['Brand', 1284, 260, '品牌标识'],
  ['Activity selected', 58, 402, '活动项选中'], ['Activity default', 126, 402, '活动项默认'], ['Quick link', 210, 402, '快捷入口'], ['Section header', 500, 402, '分区标题'], ['Drive row', 760, 402, '驱动器条目'], ['Badge', 1020, 402, '数字徽标'], ['Checkbox', 1100, 402, '复选框'],
  ['File header', 58, 544, '文件列表表头'], ['File row component', 1020, 619, '文件列表行'], ['Selected file row', 1020, 657, '选中文件行'], ['Info pair', 360, 727, '属性行'], ['Address bar', 976, 727, '路径地址栏'], ['Log row', 1020, 777, '控制台日志行'], ['Status item', 300, 827, '状态栏文字']
]) text('componentsRoot', `${caption} 组件说明`, caption, x, y - 19, name.includes('File row') ? 200 : 150, 18, 10, C.faint)

function componentPreview(comp, name, x, y, properties = {}) {
  const preview = id('p')
  add('instance.create', { component: ref(comp), x, y, parent: ref('componentsRoot') }, preview)
  if (Object.keys(properties).length) add('instance.setProperties', { ids: [ref(preview)], properties })
  add('node.set', { ids: [ref(preview)], name: `预览 / ${name}` })
}
[
  [comps.primary, '主操作按钮', 58, 205], [comps.secondary, '次操作按钮', 212, 205], [comps.quiet, '静默菜单', 366, 205], [comps.iconButton, '图标按钮', 520, 202],
  [comps.select, '下拉选择', 590, 205], [comps.search, '搜索输入框', 764, 205], [comps.tabOn, '选中页签', 1010, 207], [comps.tabOff, '默认页签', 1120, 207],
  [comps.headerAction, '顶栏操作按钮', 58, 274], [comps.secondaryWide, '宽版次操作按钮', 212, 274], [comps.secondaryCompact, '紧凑次操作按钮', 460, 274], [comps.ghostIcon, '静默图标按钮', 604, 274],
  [comps.activeIcon, '选中图标按钮', 650, 274], [comps.selectMedium, '中版选择框', 698, 274], [comps.selectSmall, '紧凑选择框', 842, 274], [comps.selectCompact, '窄版选择框', 966, 274], [comps.topSearch, '顶栏搜索框', 1284, 205], [comps.brand, '品牌标识', 1284, 274],
  [comps.activityOn, '活动项选中', 58, 416], [comps.activityOff, '活动项默认', 126, 416], [comps.quick, '快捷入口', 210, 416], [comps.section, '分区标题', 500, 416],
  [comps.drive, '驱动器条目', 760, 416], [comps.badge, '数字徽标', 1020, 416], [comps.checkbox, '复选框', 1100, 422],
  [comps.tableHeader, '文件列表表头', 58, 562], [comps.fileRow, '文件列表行', 58, 600], [comps.fileRowSelected, '选中文件行', 58, 638],
  [comps.infoPair, '属性行', 58, 708], [comps.address, '路径地址栏', 976, 708], [comps.logRow, '控制台日志行', 58, 758], [comps.status, '状态栏文字', 58, 808], [comps.pill, '控制台筛选胶囊', 150, 808]
].forEach(args => componentPreview(...args))

add('page.add', { name: '01 主工作台 · 组件化界面' }, 'workbenchPage')
add('node.create', { type: 'frame', name: 'DeskSuite 主工作台', x: 0, y: 0, width: 1600, height: 1000, props: { fill: C.canvas }, select: false }, 'workbenchRoot')

function instance(comp, parent, name, x, y, properties = {}) {
  const inst = id('i')
  add('instance.create', { component: ref(comp), x, y, parent: ref(parent) }, inst)
  if (Object.keys(properties).length) add('instance.setProperties', { ids: [ref(inst)], properties })
  if (name) add('node.set', { ids: [ref(inst)], name })
  return inst
}
function line(parent, name, x, y, width, color = C.border) {
  box(parent, name, x, y, width, 1, color)
}
function plainText(parent, name, value, x, y, width, height, size = 12, color = C.text, weight = 'Regular', align = 'left') {
  return text(parent, name, value, x, y, width, height, size, color, weight, align)
}

// Real, measured shell and splitter geometry from the running DeskSuite UI.
box('workbenchRoot', '标题栏背景', 0, 0, 1600, 44, '#ffffff')
line('workbenchRoot', '标题栏下边线', 0, 43, 1600)
box('workbenchRoot', '活动栏背景', 0, 44, 48, 924, C.subtle)
box('workbenchRoot', '左侧栏背景', 48, 44, 268, 924, '#ffffff')
box('workbenchRoot', '左侧面板分隔条', 316, 44, 6, 924, '#e2e8f0')
box('workbenchRoot', '中央工作区背景', 322, 44, 952, 698, C.canvas)
box('workbenchRoot', '右侧栏背景', 1280, 44, 320, 924, '#ffffff')
box('workbenchRoot', '右侧面板分隔条', 1274, 44, 6, 924, '#e2e8f0')
box('workbenchRoot', '底部状态栏背景', 0, 968, 1600, 32, '#ffffff')
line('workbenchRoot', '底部状态栏上边线', 0, 968, 1600)

// Header / brand, app menus and window actions.
instance(comps.brand, 'workbenchRoot', 'DeskSuite 品牌容器', 12, 6, { Label: 'DeskSuite', Glyph: '▱' })
box('workbenchRoot', '品牌分隔', 122, 10, 1, 24, C.border)
for (const [i, label] of ['文件(F)', '编辑(E)', '视图(V)', '插件(P)', '帮助(H)'].entries()) instance(comps.quiet, 'workbenchRoot', `菜单 ${label}`, 131 + i * 60, 10, { Label: label })
instance(comps.ghostIcon, 'workbenchRoot', '全局搜索按钮', 1108, 6, { Glyph: '⌕' })
instance(comps.ghostIcon, 'workbenchRoot', '更新按钮', 1144, 6, { Glyph: '↓' })
instance(comps.headerAction, 'workbenchRoot', '悬浮面板入口', 1184, 9, { Label: '☷  悬浮面板' })
instance(comps.iconButton, 'workbenchRoot', '重置窗口布局按钮', 1286, 6, { Glyph: '↶' })
instance(comps.ghostIcon, 'workbenchRoot', '左侧栏布局按钮', 1322, 6, { Glyph: '◧' })
instance(comps.ghostIcon, 'workbenchRoot', '底栏布局按钮', 1358, 6, { Glyph: '▤' })
instance(comps.ghostIcon, 'workbenchRoot', '右侧栏布局按钮', 1394, 6, { Glyph: '◨' })
instance(comps.ghostIcon, 'workbenchRoot', '外观主题按钮', 1440, 6, { Glyph: '☾' })
instance(comps.ghostIcon, 'workbenchRoot', '窗口最小化', 1492, 6, { Glyph: '−' })
instance(comps.ghostIcon, 'workbenchRoot', '窗口最大化', 1532, 6, { Glyph: '□' })
instance(comps.ghostIcon, 'workbenchRoot', '窗口关闭', 1572, 6, { Glyph: '×' })

// Activity rail uses one selected and one default component for every entry.
const activities = [['▱', '文件'], ['▥', '统计'], ['▣', '暂存'], ['›_', '控制台'], ['▦', '白板'], ['⌁', '资源'], ['▤', '笔记'], ['▧', '剪贴板'], ['▣', '启动台'], ['▣', '工程资料箱']]
activities.forEach(([icon, label], index) => instance(label === '文件' ? comps.activityOn : comps.activityOff, 'workbenchRoot', `活动项 ${label}`, 2, 49 + index * 42, { Icon: icon, Label: label }))
instance(comps.activityOff, 'workbenchRoot', '活动项 设置', 2, 916, { Icon: '⚙', Label: '设置' })
box('workbenchRoot', '活动栏右分隔', 47, 44, 1, 924, C.border)

// Left navigation panel.
instance(comps.tabOn, 'workbenchRoot', '左侧页签 资源管理', 60, 52, { Label: '资源管理' })
instance(comps.tabOff, 'workbenchRoot', '左侧页签 标签', 160, 52, { Label: '◇ 标签' })
instance(comps.ghostIcon, 'workbenchRoot', '折叠左侧面板', 278, 49, { Glyph: '‹' })
line('workbenchRoot', '左侧页签下边线', 48, 84, 268)
instance(comps.section, 'workbenchRoot', '快速访问分区标题', 60, 93, { Title: '快速访问', Action: '⟳' })
const quickLinks = [['⌂', '主目录'], ['▱', '桌面'], ['▤', '文档'], ['↓', '下载'], ['▧', '图片']]
quickLinks.forEach(([icon, label], index) => instance(comps.quick, 'workbenchRoot', `快捷入口 ${label}`, 60, 129 + index * 32, { Icon: icon, Label: label }))
line('workbenchRoot', '快捷入口分隔线', 62, 295, 242, '#edf0f4')
instance(comps.section, 'workbenchRoot', '驱动器分区标题', 60, 304, { Title: '驱动器', Action: '⠿' })
const drives = [['C:', '55.6 GB 可用', '高'], ['D:', '138 GB 可用', '高'], ['E:', '3.1 TB 可用', '低'], ['F:', '595 GB 可用', '中'], ['V:', '3.5 TB 可用', '较低'], ['W:', '3.5 TB 可用', '较低'], ['X:', '3.5 TB 可用', '较低'], ['Y:', '3.5 TB 可用', '较低'], ['Z:', '3.5 TB 可用', '较低']]
drives.forEach(([drive, free, capacity], index) => {
  const y = 337 + index * 43
  instance(comps.drive, 'workbenchRoot', `驱动器 ${drive}`, 60, y, { 容量: capacity, Drive: `▱  ${drive}`, Available: free })
})
line('workbenchRoot', '驱动器与收藏分隔线', 62, 730, 242, '#edf0f4')
instance(comps.section, 'workbenchRoot', '快捷收藏标题', 60, 738, { Title: '快捷收藏', Action: '＋' })
plainText('workbenchRoot', '收藏说明', '选中文件夹后，点击分组 ＋ 收藏', 64, 772, 230, 26, 10, C.faint)
plainText('workbenchRoot', '收藏分组', '⌄  常用  0', 64, 809, 180, 26, 11, C.text, 'SemiBold')
plainText('workbenchRoot', '暂无收藏提示', '暂无收藏，选中文件夹后点击 ＋', 64, 843, 230, 24, 10, C.faint)
instance(comps.secondaryWide, 'workbenchRoot', '新建收藏分组按钮', 64, 884, { Label: '＋  新建分组' })

// Workspace path bar, filter controls and file table.
const toolbarY = 44
;[['‹', 332], ['›', 368], ['↑', 404], ['⟳', 440], ['▱', 476]].forEach(([glyph, x], index) => instance(comps.ghostIcon, 'workbenchRoot', `路径导航按钮 ${index + 1}`, x, toolbarY + 8, { Glyph: glyph }))
instance(comps.address, 'workbenchRoot', '路径地址输入框', 518, 52, { Path: '▱   C:   ›   Users   ›   User' })
instance(comps.topSearch, 'workbenchRoot', '当前目录搜索框', 1080, 52, { Placeholder: '在当前目录搜索' })
line('workbenchRoot', '路径栏下边线', 322, 91, 952, '#e7ebf2')

const filterTop = 94
plainText('workbenchRoot', '工作区字段标题', '工作区', 334, filterTop, 42, 34, 11, C.muted, 'Medium')
instance(comps.selectMedium, 'workbenchRoot', '工作区选择器', 372, filterTop + 1, { Value: '', Chevron: '⌄' })
instance(comps.selectCompact, 'workbenchRoot', '布局选择器', 504, filterTop + 1, { Value: '单栏', Chevron: '⌄' })
instance(comps.secondaryCompact, 'workbenchRoot', '新建项目按钮', 592, filterTop + 1, { Label: '＋ 新建' })
instance(comps.badge, 'workbenchRoot', '当前布局数量', 670, filterTop + 7, { Label: '1' })
instance(comps.selectSmall, 'workbenchRoot', '文件类型筛选', 704, filterTop + 1, { Value: '全部类型' })
instance(comps.selectSmall, 'workbenchRoot', '评分筛选', 820, filterTop + 1, { Value: '全部评分' })
instance(comps.ghostIcon, 'workbenchRoot', '收藏筛选按钮', 932, filterTop + 1, { Glyph: '☆' })
instance(comps.selectSmall, 'workbenchRoot', '排序方式', 966, filterTop + 1, { Value: '按名称' })
instance(comps.ghostIcon, 'workbenchRoot', '排序方向', 1082, filterTop + 1, { Glyph: '↑' })
instance(comps.activeIcon, 'workbenchRoot', '列表视图选中', 1118, filterTop + 1, { Glyph: '☷' })
instance(comps.ghostIcon, 'workbenchRoot', '网格视图', 1154, filterTop + 1, { Glyph: '▦' })
instance(comps.ghostIcon, 'workbenchRoot', '紧凑视图', 1190, filterTop + 1, { Glyph: '▤' })

const tableY = 132
instance(comps.tableHeader, 'workbenchRoot', '文件列表表头', 322, tableY)
instance(comps.checkbox, 'workbenchRoot', '全选复选框', 334, tableY + 8)
const rows = [
  ['▱', 'Applications', '', '文件夹', '—', '今天 18:22'],
  ['▱', 'Desktop', '', '文件夹', '—', '今天 16:05'],
  ['▱', 'Documents', '', '文件夹', '—', '今天 15:48'],
  ['▱', 'Downloads', '', '文件夹', '—', '昨天 21:13'],
  ['▱', 'Design Projects', '项目', '文件夹', '—', '昨天 19:37'],
  ['▱', 'Pictures', '', '文件夹', '—', '10 月 28 日'],
  ['▤', 'Design brief.md', '', 'Markdown', '8 KB', '10 月 28 日'],
  ['▧', 'Workspace preview.png', '', 'PNG 图像', '640 KB', '10 月 27 日'],
  ['▤', 'Project notes.md', '', 'Markdown', '12 KB', '10 月 26 日'],
  ['▱', 'Shared Resources', '', '文件夹', '—', '10 月 25 日'],
  ['▱', 'WorkCrate', '', '文件夹', '—', '10 月 24 日'],
  ['▱', 'Whiteboard Scenes', '', '文件夹', '—', '10 月 23 日'],
  ['▤', 'readme.txt', '', '文本文件', '3 KB', '10 月 22 日'],
  ['▱', 'Components', '', '文件夹', '—', '10 月 21 日'],
  ['▱', 'FigCraft', '', '文件夹', '—', '10 月 20 日'],
  ['▱', 'Notes', '', '文件夹', '—', '10 月 19 日'],
  ['▱', 'Resources', '', '文件夹', '—', '10 月 18 日'],
  ['▤', 'Settings.json', '', 'JSON 文件', '2 KB', '10 月 17 日']
]
rows.forEach((row, index) => {
  const values = { Icon: row[0], Name: row[1], Tags: row[2], Type: row[3], Size: row[4], Modified: row[5] }
  instance(index === 4 ? comps.fileRowSelected : comps.fileRow, 'workbenchRoot', `文件列表行 ${index + 1}`, 322, 164 + index * 32, values)
})

// Right property sidebar.
box('workbenchRoot', '右侧页签栏', 1280, 44, 320, 42, '#ffffff')
line('workbenchRoot', '右侧页签分隔线', 1280, 85, 320)
instance(comps.tabOn, 'workbenchRoot', '属性信息页签', 1292, 51, { Label: 'ⓘ  属性信息' })
instance(comps.tabOff, 'workbenchRoot', '版本历史页签', 1390, 51, { Label: '◷  版本历史' })
instance(comps.ghostIcon, 'workbenchRoot', '右侧折叠按钮', 1564, 48, { Glyph: '›' })
box('workbenchRoot', '右侧属性内容背景', 1280, 86, 320, 882, '#fafbfd')
plainText('workbenchRoot', '未选择条目标题', '▱  未选择条目', 1292, 98, 280, 28, 13, C.ink, 'SemiBold')
box('workbenchRoot', '目录概况卡片', 1292, 126, 296, 106, '#ffffff', 9, '#e7e8f1')
instance(comps.infoPair, 'workbenchRoot', '当前目录路径信息', 1304, 132, { Property: '当前目录', Value: 'C:\\Users\\User' })
instance(comps.infoPair, 'workbenchRoot', '条目总数信息', 1304, 155, { Property: '条目总数', Value: '167' })
instance(comps.infoPair, 'workbenchRoot', '文件夹数量信息', 1304, 178, { Property: '文件夹', Value: '126' })
instance(comps.infoPair, 'workbenchRoot', '文件数量信息', 1304, 201, { Property: '文件', Value: '41' })
plainText('workbenchRoot', '右侧属性提示', '在文件列表中选择条目以查看属性、元数据与内容预览；按住 Ctrl 或 Shift 可多选。', 1292, 242, 296, 40, 10, C.faint)

// Bottom console and status bar.
box('workbenchRoot', '调试控制台背景', 322, 742, 952, 226, '#ffffff', 0, '#dfe5ed')
box('workbenchRoot', '控制台标题栏背景', 322, 743, 952, 42, '#fafbfd')
line('workbenchRoot', '控制台标题栏分隔线', 322, 784, 952)
instance(comps.tabOn, 'workbenchRoot', '调试控制台页签', 334, 750, { Label: '›_  调试控制台' })
instance(comps.ghostIcon, 'workbenchRoot', '复制日志', 1040, 748, { Glyph: '▢' })
instance(comps.ghostIcon, 'workbenchRoot', '导出日志', 1080, 748, { Glyph: '↓' })
instance(comps.ghostIcon, 'workbenchRoot', '清空日志', 1120, 748, { Glyph: '⌫' })
instance(comps.ghostIcon, 'workbenchRoot', '收起控制台', 1234, 748, { Glyph: '⌄' })
const pillData = [['信息 10', 334], ['警告 0', 406], ['错误 2', 478], ['事件 12', 550], ['启动 10', 622]]
pillData.forEach(([label, x]) => instance(comps.pill, 'workbenchRoot', `日志筛选 ${label}`, x, 792, { Label: label }))
instance(comps.search, 'workbenchRoot', '日志搜索框', 994, 792, { Placeholder: '搜索日志、来源或数据…' })
plainText('workbenchRoot', '日志条数', '34/34', 1216, 792, 48, 28, 10, C.faint, 'Medium', 'right')
const logs = [
  ['18:42:48.797', 'EVENT', 'MCP', '调用工具 capture_window'],
  ['18:42:30.447', 'INFO', 'Workbench', '工作台界面已就绪'],
  ['18:42:04.552', 'INFO', 'Explorer', '已加载当前目录条目'],
  ['18:41:56.765', 'BOOT', 'Runtime', '主进程服务已就绪']
]
logs.forEach((entry, index) => instance(comps.logRow, 'workbenchRoot', `运行日志 ${index + 1}`, 322, 828 + index * 27, { Time: entry[0], Level: entry[1], Source: entry[2], Message: entry[3] }))
box('workbenchRoot', '状态栏运行指示点', 14, 980, 8, 8, '#61c692', 4)
instance(comps.status, 'workbenchRoot', '引擎状态', 28, 972, { Label: '核心引擎就绪' })
plainText('workbenchRoot', '状态栏目录', '▱  C:\\Users\\User    126 个文件夹 / 41 个文件    共 52.6 MB', 152, 972, 500, 24, 10, C.muted)
plainText('workbenchRoot', '虚拟滚动状态', 'ϟ 虚拟滚动', 658, 972, 110, 24, 10, C.amber, 'Medium')
plainText('workbenchRoot', '状态栏日志入口', '›_  34       ◉  2', 1480, 972, 104, 24, 10, C.muted, 'Medium', 'right')

// Replace the existing componentized pages by name while retaining the other
// reference pages. Resolve IDs from the source file because FigCraft assigns
// fresh page IDs whenever a document is saved.
const info = spawnSync(cli, ['info', source], { encoding: 'utf8', windowsHide: true, maxBuffer: 16 * 1024 * 1024 })
if (info.status !== 0) throw new Error(`Could not inspect source pages: ${info.stderr || info.stdout}`)
for (const line of (info.stdout || '').split(/\r?\n/)) {
  const match = line.match(/^page (\d+) "(?:00 通用组件库|01 主工作台 · 组件化界面)"/)
  if (match) add('page.delete', { id: Number(match[1]) })
}
add('page.move', { id: ref('componentsPage'), index: 0 })
add('page.move', { id: ref('workbenchPage'), index: 1 })
add('page.select', { id: ref('workbenchPage') })

mkdirSync(dirname(output), { recursive: true })
writeFileSync(planPath, JSON.stringify(steps, null, 2), 'utf8')
const result = spawnSync(cli, ['run', planPath, '--in', source, '--out', output], { encoding: 'utf8', windowsHide: true, maxBuffer: 64 * 1024 * 1024 })
if (result.status !== 0) {
  if (result.stdout) process.stdout.write(result.stdout)
  if (result.stderr) process.stderr.write(result.stderr)
  process.exit(result.status ?? 1)
}
process.stdout.write((result.stdout || '').split(/\r?\n/).filter(Boolean).slice(-8).join('\n') + '\n')
unlinkSync(planPath)
console.log(`Saved ${output}`)

