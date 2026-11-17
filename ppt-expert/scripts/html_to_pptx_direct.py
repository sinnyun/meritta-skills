#!/usr/bin/env python3
"""
PPT Expert - HTML → PPTX 直接解析脚本 (Python 版)
读取微调后的 HTML，解析内容和样式，用 python-pptx 生成 PPTX
保留用户在 HTML 上的文本和样式微调，不依赖 puppeteer

依赖: pip install beautifulsoup4 python-pptx
"""

import sys
import re
import argparse
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("缺少 beautifulsoup4，请运行: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    print("缺少 python-pptx，请运行: pip install python-pptx", file=sys.stderr)
    sys.exit(1)


# ─── 工具函数 ───

def strip_hex(c):
    """去掉 # 前缀"""
    if not c:
        return None
    return c.replace('#', '')


def px_to_pt(px):
    """px → pt 转换（96 DPI 下 1px = 0.75pt）"""
    return round(px * 0.75)


def hex_to_rgb(hex_color):
    """十六进制颜色 → RGBColor"""
    hex_color = hex_color.replace('#', '')
    return RGBColor(int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def parse_style(style_str):
    """解析内联 style 字符串"""
    if not style_str:
        return {}
    s = {}
    color_m = re.search(r'(?:^|;)\s*color\s*:\s*(#[0-9a-fA-F]{3,8})', style_str)
    if color_m:
        s['color'] = color_m.group(1)
    size_m = re.search(r'font-size\s*:\s*(\d+)px', style_str)
    if size_m:
        s['fontSize'] = int(size_m.group(1))
    weight_m = re.search(r'font-weight\s*:\s*(bold|\d+)', style_str)
    if weight_m:
        w = weight_m.group(1)
        s['bold'] = (w == 'bold' or int(w) >= 600)
    align_m = re.search(r'text-align\s*:\s*(left|center|right)', style_str)
    if align_m:
        s['align'] = align_m.group(1)
    return s


def has_radial_gradient(style_str):
    """检查元素是否有 radial-gradient 背景（装饰性光晕，应跳过）"""
    if not style_str:
        return False
    return bool(re.search(r'radial-gradient', style_str, re.IGNORECASE))


def is_decorative_glow(el):
    """检查元素或其祖先是否有 radial-gradient 背景（装饰性光晕，应跳过）

    向上遍历祖先链，直到遇到 section（幻灯片容器）为止。
    任何一层带有 radial-gradient 背景即视为装饰性光晕元素。
    """
    if el is None:
        return False
    # BeautifulSoup 的 Tag 才有 get 方法，NavigableString 没有
    if not hasattr(el, 'get'):
        return False
    current = el
    while current is not None and hasattr(current, 'get'):
        if has_radial_gradient(current.get('style')):
            return True
        parent = current.parent
        if parent is None:
            break
        # 到 section（幻灯片容器）层级停止，不跨幻灯片
        if hasattr(parent, 'name') and parent.name == 'section':
            break
        current = parent
    return False


def extract_theme(html):
    """从 HTML 的 <style> 块中提取 :root CSS 变量"""
    theme = {}
    for style_match in re.finditer(r'<style[^>]*>(.*?)</style>', html, re.DOTALL):
        css = style_match.group(1)
        root_m = re.search(r':root\s*\{([^}]+)\}', css)
        if root_m:
            vars_css = root_m.group(1)
            for var_m in re.finditer(r'--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})', vars_css):
                key, val = var_m.group(1), var_m.group(2)
                if key == 'primary':
                    theme['primary'] = val
                elif key == 'secondary':
                    theme['secondary'] = val
                elif key == 'accent':
                    theme['accent'] = val
                elif key == 'bg-light':
                    theme['bgLight'] = val
                elif key == 'text':
                    theme['text'] = val
                elif key == 'text-light':
                    theme['textLight'] = val
    # 默认值
    theme.setdefault('primary', '#1E2761')
    theme.setdefault('secondary', '#CADCFC')
    theme.setdefault('accent', '#FFFFFF')
    theme.setdefault('bgLight', '#FFFFFF')
    theme.setdefault('text', '#1E2761')
    theme.setdefault('textLight', '#6B7280')
    return theme


# ─── 样式辅助 ───

def get_color(styles, default_color):
    if styles and 'color' in styles:
        return styles['color']
    return default_color


def get_size(styles, default_size):
    if styles and 'fontSize' in styles:
        return px_to_pt(styles['fontSize'])
    return default_size


def get_bold(styles, default_bold):
    if styles and 'bold' in styles:
        return styles['bold']
    return default_bold


def get_align(styles, default_align):
    if styles and 'align' in styles:
        return styles['align']
    return default_align


# ─── HTML 解析 ───

def parse_html(html):
    """解析 HTML，返回 { palette, slides }"""
    soup = BeautifulSoup(html, 'html.parser')
    theme = extract_theme(html)

    palette = {k: strip_hex(v) for k, v in theme.items()}

    slides = []
    for slide_el in soup.find_all(class_='slide'):
        layout = slide_el.get('data-layout') or detect_layout(slide_el)
        data = extract_slide_data(slide_el, layout)
        slides.append({'layout': layout, 'data': data})

    return {'palette': palette, 'slides': slides}


def detect_layout(slide_el):
    """从结构推断布局类型"""
    classes = slide_el.get('class', [])
    if 'slide-cover' in classes:
        return 'cover'
    if 'slide-content' in classes:
        return 'content'
    if 'slide-end' in classes:
        return 'end'
    if slide_el.find(class_='metric'):
        return 'data'
    style = slide_el.get('style', '')
    if style and 'grid-template-columns' in style:
        return 'split'
    h3s = slide_el.find_all('h3')
    if len(h3s) > 2:
        return 'timeline'
    if len(h3s) == 2:
        return 'comparison'
    return 'content'


def extract_slide_data(slide_el, layout):
    """根据布局类型分发到对应的提取函数"""
    extractors = {
        'cover': extract_cover,
        'content': extract_content,
        'data': extract_data,
        'split': extract_split,
        'timeline': extract_timeline,
        'comparison': extract_comparison,
        'end': extract_end,
    }
    fn = extractors.get(layout, extract_content)
    return fn(slide_el)


def extract_cover(slide_el):
    h1 = slide_el.find('h1')
    # 若主标题处于装饰性光晕内，尝试找下一个不在光晕内的 h1
    if h1 and is_decorative_glow(h1):
        for alt in slide_el.find_all('h1'):
            if not is_decorative_glow(alt):
                h1 = alt
                break
    sub = slide_el.find(class_='subtitle')
    # 若副标题处于装饰性光晕内，置空避免提取光晕文字
    if sub and is_decorative_glow(sub):
        sub = None
    return {
        'title': h1.get_text(strip=True) if h1 else '',
        'titleStyles': parse_style(h1.get('style')) if h1 else {},
        'subtitle': sub.get_text(strip=True) if sub else '',
        'subtitleStyles': parse_style(sub.get('style')) if sub else {},
    }


def extract_content(slide_el):
    h2 = slide_el.find('h2')
    items = []
    for li in slide_el.find_all('li'):
        # 跳过装饰性光晕内的 li（含祖先链检查）
        if is_decorative_glow(li):
            continue
        items.append({
            'text': li.get_text(strip=True),
            'styles': parse_style(li.get('style'))
        })
    return {
        'title': h2.get_text(strip=True) if h2 else '',
        'titleStyles': parse_style(h2.get('style')) if h2 else {},
        'items': items
    }


def extract_data(slide_el):
    h2 = slide_el.find('h2')
    metrics = []
    for m in slide_el.find_all(class_='metric'):
        # 跳过装饰性光晕内的 metric
        if is_decorative_glow(m):
            continue
        val = m.find(class_='metric-value')
        label = m.find(class_='metric-label')
        metrics.append({
            'value': val.get_text(strip=True) if val else '',
            'label': label.get_text(strip=True) if label else '',
            'valueStyles': parse_style(val.get('style')) if val else {},
            'labelStyles': parse_style(label.get('style')) if label else {},
        })
    return {
        'title': h2.get_text(strip=True) if h2 else '',
        'titleStyles': parse_style(h2.get('style')) if h2 else {},
        'metrics': metrics
    }


def extract_split(slide_el):
    h2 = slide_el.find('h2')
    items = []
    for li in slide_el.find_all('li'):
        # 跳过装饰性光晕内的 li
        if is_decorative_glow(li):
            continue
        items.append({
            'text': li.get_text(strip=True),
            'styles': parse_style(li.get('style'))
        })
    return {
        'title': h2.get_text(strip=True) if h2 else '',
        'titleStyles': parse_style(h2.get('style')) if h2 else {},
        'items': items
    }


def extract_timeline(slide_el):
    h2 = slide_el.find('h2')
    steps = []
    for h3 in slide_el.find_all('h3'):
        # 跳过装饰性光晕内的 h3
        if is_decorative_glow(h3):
            continue
        step_div = h3.parent
        p = step_div.find('p')
        steps.append({
            'title': h3.get_text(strip=True),
            'desc': p.get_text(strip=True) if p else '',
            'titleStyles': parse_style(h3.get('style')),
            'descStyles': parse_style(p.get('style')) if p else {},
        })
    return {
        'title': h2.get_text(strip=True) if h2 else '',
        'titleStyles': parse_style(h2.get('style')) if h2 else {},
        'steps': steps
    }


def extract_comparison(slide_el):
    h2 = slide_el.find('h2')
    h3s = slide_el.find_all('h3')

    def extract_col(col_el):
        if not col_el:
            return {'title': '', 'titleStyles': {}, 'items': []}
        h3 = col_el.find('h3')
        items = []
        for li in col_el.find_all('li'):
            # 跳过装饰性光晕内的 li
            if is_decorative_glow(li):
                continue
            items.append({
                'text': li.get_text(strip=True),
                'styles': parse_style(li.get('style'))
            })
        return {
            'title': h3.get_text(strip=True) if h3 else '',
            'titleStyles': parse_style(h3.get('style')) if h3 else {},
            'items': items
        }

    left = extract_col(h3s[0].parent if len(h3s) > 0 else None)
    right = extract_col(h3s[1].parent if len(h3s) > 1 else None)

    return {
        'title': h2.get_text(strip=True) if h2 else '',
        'titleStyles': parse_style(h2.get('style')) if h2 else {},
        'left': left,
        'right': right
    }


def extract_end(slide_el):
    h2 = slide_el.find('h2')
    # 若主标题处于装饰性光晕内，尝试找下一个不在光晕内的 h2
    if h2 and is_decorative_glow(h2):
        for alt in slide_el.find_all('h2'):
            if not is_decorative_glow(alt):
                h2 = alt
                break
    p = slide_el.find('p')
    # 若副标题处于装饰性光晕内，尝试找下一个不在光晕内的 p
    if p and is_decorative_glow(p):
        for alt in slide_el.find_all('p'):
            if not is_decorative_glow(alt):
                p = alt
                break
        else:
            p = None
    return {
        'title': h2.get_text(strip=True) if h2 else '',
        'titleStyles': parse_style(h2.get('style')) if h2 else {},
        'subtitle': p.get_text(strip=True) if p else '',
        'subtitleStyles': parse_style(p.get('style')) if p else {},
    }


# ─── PPTX 元素辅助 ───

def add_textbox(slide, x, y, w, h, text, font_size, bold, color, align='left', valign='top'):
    txBox = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    p.font.size = Pt(font_size)
    p.font.bold = bold
    p.font.color.rgb = hex_to_rgb(color)
    p.font.name = 'Geist'
    if align == 'center':
        p.alignment = PP_ALIGN.CENTER
    elif align == 'right':
        p.alignment = PP_ALIGN.RIGHT
    if valign == 'middle':
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    return txBox


def add_bullet_list(slide, x, y, w, h, items, palette):
    """添加要点列表（支持每项独立样式）"""
    txBox = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item['text']
        opts = item.get('options', {})
        p.font.size = Pt(opts.get('fontSize', 18))
        p.font.color.rgb = hex_to_rgb(opts.get('color', palette['text']))
        p.font.bold = opts.get('bold', False)
        p.font.name = 'Geist'
        p.space_after = Pt(opts.get('paraSpaceAfter', 12))
    return txBox


def add_rect(slide, x, y, w, h, fill_color):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_color)
    shape.line.fill.background()
    return shape


def add_rounded_rect(slide, x, y, w, h, fill_color, line_color=None, line_width=0):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_color)
    if line_color:
        shape.line.color.rgb = hex_to_rgb(line_color)
        shape.line.width = Pt(line_width)
    else:
        shape.line.fill.background()
    return shape


