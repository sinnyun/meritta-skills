#!/usr/bin/env python3
"""
PPT Expert - content.json → PPTX 直接生成脚本 (Python 版)
不依赖 puppeteer，直接用 python-pptx 构建原生 PPTX 元素
快速、准确、生成效果好

依赖: pip install python-pptx
"""

import sys
import json
import argparse
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
    from pptx.dml.color import RGBColor
    from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
    from pptx.enum.shapes import MSO_SHAPE
except ImportError:
    print("缺少 python-pptx，请运行: pip install python-pptx", file=sys.stderr)
    sys.exit(1)


# ─── 配色方案（与 generate_html.js 保持一致）───
COLOR_PALETTES = {
    'midnight-executive': {
        'primary': '1E2761', 'secondary': 'CADCFC',
        'accent': 'FFFFFF', 'bgLight': 'FFFFFF', 'text': '1E2761', 'textLight': '6B7280'
    },
    'tech-dark': {
        'primary': '58A6FF', 'secondary': '161B22',
        'accent': '58A6FF', 'bgLight': '0D1117', 'text': 'F0F6FC', 'textLight': '8B949E'
    },
    'coral-energy': {
        'primary': 'F96167', 'secondary': 'F9E795',
        'accent': '2F3C7E', 'bgLight': 'FFFFFF', 'text': '1F2937', 'textLight': '6B7280'
    },
    'warm-terracotta': {
        'primary': 'B85042', 'secondary': 'E7E8D1',
        'accent': 'A7BEAE', 'bgLight': 'FDFBF7', 'text': '3D3D3D', 'textLight': '6B7280'
    },
    'ocean-gradient': {
        'primary': '065A82', 'secondary': '1C7293',
        'accent': '21295C', 'bgLight': 'FFFFFF', 'text': '065A82', 'textLight': '6B7280'
    },
    'charcoal-minimal': {
        'primary': '36454F', 'secondary': 'F2F2F2',
        'accent': '212121', 'bgLight': 'FFFFFF', 'text': '36454F', 'textLight': '8B949E'
    },
    'teal-trust': {
        'primary': '028090', 'secondary': '00A896',
        'accent': '02C39A', 'bgLight': 'FFFFFF', 'text': '065A60', 'textLight': '374151'
    },
    'berry-cream': {
        'primary': '6D2E46', 'secondary': 'A26769',
        'accent': 'ECE2D0', 'bgLight': 'FFFFFF', 'text': '6D2E46', 'textLight': '8B949E'
    },
}


def hex_to_rgb(hex_color):
    """将十六进制颜色转为 RGBColor"""
    hex_color = hex_color.replace('#', '')
    return RGBColor(int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))


def add_textbox(slide, x, y, w, h, text, font_size, bold, color, align='left', valign='top'):
    """添加文本框"""
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


def add_bullet_list(slide, x, y, w, h, items, font_size, color):
    """添加要点列表"""
    txBox = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.text = item
        p.font.size = Pt(font_size)
        p.font.color.rgb = hex_to_rgb(color)
        p.font.name = 'Geist'
        p.space_after = Pt(12)
    return txBox


def add_rect(slide, x, y, w, h, fill_color, line_color=None, line_width=0):
    """添加矩形"""
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_color)
    if line_color:
        shape.line.color.rgb = hex_to_rgb(line_color)
        shape.line.width = Pt(line_width)
    else:
        shape.line.fill.background()
    return shape


def add_rounded_rect(slide, x, y, w, h, fill_color, line_color=None, line_width=0):
    """添加圆角矩形"""
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
    """添加椭圆"""
    shape = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = hex_to_rgb(fill_color)
    shape.line.fill.background()
    return shape


def set_bg(slide, color):
    """设置幻灯片背景"""
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = hex_to_rgb(color)


# ─── 布局生成器 ───

