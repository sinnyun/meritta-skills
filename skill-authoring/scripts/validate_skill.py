#!/usr/bin/env python3
"""validate_skill.py — Skill 静态校验

用法:
    python validate_skill.py --skill-path <Skill路径>

功能:
    检查 Skill 目录和文件的确定性问题，输出 PASS / WARNING / FAIL。

检查项:
    1. SKILL.md 是否存在
    2. YAML frontmatter 是否合法
    3. name 字段是否存在
    4. description 字段是否存在
    5. name 是否 lowercase
    6. name 是否 kebab-case
    7. references 中引用的文件是否存在
    8. scripts 中引用的脚本是否存在
    9. 是否残留 TODO
    10. 是否存在空模板目录
    11. 是否存在明显无效路径
    12. 脚本是否使用了 cwd 依赖的路径解析
    13. 目录结构是否合法
"""

import argparse
import os
import re
import sys
from pathlib import Path

# Exit codes
EXIT_PASS = 0
EXIT_WARNING = 1
EXIT_FAIL = 2


class ValidationResult:
    def __init__(self):
        self.errors = []      # FAIL
        self.warnings = []    # WARNING
        self.passes = []      # PASS

    @property
    def status(self):
        if self.errors:
            return 'FAIL'
        if self.warnings:
            return 'WARNING'
        return 'PASS'

    @property
    def exit_code(self):
        if self.errors:
            return EXIT_FAIL
        if self.warnings:
            return EXIT_WARNING
        return EXIT_PASS


def parse_frontmatter(content: str):
    """解析 YAML frontmatter，返回 (frontmatter_str, body_str)"""
    if not content.startswith('---'):
        return None, content

    # 找到第二个 ---
    idx = content.find('---', 3)
    if idx == -1:
        return None, content

    frontmatter = content[3:idx].strip()
    body = content[idx + 3:].strip()
    return frontmatter, body