def add_ellipse(slide, x, y, w, h, fill_color):
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_color)
    shape.line.fill.background()
    return shape


def set_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(color)


# ─── PPTX 布局生成器（样式感知）───

def layout_cover(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_rect(slide, 8.5, 0, 4.83, 7.5, palette['primary'])
    add_textbox(slide, 0.8, 2.2, 7.2, 2.0, data.get('title', '演示文稿'),
                get_size(data.get('titleStyles'), 44), get_bold(data.get('titleStyles'), True),
                get_color(data.get('titleStyles'), palette['primary']), valign='middle')
    add_textbox(slide, 0.8, 4.3, 7.2, 0.8, data.get('subtitle', ''),
                get_size(data.get('subtitleStyles'), 20), False,
                get_color(data.get('subtitleStyles'), palette['textLight']))


def layout_content(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_textbox(slide, 0.8, 0.5, 11.73, 1.0, data.get('title', ''),
                get_size(data.get('titleStyles'), 32), get_bold(data.get('titleStyles'), True),
                get_color(data.get('titleStyles'), palette['primary']),
                align=get_align(data.get('titleStyles'), 'left'), valign='middle')
    items = []
    for item in data.get('items', []):
        items.append({
            'text': item['text'],
            'options': {
                'fontSize': get_size(item.get('styles'), 18),
                'color': get_color(item.get('styles'), palette['text']),
                'bold': get_bold(item.get('styles'), False),
                'paraSpaceAfter': 12
            }
        })
    if items:
        add_bullet_list(slide, 0.8, 1.8, 11.73, 5.0, items, palette)


def layout_data(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_textbox(slide, 0.8, 0.5, 11.73, 1.0, data.get('title', ''),
                get_size(data.get('titleStyles'), 32), get_bold(data.get('titleStyles'), True),
                get_color(data.get('titleStyles'), palette['primary']),
                align=get_align(data.get('titleStyles'), 'left'), valign='middle')
    metrics = data.get('metrics', [])
    card_w = 3.5
    gap = 0.4
    total_w = len(metrics) * card_w + (len(metrics) - 1) * gap
    start_x = (13.33 - total_w) / 2
    for i, m in enumerate(metrics):
        x = start_x + i * (card_w + gap)
        add_rounded_rect(slide, x, 2.2, card_w, 3.5, palette['bgLight'], palette['secondary'], 2)
        add_textbox(slide, x, 2.6, card_w, 1.5, m.get('value', ''),
                    get_size(m.get('valueStyles'), 40), get_bold(m.get('valueStyles'), True),
                    get_color(m.get('valueStyles'), palette['primary']),
                    align='center', valign='middle')
        add_textbox(slide, x, 4.2, card_w, 0.8, m.get('label', ''),
                    get_size(m.get('labelStyles'), 16), False,
                    get_color(m.get('labelStyles'), palette['textLight']), align='center')


def layout_split(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_rounded_rect(slide, 6.67, 1.0, 5.87, 5.5, palette['secondary'])
    add_textbox(slide, 0.8, 1.0, 5.5, 1.2, data.get('title', ''),
                get_size(data.get('titleStyles'), 28), get_bold(data.get('titleStyles'), True),
                get_color(data.get('titleStyles'), palette['primary']), valign='middle')
    items = []
    for item in data.get('items', []):
        items.append({
            'text': item['text'],
            'options': {
                'fontSize': get_size(item.get('styles'), 16),
                'color': get_color(item.get('styles'), palette['text']),
                'bold': get_bold(item.get('styles'), False),
                'paraSpaceAfter': 10
            }
        })
    if items:
        add_bullet_list(slide, 0.8, 2.5, 5.5, 4.0, items, palette)


def layout_timeline(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_textbox(slide, 0.8, 0.5, 11.73, 1.0, data.get('title', ''),
                get_size(data.get('titleStyles'), 32), get_bold(data.get('titleStyles'), True),
                get_color(data.get('titleStyles'), palette['primary']),
                align=get_align(data.get('titleStyles'), 'center'), valign='middle')
    steps = data.get('steps', [])
    step_w = 11.0 / max(len(steps), 1)
    for i, step in enumerate(steps):
        cx = 1.16 + i * step_w + step_w / 2
        add_ellipse(slide, cx - 0.3, 2.7, 0.6, 0.6, palette['primary'])
        add_textbox(slide, cx - 0.3, 2.7, 0.6, 0.6, str(i + 1), 14, True, 'FFFFFF',
                    align='center', valign='middle')
        add_textbox(slide, cx - step_w / 2 + 0.1, 3.6, step_w - 0.2, 0.6, step.get('title', ''),
                    get_size(step.get('titleStyles'), 18), get_bold(step.get('titleStyles'), True),
                    get_color(step.get('titleStyles'), palette['primary']), align='center')
        add_textbox(slide, cx - step_w / 2 + 0.1, 4.3, step_w - 0.2, 1.5, step.get('desc', ''),
                    get_size(step.get('descStyles'), 14), False,
                    get_color(step.get('descStyles'), palette['textLight']), align='center')


def layout_comparison(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_textbox(slide, 0.8, 0.5, 11.73, 1.0, data.get('title', ''),
                get_size(data.get('titleStyles'), 32), get_bold(data.get('titleStyles'), True),
                get_color(data.get('titleStyles'), palette['primary']),
                align=get_align(data.get('titleStyles'), 'center'), valign='middle')
    left = data.get('left', {})
    right = data.get('right', {})
    col_w = 5.5
    gap = 0.33
    start_x = (13.33 - col_w * 2 - gap) / 2

    # 左侧
    add_rounded_rect(slide, start_x, 1.8, col_w, 5.0, 'F9FAFB', palette['secondary'], 1)
    add_textbox(slide, start_x, 2.0, col_w, 0.8, left.get('title', ''),
                get_size(left.get('titleStyles'), 22), get_bold(left.get('titleStyles'), True),
                get_color(left.get('titleStyles'), palette['primary']), align='center', valign='middle')
    left_items = []
    for item in left.get('items', []):
        left_items.append({
            'text': item['text'],
            'options': {
                'fontSize': get_size(item.get('styles'), 16),
                'color': get_color(item.get('styles'), palette['text']),
                'bold': get_bold(item.get('styles'), False),
                'paraSpaceAfter': 10
            }
        })
    if left_items:
        add_bullet_list(slide, start_x + 0.3, 3.0, col_w - 0.6, 3.5, left_items, palette)

    # 右侧
    right_x = start_x + col_w + gap
    add_rounded_rect(slide, right_x, 1.8, col_w, 5.0, palette['bgLight'], palette['primary'], 2)
    add_textbox(slide, right_x, 2.0, col_w, 0.8, right.get('title', ''),
                get_size(right.get('titleStyles'), 22), get_bold(right.get('titleStyles'), True),
                get_color(right.get('titleStyles'), palette['primary']), align='center', valign='middle')
    right_items = []
    for item in right.get('items', []):
        right_items.append({
            'text': item['text'],
            'options': {
                'fontSize': get_size(item.get('styles'), 16),
                'color': get_color(item.get('styles'), palette['text']),
                'bold': get_bold(item.get('styles'), False),
                'paraSpaceAfter': 10
            }
        })
    if right_items:
        add_bullet_list(slide, right_x + 0.3, 3.0, col_w - 0.6, 3.5, right_items, palette)


def layout_end(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_rect(slide, 0, 0, 13.33, 0.15, palette['primary'])
    add_textbox(slide, 0, 2.5, 13.33, 1.5, data.get('title', '谢谢'),
                get_size(data.get('titleStyles'), 48), get_bold(data.get('titleStyles'), True),
                get_color(data.get('titleStyles'), palette['primary']),
                align=get_align(data.get('titleStyles'), 'center'), valign='middle')
    add_textbox(slide, 0, 4.2, 13.33, 0.8, data.get('subtitle', ''),
                get_size(data.get('subtitleStyles'), 22), False,
                get_color(data.get('subtitleStyles'), palette['textLight']), align='center')


LAYOUTS = {
    'cover': layout_cover,
    'content': layout_content,
    'data': layout_data,
    'split': layout_split,
    'timeline': layout_timeline,
    'comparison': layout_comparison,
    'end': layout_end,
}


# ─── 主生成函数 ───

def html_to_pptx(html_file, output_file):
    html = Path(html_file).read_text(encoding='utf-8')
    parsed = parse_html(html)
    palette = parsed['palette']
    slides = parsed['slides']

    print(f"共 {len(slides)} 页幻灯片")

    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    for i, slide_info in enumerate(slides):
        print(f"处理第 {i + 1}/{len(slides)} 页...")
        slide = prs.slides.add_slide(blank_layout)
        layout_fn = LAYOUTS.get(slide_info['layout'], layout_content)
        layout_fn(slide, slide_info['data'], palette)

    prs.save(output_file)
    print(f"PPTX 已导出: {output_file}")
    return output_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HTML → PPTX 直接解析生成')
    parser.add_argument('--input', '-i', required=True, help='HTML 文件路径')
    parser.add_argument('--output', '-o', help='输出 PPTX 文件路径')
    args = parser.parse_args()

    output = args.output or args.input.replace('.html', '.pptx')
    html_to_pptx(args.input, output)