def layout_cover(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_rect(slide, 8.5, 0, 4.83, 7.5, palette['primary'])
    add_textbox(slide, 0.8, 2.2, 7.2, 2.0, data.get('title', '演示文稿'), 44, True, palette['primary'], valign='middle')
    add_textbox(slide, 0.8, 4.3, 7.2, 0.8, data.get('subtitle', ''), 20, False, palette['textLight'])


def layout_content(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_textbox(slide, 0.8, 0.5, 11.73, 1.0, data.get('title', ''), 32, True, palette['primary'], valign='middle')
    add_bullet_list(slide, 0.8, 1.8, 11.73, 5.0, data.get('items', []), 18, palette['text'])


def layout_data(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_textbox(slide, 0.8, 0.5, 11.73, 1.0, data.get('title', ''), 32, True, palette['primary'], valign='middle')
    metrics = data.get('metrics', [])
    card_width = 3.5
    gap = 0.4
    total_width = len(metrics) * card_width + (len(metrics) - 1) * gap
    start_x = (13.33 - total_width) / 2
    for i, m in enumerate(metrics):
        x = start_x + i * (card_width + gap)
        add_rounded_rect(slide, x, 2.2, card_width, 3.5, palette['bgLight'], palette['secondary'], 2)
        add_textbox(slide, x, 2.6, card_width, 1.5, m.get('value', ''), 40, True, palette['primary'], align='center', valign='middle')
        add_textbox(slide, x, 4.2, card_width, 0.8, m.get('label', ''), 16, False, palette['textLight'], align='center')


def layout_split(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_rounded_rect(slide, 6.67, 1.0, 5.87, 5.5, palette['secondary'])
    add_textbox(slide, 0.8, 1.0, 5.5, 1.2, data.get('title', ''), 28, True, palette['primary'], valign='middle')
    add_bullet_list(slide, 0.8, 2.5, 5.5, 4.0, data.get('items', []), 16, palette['text'])


def layout_timeline(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_textbox(slide, 0.8, 0.5, 11.73, 1.0, data.get('title', ''), 32, True, palette['primary'], align='center', valign='middle')
    steps = data.get('steps', [])
    step_width = 11.0 / max(len(steps), 1)
    for i, step in enumerate(steps):
        cx = 1.16 + i * step_width + step_width / 2
        add_ellipse(slide, cx - 0.3, 2.7, 0.6, 0.6, palette['primary'])
        add_textbox(slide, cx - 0.3, 2.7, 0.6, 0.6, str(i + 1), 14, True, 'FFFFFF', align='center', valign='middle')
        add_textbox(slide, cx - step_width / 2 + 0.1, 3.6, step_width - 0.2, 0.6, step.get('title', ''), 18, True, palette['primary'], align='center')
        add_textbox(slide, cx - step_width / 2 + 0.1, 4.3, step_width - 0.2, 1.5, step.get('desc', ''), 14, False, palette['textLight'], align='center')


def layout_comparison(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_textbox(slide, 0.8, 0.5, 11.73, 1.0, data.get('title', ''), 32, True, palette['primary'], align='center', valign='middle')
    col_width = 5.5
    gap = 0.33
    start_x = (13.33 - col_width * 2 - gap) / 2
    left = data.get('left', {})
    right = data.get('right', {})
    # 左侧
    add_rounded_rect(slide, start_x, 1.8, col_width, 5.0, 'F9FAFB', palette['secondary'], 1)
    add_textbox(slide, start_x, 2.0, col_width, 0.8, left.get('title', ''), 22, True, palette['primary'], align='center', valign='middle')
    add_bullet_list(slide, start_x + 0.3, 3.0, col_width - 0.6, 3.5, left.get('items', []), 16, palette['text'])
    # 右侧
    right_x = start_x + col_width + gap
    add_rounded_rect(slide, right_x, 1.8, col_width, 5.0, palette['bgLight'], palette['primary'], 2)
    add_textbox(slide, right_x, 2.0, col_width, 0.8, right.get('title', ''), 22, True, palette['primary'], align='center', valign='middle')
    add_bullet_list(slide, right_x + 0.3, 3.0, col_width - 0.6, 3.5, right.get('items', []), 16, palette['text'])


def layout_end(slide, data, palette):
    set_bg(slide, palette['bgLight'])
    add_rect(slide, 0, 0, 13.33, 0.15, palette['primary'])
    add_textbox(slide, 0, 2.5, 13.33, 1.5, data.get('title', '谢谢'), 48, True, palette['primary'], align='center', valign='middle')
    add_textbox(slide, 0, 4.2, 13.33, 0.8, data.get('subtitle', ''), 22, False, palette['textLight'], align='center')


LAYOUTS = {
    'cover': layout_cover,
    'content': layout_content,
    'data': layout_data,
    'split': layout_split,
    'timeline': layout_timeline,
    'comparison': layout_comparison,
    'end': layout_end,
}


def content_to_pptx(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = json.load(f)

    title = content.get('title', '演示文稿')
    theme = content.get('theme', 'midnight-executive')
    slides_data = content.get('slides', [])
    palette = COLOR_PALETTES.get(theme, COLOR_PALETTES['midnight-executive'])

    print(f"主题: {palette.get('name', theme)} ({theme})")
    print(f"共 {len(slides_data)} 页幻灯片")

    # 创建演示文稿
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    # 使用空白布局
    blank_layout = prs.slide_layouts[6]

    for i, slide_data in enumerate(slides_data):
        print(f"处理第 {i + 1}/{len(slides_data)} 页...")
        slide = prs.slides.add_slide(blank_layout)
        layout_fn = LAYOUTS.get(slide_data.get('layout', 'content'), layout_content)
        layout_fn(slide, slide_data.get('data', slide_data), palette)

    prs.save(output_file)
    print(f"PPTX 已导出: {output_file}")
    return output_file


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='content.json → PPTX 直接生成')
    parser.add_argument('--input', '-i', required=True, help='content.json 文件路径')
    parser.add_argument('--output', '-o', help='输出 PPTX 文件路径')
    args = parser.parse_args()

    output = args.output or args.input.replace('.json', '.pptx')
    content_to_pptx(args.input, output)
