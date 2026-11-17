#!/usr/bin/env python3
"""
3D游戏统一生成器
支持7种3D游戏类型：sphere, cube, maze, flappy3d, shooter, platform, racing
"""

import argparse
import json
import os
import sys

# 导入各游戏生成器
from three_d_sphere import generate_sphere_game
from three_d_cube import generate_cube_game
from three_d_maze import generate_maze_game
from three_d_flappy import generate_flappy3d_game
from three_d_shooter import generate_shooter_game
from three_d_platform import generate_platform_game
from three_d_racing import generate_racing_game

# 游戏类型映射
GAME_TYPES = {
    'sphere': generate_sphere_game,
    'cube': generate_cube_game,
    'maze': generate_maze_game,
    'flappy3d': generate_flappy3d_game,
    'shooter': generate_shooter_game,
    'platform': generate_platform_game,
    'racing': generate_racing_game,
}

# 游戏描述
GAME_DESCRIPTIONS = {
    'sphere': '3D弹球收集游戏 - 收集物品，躲避障碍',
    'cube': '3D方块跑酷 - 无限跑酷，躲避障碍',
    'maze': '3D第一人称迷宫 - 探索迷宫，计时挑战',
    'flappy3d': '3D Flappy Bird - 控制飞行器穿越圆环',
    'shooter': '3D射击游戏 - 第一人称射击靶标',
    'platform': '3D平台跳跃 - 跳平台，收集金币',
    'racing': '3D赛车躲避 - 躲避迎面而来的障碍物',
}


def main():
    parser = argparse.ArgumentParser(
        description='3D Game Generator - Generate various 3D web games',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Game Types:
  sphere      - 3D Ball Collection Game
  cube        - 3D Cube Endless Runner
  maze        - 3D First-Person Maze
  flappy3d    - 3D Flappy Bird
  shooter     - 3D First-Person Shooter
  platform   - 3D Platform Jumping
  racing     - 3D Racing Dodge

Examples:
  python three_d_scene.py --type sphere --title "My Game"
  python three_d_scene.py --type flappy3d --difficulty hard
  python three_d_scene.py --type shooter --output my_game.html
        '''
    )
    
    parser.add_argument(
        '--type', '-t',
        required=True,
        choices=list(GAME_TYPES.keys()),
        help='Game type to generate'
    )
    parser.add_argument(
        '--title',
        default='3D Game',
        help='Game title (HTML-escaped automatically)'
    )
    parser.add_argument(
        '--difficulty', '-d',
        default='normal',
        choices=['easy', 'normal', 'hard'],
        help='Game difficulty'
    )
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Output HTML file (default: <type>.html)'
    )
    
    args = parser.parse_args()
    
    # 默认输出文件名
    if args.output is None:
        args.output = f'{args.type}.html'
    
    try:
        # 调用对应的生成器
        generator = GAME_TYPES[args.type]
        result = generator(
            title=args.title,
            difficulty=args.difficulty,
            output=args.output
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except KeyboardInterrupt:
        print(json.dumps({"status": "cancelled", "message": "User cancelled"}, ensure_ascii=False))
        sys.exit(130)
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == '__main__':
    main()