def extract_field(frontmatter: str, field: str) -> str:
    """从 frontmatter 文本中提取字段值（简单解析，不依赖 yaml 库）
    支持 YAML block scalar (| 和 >) 和单行值。
    """
    pattern = rf'^{field}:\s*(.*)$'
    match = re.search(pattern, frontmatter, re.MULTILINE | re.IGNORECASE)
    if match:
        value = match.group(1).strip()
        # 去掉引号
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        # 处理 block scalar (| 或 >)
        if value in ('|', '>', '|-', '>-', '|+', '>+'):
            # 取后续缩进行的第一行非空内容作为值
            lines = frontmatter.split('\n')
            found_line = -1
            for i, line in enumerate(lines):
                if re.match(rf'^{field}:', line, re.IGNORECASE):
                    found_line = i
                    break
            if found_line >= 0:
                for j in range(found_line + 1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith('#'):
                        return next_line
            return ''
        return value
    return ''


def validate_skill(skill_path: str) -> ValidationResult:
    result = ValidationResult()
    skill_dir = Path(skill_path)

    if not skill_dir.is_dir():
        result.errors.append(f"Skill 目录不存在: {skill_path}")
        return result

    # 1. SKILL.md 是否存在
    skill_md = skill_dir / 'SKILL.md'
    if not skill_md.exists():
        result.errors.append("SKILL.md 不存在")
        return result
    result.passes.append("SKILL.md 存在")

    # 读取 SKILL.md
    content = skill_md.read_text(encoding='utf-8')

    # 2. YAML frontmatter 是否合法
    frontmatter, body = parse_frontmatter(content)
    if frontmatter is None:
        result.errors.append("SKILL.md 缺少 YAML frontmatter（必须以 --- 开头和结尾）")
        return result
    result.passes.append("YAML frontmatter 存在")

    # 3. name 字段
    name = extract_field(frontmatter, 'name')
    if not name:
        result.errors.append("frontmatter 中缺少 name 字段")
    else:
        result.passes.append(f"name = '{name}'")

        # 5. name 是否 lowercase
        if name != name.lower():
            result.errors.append(f"name '{name}' 不是全小写")

        # 6. name 是否 kebab-case
        kebab_pattern = r'^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$'
        if not re.match(kebab_pattern, name):
            result.errors.append(f"name '{name}' 不符合 kebab-case 规范")

    # 4. description 字段
    description = extract_field(frontmatter, 'description')
    if not description:
        result.errors.append("frontmatter 中缺少 description 字段")
    elif len(description) < 10:
        result.warnings.append("description 过短，可能无法准确触发")
    else:
        result.passes.append("description 存在")

    # 7. 检查 references 中引用的文件是否存在
    # 搜索 body 中类似 references/xxx.md 的路径引用
    ref_pattern = r'(?:references|scripts|assets)/[^\s\'"<>]+\.\w+'
    referenced_files = re.findall(ref_pattern, body)
    for ref in referenced_files:
        ref_path = skill_dir / ref
        if not ref_path.exists():
            result.warnings.append(f"引用的文件不存在: {ref}")

    # 8. 检查 SKILL.md 中的 $AGENT_ROOT / $SKILL_ROOT 引用
    # 这些是运行时变量，不检查具体路径
    var_refs = re.findall(r'\$(?:AGENT_ROOT|SKILL_ROOT)/[^\s\'"<>]+', body)
    if var_refs:
        result.passes.append(f"发现 {len(var_refs)} 个变量路径引用（运行时解析）")

    # 9. 是否残留 TODO
    todo_pattern = r'TODO|FIXME|PLACEHOLDER|<your-|<TODO>'
    todos = re.findall(todo_pattern, content, re.IGNORECASE)
    if todos:
        result.warnings.append(f"SKILL.md 中残留 {len(todos)} 个 TODO/FIXME/占位符")

    # 检查其他文件中的 TODO（跳过 SKILL.md，已检查过）
    for f in skill_dir.rglob('*'):
        if f == skill_md:
            continue
        if f.is_file() and f.suffix in ('.md', '.py', '.js', '.mjs', '.ts', '.sh'):
            try:
                file_content = f.read_text(encoding='utf-8')
                file_todos = re.findall(todo_pattern, file_content, re.IGNORECASE)
                if file_todos:
                    rel_path = f.relative_to(skill_dir)
                    result.warnings.append(f"{rel_path} 中残留 {len(file_todos)} 个 TODO/FIXME")
            except Exception:
                pass

    # 10. 是否存在空目录（只有 .gitkeep）
    for d in skill_dir.rglob('*'):
        if d.is_dir():
            files = list(d.iterdir())
            if len(files) == 1 and files[0].name == '.gitkeep':
                rel_path = d.relative_to(skill_dir)
                result.warnings.append(f"空目录（只有 .gitkeep）: {rel_path}")
            elif len(files) == 0:
                rel_path = d.relative_to(skill_dir)
                result.warnings.append(f"空目录: {rel_path}")

    # 11. 检查是否有无效路径（绝对路径指向不存在的位置）
    abs_path_pattern = r'(?:/|\w:\\)[^\s\'"<>]+\.\w+'
    abs_paths = re.findall(abs_path_pattern, body)
    for ap in abs_paths:
        # 跳过变量路径和常见路径
        if '$' in ap or ap.startswith('http') or 'AGENT_ROOT' in ap or 'SKILL_ROOT' in ap:
            continue
        # 检查是否是相对路径中的绝对路径引用
        if os.path.isabs(ap) and not os.path.exists(ap):
            # 可能是示例路径，只 warn
            if not ap.startswith('/tmp') and not ap.startswith('/usr') and not ap.startswith('/bin'):
                result.warnings.append(f"可能无效的绝对路径: {ap}")

    # 11.5. 检查脚本是否使用了 cwd 依赖的路径解析
    scripts_dir = skill_dir / 'scripts'
    if scripts_dir.exists() and scripts_dir.is_dir():
        for script_file in scripts_dir.rglob('*.py'):
            try:
                script_content = script_file.read_text(encoding='utf-8')
                # 检查 Path("./") 或 Path('.') 或 os.chdir() 这类模式
                cwd_patterns = [
                    r'Path\(["\']\./',  # Path("./
                    r'Path\(["\']\.["\']\)',  # Path('.')
                    r'os\.chdir\(',  # os.chdir(
                ]
                for pattern in cwd_patterns:
                    matches = re.findall(pattern, script_content)
                    if matches:
                        rel_path = script_file.relative_to(skill_dir)
                        result.warnings.append(f"{rel_path} 使用了 cwd 依赖的路径解析（{len(matches)} 处）— 应使用 Path(__file__) 而非相对路径")
                        break  # 只报告一次，不重复报告
            except Exception:
                pass

    # 12. 目录结构是否合法
    valid_dirs = {'scripts', 'references', 'assets', 'config', 'prompts', 'workflows', 'templates', 'evals'}
    for item in skill_dir.iterdir():
        if item.is_dir() and item.name not in valid_dirs and not item.name.startswith('.'):
            rel_path = item.relative_to(skill_dir)
            result.warnings.append(f"非标准目录: {rel_path}（标准目录: {', '.join(sorted(valid_dirs))}）")

    return result


def print_report(result: ValidationResult, skill_path: str):
    print(f"\n{'=' * 60}")
    print(f"Skill Validation Report")
    print(f"Path: {skill_path}")
    print(f"{'=' * 60}\n")

    if result.passes:
        print("--- PASS ---")
        for p in result.passes:
            print(f"  [PASS] {p}")
        print()

    if result.warnings:
        print("--- WARNING ---")
        for w in result.warnings:
            print(f"  [WARN] {w}")
        print()

    if result.errors:
        print("--- FAIL ---")
        for e in result.errors:
            print(f"  [FAIL] {e}")
        print()

    print(f"{'=' * 60}")
    print(f"Status: {result.status}")
    print(f"  PASS: {len(result.passes)}")
    print(f"  WARNING: {len(result.warnings)}")
    print(f"  FAIL: {len(result.errors)}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description='Skill 静态校验')
    parser.add_argument('--skill-path', required=True, help='Skill 目录路径')
    args = parser.parse_args()

    skill_path = os.path.abspath(args.skill_path)
    result = validate_skill(skill_path)
    print_report(result, skill_path)
    sys.exit(result.exit_code)


if __name__ == '__main__':
    main()
