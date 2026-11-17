#!/usr/bin/env python3
"""prepare_review.py — 生成隔离的 Review Package

用法:
    python prepare_review.py --skill-path <Skill路径> --requirement "<用户原始需求>" --skill-root <SKILL_ROOT> --output <输出文件> [--previous-review <上一轮报告路径>]

功能:
    生成一份精简的 Review Package 导航文档，包含：
    - 用户原始需求
    - Skill 绝对路径（评审者据此直接读取 Skill 目录下的文件，包括 SKILL.md）
    - Skill 目录树（排除 .review/）
    - 上一轮评审报告（如有）

    不包含：
    - SKILL.md 全文（评审者通过 Skill 路径直接读取）
    - Creator 的思考过程、自我评价或设计决策理由
    - references/scripts/assets 的文件内容（评审者通过 Skill 路径直接读取）
    - Evaluation Rubric / Issue Severity（由 skill-review Skill 自行加载）
"""

import argparse
import os
import sys
from pathlib import Path


def build_skill_tree(skill_dir: Path, prefix: str = '', exclude_dirs: set = None) -> str:
    """生成 Skill 目录树，排除指定目录（如 .review/）"""
    if exclude_dirs is None:
        exclude_dirs = {'.review'}

    lines = []
    items = sorted(
        [item for item in skill_dir.iterdir() if item.name not in exclude_dirs],
        key=lambda x: (x.is_file(), x.name)
    )

    for i, item in enumerate(items):
        is_last = (i == len(items) - 1)
        connector = '└── ' if is_last else '├── '
        lines.append(f"{prefix}{connector}{item.name}")

        if item.is_dir():
            extension = '    ' if is_last else '│   '
            sub_tree = build_skill_tree(item, prefix + extension, exclude_dirs)
            lines.append(sub_tree)

    return '\n'.join(lines)


def read_file_content(filepath: Path) -> str:
    """读取文件内容"""
    try:
        return filepath.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        return f"[读取失败: {e}]"


def generate_review_input(requirement: str, skill_path: str, skill_info: dict, previous_review: str = '') -> str:
    """生成 Review Input 文档"""
    sections = []

    # 1. 原始需求
    sections.append("## Original Requirement\n")
    sections.append(requirement)
    sections.append("")

    # 2. Skill 路径
    sections.append("## Skill Path\n")
    sections.append(f"```\n{skill_path}\n```")
    sections.append("")

    # 3. Skill 目录树
    sections.append("## Skill Directory Tree\n")
    sections.append("```")
    sections.append(skill_info['tree'])
    sections.append("```")
    sections.append("")

    # 4. 上一轮评审报告（如有）
    if previous_review:
        sections.append("## Previous Review Report\n")
        sections.append("以下是上一轮评审的结果。已修复的问题请验证，未修复的问题请继续关注。")
        sections.append("")
        sections.append("```markdown")
        sections.append(previous_review)
        sections.append("```")
        sections.append("")

    return '\n'.join(sections)


def main():
    parser = argparse.ArgumentParser(description='生成隔离的 Review Package')
    parser.add_argument('--skill-path', required=True, help='目标 Skill 目录路径')
    parser.add_argument('--requirement', required=True, help='用户原始需求')
    parser.add_argument('--skill-root', required=True, help='skill-authoring Skill 根目录路径')
    parser.add_argument('--output', required=True, help='输出文件路径')
    parser.add_argument('--previous-review', default=None, help='上一轮评审报告路径（可选，用于多轮评审）')
    args = parser.parse_args()

    skill_path = os.path.abspath(args.skill_path)
    skill_root = os.path.abspath(args.skill_root)
    output = os.path.abspath(args.output)

    # 读取上一轮评审报告（如有）
    previous_review = ''
    if args.previous_review:
        prev_path = os.path.abspath(args.previous_review)
        if os.path.exists(prev_path):
            with open(prev_path, 'r', encoding='utf-8') as f:
                previous_review = f.read()
        else:
            print(f"警告: 上一轮评审报告不存在: {prev_path}", file=sys.stderr)

    # 收集 Skill 信息（仅目录树）
    skill_dir = Path(skill_path)
    skill_info = {
        'tree': build_skill_tree(skill_dir),
    }

    # 生成 Review Input
    review_input = generate_review_input(args.requirement, skill_path, skill_info, previous_review)

    # 组装完整文档
    full_doc = []
    full_doc.append("# Review Package\n")
    full_doc.append("以下是为独立评审准备的 Skill 导航信息。")
    full_doc.append("请通过 Skill Path 直接读取 Skill 目录下的文件进行评审。")
    full_doc.append("你不应假设 Creator 的设计意图，只根据材料评审。\n")

    full_doc.append(review_input)

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output), exist_ok=True)

    with open(output, 'w', encoding='utf-8') as f:
        f.write('\n'.join(full_doc))

    # 统计
    total_size = os.path.getsize(output)

    print(f"Review Package 已生成: {output}")
    print(f"  文件大小: {total_size} bytes")
    print(f"  包含内容:")
    print(f"    - 用户原始需求")
    print(f"    - Skill 路径: {skill_path}")
    print(f"    - Skill 目录树（排除 .review/）")
    if previous_review:
        print(f"    - 上一轮评审报告: {args.previous_review}")


if __name__ == '__main__':
    main()
