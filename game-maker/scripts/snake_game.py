#!/usr/bin/env python3
"""
Snake Game Generator - 贪吃蛇游戏生成器
快速生成经典的贪吃蛇网页游戏
"""

import argparse
import json
import html
import os
from pathlib import Path

# 贪吃蛇游戏完整代码模板（已移除roundRect，使用fillRect兼容旧浏览器）
SNAKE_GAME_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline'">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            font-family: 'Segoe UI', sans-serif;
        }}
        #gameContainer {{ text-align: center; }}
        h1 {{ color: #00ff88; margin-bottom: 20px; text-shadow: 0 0 10px rgba(0,255,136,0.5); }}
        canvas {{ border: 3px solid #00ff88; border-radius: 10px; box-shadow: 0 0 30px rgba(0,255,136,0.3); }}
        #score {{ color: #fff; font-size: 24px; margin: 15px 0; }}
        #instructions {{ color: #888; margin-top: 15px; }}
    </style>
</head>
<body>
    <div id="gameContainer">
        <h1>{title}</h1>
        <div id="score">Score: 0</div>
        <canvas id="gameCanvas" width="{width}" height="{height}"></canvas>
        <div id="instructions">Arrow Keys/WASD: Move | Space: Pause | R: Restart</div>
    </div>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreDisplay = document.getElementById('score');
        
        const gridSize = 20;
        const cols = Math.floor(canvas.width / gridSize);
        const rows = Math.floor(canvas.height / gridSize);
        const speed = {speed};
        
        let snake, direction, food, score, gameOver, paused, gameLoop;
        
        function init() {{
            snake = [{{x: 5, y: 5}}];
            direction = {{x: 1, y: 0}};
            score = 0;
            gameOver = false;
            paused = false;
            scoreDisplay.textContent = 'Score: 0';
            placeFood();
            if (gameLoop) clearInterval(gameLoop);
            gameLoop = setInterval(update, Math.max(50, 200 - speed * 15));
        }}
        
        function placeFood() {{
            food = {{
                x: Math.floor(Math.random() * cols),
                y: Math.floor(Math.random() * rows)
            }};
            while (snake.some(seg => seg.x === food.x && seg.y === food.y)) {{
                food = {{
                    x: Math.floor(Math.random() * cols),
                    y: Math.floor(Math.random() * rows)
                }};
            }}
        }}
        
        function update() {{
            if (paused || gameOver) return;
            
            const head = {{
                x: snake[0].x + direction.x,
                y: snake[0].y + direction.y
            }};
            
            if (head.x < 0 || head.x >= cols || head.y < 0 || head.y >= rows) {{
                endGame();
                return;
            }}
            
            if (snake.some(seg => seg.x === head.x && seg.y === head.y)) {{
                endGame();
                return;
            }}
            
            snake.unshift(head);
            
            if (head.x === food.x && head.y === food.y) {{
                score += 10;
                scoreDisplay.textContent = 'Score: ' + score;
                placeFood();
            }} else {{
                snake.pop();
            }}
        }}
        
        function draw() {{
            ctx.fillStyle = '#0f0f23';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.strokeStyle = '#1a1a3e';
            for (let i = 0; i <= cols; i++) {{
                ctx.beginPath();
                ctx.moveTo(i * gridSize, 0);
                ctx.lineTo(i * gridSize, canvas.height);
                ctx.stroke();
            }}
            for (let i = 0; i <= rows; i++) {{
                ctx.beginPath();
                ctx.moveTo(0, i * gridSize);
                ctx.lineTo(canvas.width, i * gridSize);
                ctx.stroke();
            }}
            
            // 食物
            ctx.fillStyle = '#ff4757';
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#ff4757';
            ctx.beginPath();
            ctx.arc(food.x * gridSize + gridSize/2, food.y * gridSize + gridSize/2, gridSize/2 - 2, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
            
            // 蛇
            snake.forEach((segment, index) => {{
                const gradient = ctx.createRadialGradient(
                    segment.x * gridSize + gridSize/2, segment.y * gridSize + gridSize/2, 0,
                    segment.x * gridSize + gridSize/2, segment.y * gridSize + gridSize/2, gridSize/2
                );
                gradient.addColorStop(0, index === 0 ? '#00ff88' : '#00cc6a');
                gradient.addColorStop(1, index === 0 ? '#00cc6a' : '#009955');
                
                ctx.fillStyle = gradient;
                // 兼容旧浏览器，使用fillRect替代roundRect
                ctx.fillRect(segment.x * gridSize + 1, segment.y * gridSize + 1, gridSize - 2, gridSize - 2);
                
                // 蛇眼睛
                if (index === 0) {{
                    ctx.fillStyle = '#fff';
                    const eyeOffset = 4;
                    let eye1x, eye1y, eye2x, eye2y;
                    if (direction.x === 1) {{
                        eye1x = segment.x * gridSize + gridSize - eyeOffset; eye1y = segment.y * gridSize + 5;
                        eye2x = segment.x * gridSize + gridSize - eyeOffset; eye2y = segment.y * gridSize + gridSize - 5;
                    }} else if (direction.x === -1) {{
                        eye1x = segment.x * gridSize + eyeOffset; eye1y = segment.y * gridSize + 5;
                        eye2x = segment.x * gridSize + eyeOffset; eye2y = segment.y * gridSize + gridSize - 5;
                    }} else if (direction.y === 1) {{
                        eye1x = segment.x * gridSize + 5; eye1y = segment.y * gridSize + gridSize - eyeOffset;
                        eye2x = segment.x * gridSize + gridSize - 5; eye2y = segment.y * gridSize + gridSize - eyeOffset;
                    }} else {{
                        eye1x = segment.x * gridSize + 5; eye1y = segment.y * gridSize + eyeOffset;
                        eye2x = segment.x * gridSize + gridSize - 5; eye2y = segment.y * gridSize + eyeOffset;
                    }}
                    ctx.beginPath();
                    ctx.arc(eye1x, eye1y, 3, 0, Math.PI * 2);
                    ctx.arc(eye2x, eye2y, 3, 0, Math.PI * 2);
                    ctx.fill();
                }}
            }});
            
            if (gameOver) {{
                ctx.fillStyle = 'rgba(0,0,0,0.7)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#ff4757';
                ctx.font = 'bold 48px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('GAME OVER', canvas.width/2, canvas.height/2 - 20);
                ctx.fillStyle = '#fff';
                ctx.font = '24px Arial';
                ctx.fillText('Final Score: ' + score, canvas.width/2, canvas.height/2 + 30);
                ctx.fillText('Press R to Restart', canvas.width/2, canvas.height/2 + 70);
            }}
            
            if (paused) {{
                ctx.fillStyle = 'rgba(0,0,0,0.5)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#00ff88';
                ctx.font = 'bold 36px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('PAUSED', canvas.width/2, canvas.height/2);
                ctx.fillStyle = '#fff';
                ctx.font = '18px Arial';
                ctx.fillText('Press Space to Resume', canvas.width/2, canvas.height/2 + 40);
            }}
            
            requestAnimationFrame(draw);
        }}
        
        function endGame() {{
            gameOver = true;
            clearInterval(gameLoop);
        }}
        
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'r' || e.key === 'R') {{ init(); return; }}
            if (e.key === ' ') {{ paused = !paused; return; }}
            if (['ArrowUp', 'w', 'W'].includes(e.key) && direction.y !== 1) {{
                direction = {{x: 0, y: -1}};
            }} else if (['ArrowDown', 's', 'S'].includes(e.key) && direction.y !== -1) {{
                direction = {{x: 0, y: 1}};
            }} else if (['ArrowLeft', 'a', 'A'].includes(e.key) && direction.x !== 1) {{
                direction = {{x: -1, y: 0}};
            }} else if (['ArrowRight', 'd', 'D'].includes(e.key) && direction.x !== -1) {{
                direction = {{x: 1, y: 0}};
            }}
        }});
        
        // 移动端支持
        let touchStartX, touchStartY;
        canvas.addEventListener('touchstart', (e) => {{
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        }});
        
        canvas.addEventListener('touchend', (e) => {{
            const dx = e.changedTouches[0].clientX - touchStartX;
            const dy = e.changedTouches[0].clientY - touchStartY;
            if (Math.abs(dx) > Math.abs(dy)) {{
                if (dx > 30 && direction.x !== -1) direction = {{x: 1, y: 0}};
                else if (dx < -30 && direction.x !== 1) direction = {{x: -1, y: 0}};
            }} else {{
                if (dy > 30 && direction.y !== -1) direction = {{x: 0, y: 1}};
                else if (dy < -30 && direction.y !== 1) direction = {{x: 0, y: -1}};
            }}
        }});
        
        init();
        draw();
    </script>
</body>
</html>'''


def validate_output_path(output_path: str) -> str:
    """验证输出路径，防止路径遍历攻击"""
    # 禁止写入敏感目录
    sensitive_dirs = ['/etc', '/var', '/usr', '/bin', '/sbin', '/boot', '/dev', '/proc', '/sys']
    
    # 检查是否是绝对路径
    if os.path.isabs(output_path):
        real_path = os.path.realpath(output_path)
        for sensitive in sensitive_dirs:
            if real_path.startswith(sensitive + '/') or real_path == sensitive:
                raise ValueError(f"Cannot write to system directory: {sensitive}")
        return output_path
    
    # 相对路径：确保不包含 ../ 等路径遍历
    if '..' in output_path:
        raise ValueError(f"Path traversal detected: {output_path}")
    
    return output_path


def generate_snake_game(width: int = 800, height: int = 600, speed: int = 5, title: str = "Snake Game"):
    """生成贪吃蛇游戏HTML
    
    Args:
        width: 画布宽度 (200-1920)
        height: 画布高度 (200-1080)
        speed: 游戏速度 (1-10, 越高越快)
        title: 游戏标题 (会自动转义防止XSS)
    
    Returns:
        str: HTML内容
    """
    # 参数校验
    width = max(200, min(1920, width))
    height = max(200, min(1080, height))
    speed = max(1, min(10, speed))
    
    # XSS防护：转义title
    safe_title = html.escape(title, quote=True)
    
    return SNAKE_GAME_TEMPLATE.format(
        width=width,
        height=height,
        speed=speed,
        title=safe_title
    )


def main():
    parser = argparse.ArgumentParser(
        description='Snake Game Generator - 生成贪吃蛇网页游戏',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python snake_game.py                          # 默认设置
  python snake_game.py --speed 8               # 快速游戏
  python snake_game.py -w 600 -he 400          # 自定义尺寸
  python snake_game.py -t "My Snake"           # 自定义标题
        '''
    )
    parser.add_argument('--width', '-w', type=int, default=800, 
                        help='画布宽度 (200-1920, 默认800)')
    parser.add_argument('--height', '-H', type=int, default=600, 
                        help='画布高度 (200-1080, 默认600)')
    parser.add_argument('--speed', '-s', type=int, default=5, choices=range(1, 11), 
                        help='游戏速度 1-10, 越高越快 (默认5)')
    parser.add_argument('--title', '-t', type=str, default='Snake Game', 
                        help='游戏标题 (默认 Snake Game)')
    parser.add_argument('--output', '-o', type=str, default='snake-game.html', 
                        help='输出文件名 (默认 snake-game.html)')
    
    args = parser.parse_args()
    
    try:
        # 安全校验输出路径
        safe_output = validate_output_path(args.output)
        
        html_content = generate_snake_game(
            width=args.width,
            height=args.height,
            speed=args.speed,
            title=args.title
        )
        
        with open(safe_output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        result = {
            "status": "success",
            "game": "snake",
            "output_file": safe_output,
            "file_size": len(html_content),
            "config": {
                "width": args.width,
                "height": args.height,
                "speed": args.speed,
                "title": args.title
            },
            "instructions": f"在浏览器中打开 {safe_output} 即可游玩。使用方向键或WASD控制贪吃蛇。"
        }
        print(json.dumps(result, ensure_ascii=False))
        
    except ValueError as e:
        error_result = {
            "status": "error",
            "error": str(e),
            "help": "确保输出路径是相对路径，不包含 ../ 等路径遍历字符"
        }
        print(json.dumps(error_result, ensure_ascii=False))
        exit(1)
    except IOError as e:
        error_result = {
            "status": "error",
            "error": f"文件写入失败: {str(e)}",
            "help": "检查目录是否存在且有写入权限"
        }
        print(json.dumps(error_result, ensure_ascii=False))
        exit(1)


if __name__ == "__main__":
    main()
