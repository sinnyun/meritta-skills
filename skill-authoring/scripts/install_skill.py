#!/usr/bin/env python3
"""install_skill.py — 安装 Skill 到目标目录

用法:
    python install_skill.py --skill-zip <zip_path> --target <target_dir>

功能:
    将打包好的 Skill ZIP 安装到指定的 skills 目录。
    Agent 调用时必须提供 --target 参数（Agent 知道自己的全局 skills 目录位置）。

示例:
    python install_skill.py --skill-zip meeting-minutes.zip --target ~/.codearts/skills
"""

import argparse
import os
import sys
import zipfile
from pathlib import Path


def install_skill(skill_zip: Path, target_dir: Path, force: bool = False) -> bool:
    """将 Skill ZIP 解压到目标目录。

    如果目标目录下已存在同名 Skill，默认报错退出。
    只有 force=True 时才覆盖。
    """
    skill_name = skill_zip.stem  # e.g. "portrait-bg-remover" from "portrait-bg-remover.zip"
    dest = target_dir / skill_name

    # 如果已存在，检查是否允许覆盖
    if dest.exists():
        if not force:
            print(f"错误: 目标已存在: {dest}", file=sys.stderr)
            print(f"提示: 如需覆盖，请添加 --force 参数", file=sys.stderr)
            return False
        import shutil
        shutil.rmtree(dest)
        print(f"已删除旧版本: {dest}")

    # 解压
    with zipfile.ZipFile(skill_zip, 'r') as zf:
        zf.extractall(target_dir)

    print(f"安装完成: {dest}")
    return True


def main():
    parser = argparse.ArgumentParser(description='安装 Skill 到目标目录')
    parser.add_argument('--skill-zip', required=True, help='Skill ZIP 文件路径')
    parser.add_argument('--target', required=True, help='目标 skills 目录')
    parser.add_argument('--force', action='store_true', help='如果目标已存在，强制覆盖')
    args = parser.parse_args()

    skill_zip = Path(args.skill_zip).resolve()
    target_dir = Path(args.target).resolve()

    if not skill_zip.exists():
        print(f"错误: ZIP 文件不存在: {skill_zip}", file=sys.stderr)
        sys.exit(1)

    if not target_dir.is_dir():
        print(f"错误: 目标目录不存在: {target_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"安装到: {target_dir}")

    if install_skill(skill_zip, target_dir, force=args.force):
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
