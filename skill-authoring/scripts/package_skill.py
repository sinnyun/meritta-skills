#!/usr/bin/env python3
"""package_skill.py — Skill 最终打包

用法:
    python package_skill.py --skill-path <Skill路径> --skill-root <skill-authoring路径>

功能:
    - 打包前自动 Validation
    - Validation FAIL 禁止打包
    - 排除临时文件、缓存、.DS_Store、__pycache__ 等
    - 在当前工作目录下输出 <skill-name>.zip
"""

import argparse
import os
import subprocess
import sys
import zipfile
from pathlib import Path


EXCLUDE_PATTERNS = {
    '__pycache__', '.pyc', '.DS_Store', '.review', '.review-tmp', '.git',
    'node_modules', '.gitkeep', '*.tmp', '*.bak', '*.swp', '*.swo',
    '.pytest_cache', '.mypy_cache', '.ruff_cache', '*.egg-info'
}


def should_exclude(path: Path) -> bool:
    """判断文件是否应该排除"""
    parts = path.parts
    for part in parts:
        if part in EXCLUDE_PATTERNS:
            return True
        for pattern in EXCLUDE_PATTERNS:
            if '*' in pattern and part.endswith(pattern.replace('*', '')):
                return True

    # 检查文件名
    name = path.name
    for pattern in EXCLUDE_PATTERNS:
        if '*' in pattern:
            suffix = pattern.replace('*', '')
            if name.endswith(suffix):
                return True
        elif name == pattern:
            return True

    return False


def run_validation(skill_path: str, skill_root: str) -> bool:
    """运行静态校验"""
    validate_script = os.path.join(skill_root, 'scripts', 'validate_skill.py')
    if not os.path.exists(validate_script):
        print("WARNING: validate_skill.py 不存在，跳过校验")
        return True

    try:
        result = subprocess.run(
            [sys.executable, validate_script, '--skill-path', skill_path],
            capture_output=True, text=True, encoding='utf-8', errors='replace'
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        # exit_code 0 = PASS, 1 = WARNING, 2 = FAIL
        if result.returncode == 2:
            print("ERROR: Validation FAIL，禁止打包")
            return False
        return True
    except Exception as e:
        print(f"ERROR: 校验执行失败: {e}", file=sys.stderr)
        return False


def package_skill(skill_path: str, skill_root: str) -> str:
    """打包 Skill 为 ZIP，输出到当前工作目录

    返回 ZIP 文件路径。
    """
    skill_dir = Path(skill_path)
    skill_name = skill_dir.name
    output = os.path.join(os.getcwd(), f"{skill_name}.zip")

    # 创建 ZIP
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(skill_path):
            # 过滤目录
            dirs[:] = [d for d in dirs if not should_exclude(Path(root) / d)]

            for file in files:
                file_path = Path(root) / file
                if should_exclude(file_path):
                    continue

                arcname = os.path.relpath(file_path, os.path.dirname(skill_path))
                zf.write(file_path, arcname)
                print(f"  Added: {arcname}")

    return output


def main():
    parser = argparse.ArgumentParser(description='Skill 最终打包')
    parser.add_argument('--skill-path', required=True, help='Skill 目录路径')
    parser.add_argument('--skill-root', default='', help='skill-authoring Skill 根目录路径（用于校验）')
    parser.add_argument('--skip-validation', action='store_true', help='跳过校验（不推荐）')
    args = parser.parse_args()

    skill_path = os.path.abspath(args.skill_path)
    skill_root = os.path.abspath(args.skill_root) if args.skill_root else ''

    if not os.path.isdir(skill_path):
        print(f"ERROR: Skill 目录不存在: {skill_path}", file=sys.stderr)
        sys.exit(1)

    # 自动 Validation
    if not args.skip_validation:
        if skill_root:
            if not run_validation(skill_path, skill_root):
                sys.exit(2)
        else:
            print("WARNING: 未提供 --skill-root，跳过校验")

    # 打包
    print(f"\nPackaging: {skill_path}")
    output = package_skill(skill_path, skill_root)
    if output:
        size = os.path.getsize(output)
        print(f"\n打包完成: {output}")
        print(f"  大小: {size:,} bytes ({size / 1024:.1f} KB)")
    else:
        print("ERROR: 打包失败", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
