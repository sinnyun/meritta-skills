#!/usr/bin/env python3
"""init_skill.py — 从模板初始化 Skill 目录结构

用法:
    python init_skill.py --name <skill-name> --skill-root <SKILL_ROOT>

功能:
    - 在当前工作目录下创建 Skill 目录
    - 从模板复制 SKILL.md
    - 创建 scripts/ references/ assets/ 空目录（后续按需删除）
    - 不生成大量无意义示例内容
"""

import argparse
import os
import re
import shutil
import sys


def validate_name(name: str) -> str:
    """校验 Skill name 是否符合 kebab-case"""
    pattern = r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$'
    if not re.match(pattern, name):
        print(f"ERROR: name '{name}' 不符合 kebab-case 规范（全小写，连字符分隔）", file=sys.stderr)
        sys.exit(1)
    return name


def init_skill(name: str, output: str, skill_root: str) -> str:
    """初始化 Skill 目录"""
    skill_path = os.path.join(output, name)

    # 检查目录是否已存在
    if os.path.exists(skill_path):
        print(f"ERROR: 目录已存在: {skill_path}", file=sys.stderr)
        sys.exit(1)

    # 创建根目录
    os.makedirs(skill_path, exist_ok=True)

    # 从模板复制 SKILL.md
    template_path = os.path.join(skill_root, 'assets', 'skill-template', 'SKILL.md')
    if os.path.exists(template_path):
        dest = os.path.join(skill_path, 'SKILL.md')
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # 替换模板中的 name 占位符
        content = content.replace('{{SKILL_NAME}}', name)
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Created: SKILL.md")
    else:
        # 模板不存在，创建基础 SKILL.md
        dest = os.path.join(skill_path, 'SKILL.md')
        content = f"""---
name: {name}
description: |
  TODO: 描述 Skill 做什么。
  什么场景应该触发。
  触发词：关键词1、关键词2。
---

# {name.replace('-', ' ').title()}

## TODO: 编写 Skill 核心工作流
"""
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Created: SKILL.md (基础模板，需要补充内容)")

    # 创建空目录（后续按需删除）
    for subdir in ['scripts', 'references', 'assets']:
        dir_path = os.path.join(skill_path, subdir)
        os.makedirs(dir_path, exist_ok=True)
        # 创建 .gitkeep 保持目录
        gitkeep = os.path.join(dir_path, '.gitkeep')
        with open(gitkeep, 'w') as f:
            pass
        print(f"  Created: {subdir}/")

    print(f"\nSkill '{name}' 已初始化: {skill_path}")
    print("提示: 根据需求保留必要的目录，删除不需要的空目录。")
    return skill_path


def main():
    parser = argparse.ArgumentParser(description='初始化 Skill 目录结构')
    parser.add_argument('--name', required=True, help='Skill 名称 (kebab-case)')
    parser.add_argument('--skill-root', required=True, help='skill-authoring Skill 根目录路径')
    args = parser.parse_args()

    name = validate_name(args.name)
    output = os.getcwd()  # 直接在当前工作目录创建
    skill_root = os.path.abspath(args.skill_root)

    if not os.path.isdir(skill_root):
        print(f"ERROR: Skill 根目录不存在: {skill_root}", file=sys.stderr)
        sys.exit(1)

    init_skill(name, output, skill_root)


if __name__ == '__main__':
    main()
