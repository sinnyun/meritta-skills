#!/usr/bin/env python3
"""
Breakout Game Generator - 打砖块游戏生成器
快速生成经典的打砖块网页游戏
"""

import argparse
import json
import html
import os

# 打砖块游戏模板（已移除roundRect，使用fillRect兼容旧浏览器）
BREAKOUT_GAME_TEMPLATE = '''<!DOCTYPE html>
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
            background: linear-gradient(135deg, #2c3e50 0%, #1a252f 100%);
            font-family: 'Segoe UI', sans-serif;
        }}
        #gameContainer {{ text-align: center; }}
        h1 {{ color: #3498db; margin-bottom: 15px; text-shadow: 0 0 10px rgba(52,152,219,0.5); }}
        canvas {{ border: 3px solid #3498db; border-radius: 10px; box-shadow: 0 0 30px rgba(52,152,219,0.3); }}
        #score {{ color: #fff; font-size: 20px; margin: 10px 0; }}
        #instructions {{ color: #888; margin-top: 10px; font-size: 14px; }}
    </style>
</head>
<body>
    <div id="gameContainer">
        <h1>{title}</h1>
        <div id="score">Score: 0 | Lives: {lives}</div>
        <canvas id="gameCanvas" width="{width}" height="{height}"></canvas>
        <div id="instructions">Mouse/Arrow Keys: Move | R: Restart</div>
    </div>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreDisplay = document.getElementById('score');
        
        const brickRowCount = {brick_rows};
        const brickColumnCount = 10;
        const brickWidth = 70;
        const brickHeight = 20;
        const brickPadding = 5;
        const brickOffsetTop = 50;
        const brickOffsetLeft = (canvas.width - (brickColumnCount * (brickWidth + brickPadding) - brickPadding)) / 2;
        
        const paddleHeight = 15;
        const paddleWidth = 100;
        let paddleX = (canvas.width - paddleWidth) / 2;
        
        const ballRadius = 10;
        let ballX = canvas.width / 2;
        let ballY = canvas.height - 50;
        let ballDX = {ball_speed};
        let ballDY = -{ball_speed};
        
        let score = 0;
        let lives = {lives};
        let gameOver = false;
        let gameWon = false;
        let rightPressed = false;
        let leftPressed = false;
        
        const bricks = [];
        const colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#3498db', '#9b59b6', '#1abc9c', '#e91e63'];
        
        for(let c = 0; c < brickColumnCount; c++) {{
            bricks[c] = [];
            for(let r = 0; r < brickRowCount; r++) {{
                bricks[c][r] = {{ x: 0, y: 0, status: 1, color: colors[r % colors.length] }};
            }}
        }}
        
        document.addEventListener('keydown', keyDownHandler);
        document.addEventListener('keyup', keyUpHandler);
        document.addEventListener('mousemove', mouseMoveHandler);
        
        function keyDownHandler(e) {{
            if(e.key === 'Right' || e.key === 'ArrowRight') rightPressed = true;
            else if(e.key === 'Left' || e.key === 'ArrowLeft') leftPressed = true;
            else if(e.key === 'r' || e.key === 'R') init();
        }}
        
        function keyUpHandler(e) {{
            if(e.key === 'Right' || e.key === 'ArrowRight') rightPressed = false;
            else if(e.key === 'Left' || e.key === 'ArrowLeft') leftPressed = false;
        }}
        
        function mouseMoveHandler(e) {{
            const relativeX = e.clientX - canvas.offsetLeft;
            if(relativeX > paddleWidth / 2 && relativeX < canvas.width - paddleWidth / 2) {{
                paddleX = relativeX - paddleWidth / 2;
            }}
        }}
        
        function collisionDetection() {{
            for(let c = 0; c < brickColumnCount; c++) {{
                for(let r = 0; r < brickRowCount; r++) {{
                    const b = bricks[c][r];
                    if(b.status === 1) {{
                        if(ballX > b.x && ballX < b.x + brickWidth && ballY > b.y && ballY < b.y + brickHeight) {{
                            ballDY = -ballDY;
                            b.status = 0;
                            score += 10;
                            scoreDisplay.textContent = 'Score: ' + score + ' | Lives: ' + lives;
                            if(score === brickRowCount * brickColumnCount * 10) {{
                                gameWon = true;
                            }}
                        }}
                    }}
                }}
            }}
        }}
        
        function drawBall() {{
            ctx.beginPath();
            ctx.arc(ballX, ballY, ballRadius, 0, Math.PI * 2);
            const gradient = ctx.createRadialGradient(ballX, ballY, 0, ballX, ballY, ballRadius);
            gradient.addColorStop(0, '#fff');
            gradient.addColorStop(1, '#3498db');
            ctx.fillStyle = gradient;
            ctx.fill();
            ctx.closePath();
        }}
        
        function drawPaddle() {{
            const gradient = ctx.createLinearGradient(paddleX, 0, paddleX + paddleWidth, 0);
            gradient.addColorStop(0, '#3498db');
            gradient.addColorStop(1, '#2980b9');
            ctx.fillStyle = gradient;
            ctx.fillRect(paddleX, canvas.height - paddleHeight - 10, paddleWidth, paddleHeight);
        }}
        
        function drawBricks() {{
            for(let c = 0; c < brickColumnCount; c++) {{
                for(let r = 0; r < brickRowCount; r++) {{
                    if(bricks[c][r].status === 1) {{
                        const brickX = c * (brickWidth + brickPadding) + brickOffsetLeft;
                        const brickY = r * (brickHeight + brickPadding) + brickOffsetTop;
                        bricks[c][r].x = brickX;
                        bricks[c][r].y = brickY;
                        ctx.fillStyle = bricks[c][r].color;
                        ctx.fillRect(brickX, brickY, brickWidth, brickHeight);
                    }}
                }}
            }}
        }}
        
        function init() {{
            ballX = canvas.width / 2;
            ballY = canvas.height - 50;
            ballDX = {ball_speed} * (Math.random() > 0.5 ? 1 : -1);
            ballDY = -{ball_speed};
            paddleX = (canvas.width - paddleWidth) / 2;
            score = 0;
            lives = {lives};
            gameOver = false;
            gameWon = false;
            scoreDisplay.textContent = 'Score: 0 | Lives: ' + lives;
            
            for(let c = 0; c < brickColumnCount; c++) {{
                for(let r = 0; r < brickRowCount; r++) {{
                    bricks[c][r].status = 1;
                }}
            }}
        }}
        
        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawBricks();
            drawBall();
            drawPaddle();
            collisionDetection();
            
            if(ballX + ballDX > canvas.width - ballRadius || ballX + ballDX < ballRadius) {{
                ballDX = -ballDX;
            }}
            if(ballY + ballDY < ballRadius) {{
                ballDY = -ballDY;
            }} else if(ballY + ballDY > canvas.height - ballRadius - paddleHeight - 10) {{
                if(ballX > paddleX && ballX < paddleX + paddleWidth) {{
                    ballDY = -ballDY;
                    const hitPos = (ballX - paddleX) / paddleWidth;
                    ballDX = (hitPos - 0.5) * 10;
                }}
            }}
            
            ballX += ballDX;
            ballY += ballDY;
            
            if(rightPressed && paddleX < canvas.width - paddleWidth) paddleX += 7;
            else if(leftPressed && paddleX > 0) paddleX -= 7;
            
            if(ballY > canvas.height) {{
                lives--;
                scoreDisplay.textContent = 'Score: ' + score + ' | Lives: ' + lives;
                if(!lives) {{
                    gameOver = true;
                    ctx.fillStyle = 'rgba(0,0,0,0.8)';
                    ctx.fillRect(0, 0, canvas.width, canvas.height);
                    ctx.fillStyle = '#e74c3c';
                    ctx.font = 'bold 48px Arial';
                    ctx.textAlign = 'center';
                    ctx.fillText('GAME OVER', canvas.width/2, canvas.height/2);
                    ctx.fillStyle = '#fff';
                    ctx.font = '24px Arial';
                    ctx.fillText('Final Score: ' + score, canvas.width/2, canvas.height/2 + 40);
                }} else {{
                    ballX = canvas.width / 2;
                    ballY = canvas.height - 50;
                    ballDX = {ball_speed} * (Math.random() > 0.5 ? 1 : -1);
                    ballDY = -{ball_speed};
                    paddleX = (canvas.width - paddleWidth) / 2;
                }}
            }}
            
            if(gameWon) {{
                ctx.fillStyle = 'rgba(0,0,0,0.8)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#2ecc71';
                ctx.font = 'bold 48px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('YOU WIN!', canvas.width/2, canvas.height/2);
                ctx.fillStyle = '#fff';
                ctx.font = '24px Arial';
                ctx.fillText('Final Score: ' + score, canvas.width/2, canvas.height/2 + 40);
            }}
            
            if(!gameOver && !gameWon) requestAnimationFrame(draw);
        }}
        
        draw();
    </script>
</body>
</html>'''


def get_difficulty_settings(difficulty: str) -> dict:
    """根据难度返回游戏设置
    
    Args:
        difficulty: easy/normal/hard
    
    Returns:
        dict: 包含brick_rows, lives, ball_speed的字典
    """
    settings = {
        'easy': {'brick_rows': 4, 'lives': 5, 'ball_speed': 3},
        'normal': {'brick_rows': 6, 'lives': 3, 'ball_speed': 4},
        'hard': {'brick_rows': 8, 'lives': 2, 'ball_speed': 6}
    }
    return settings.get(difficulty, settings['normal'])


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


def generate_breakout_game(width: int = 800, height: int = 600, 
                           difficulty: str = "normal", title: str = "Breakout"):
    """生成打砖块游戏HTML
    
    Args:
        width: 画布宽度 (200-1920)
        height: 画布高度 (200-1080)
        difficulty: easy/normal/hard
        title: 游戏标题 (会自动转义)
    
    Returns:
        str: HTML内容
    """
    # 参数校验
    width = max(200, min(1920, width))
    height = max(200, min(1080, height))
    
    # XSS防护
    safe_title = html.escape(title, quote=True)
    
    settings = get_difficulty_settings(difficulty)
    
    return BREAKOUT_GAME_TEMPLATE.format(
        width=width,
        height=height,
        title=safe_title,
        brick_rows=settings['brick_rows'],
        lives=settings['lives'],
        ball_speed=settings['ball_speed']
    )


def main():
    parser = argparse.ArgumentParser(
        description='Breakout Game Generator - 生成打砖块网页游戏',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python breakout_game.py                         # 普通难度
  python breakout_game.py --difficulty hard        # 困难模式
  python breakout_game.py -w 600 -H 400          # 自定义尺寸
  python breakout_game.py -t "My Breakout"       # 自定义标题
        '''
    )
    parser.add_argument('--width', '-w', type=int, default=800, 
                        help='画布宽度 (200-1920, 默认800)')
    parser.add_argument('--height', '-H', type=int, default=600, 
                        help='画布高度 (200-1080, 默认600)')
    parser.add_argument('--difficulty', '-d', choices=['easy', 'normal', 'hard'], 
                        default='normal', help='难度等级 (默认normal)')
    parser.add_argument('--title', '-t', type=str, default='Breakout', 
                        help='游戏标题 (默认Breakout)')
    parser.add_argument('--output', '-o', type=str, default='breakout-game.html', 
                        help='输出文件名 (默认breakout-game.html)')
    
    args = parser.parse_args()
    
    try:
        safe_output = validate_output_path(args.output)
        
        html_content = generate_breakout_game(
            width=args.width,
            height=args.height,
            difficulty=args.difficulty,
            title=args.title
        )
        
        with open(safe_output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        result = {
            "status": "success",
            "game": "breakout",
            "output_file": safe_output,
            "config": {
                "width": args.width,
                "height": args.height,
                "difficulty": args.difficulty
            },
            "instructions": f"在浏览器中打开 {safe_output} 即可游玩。使用鼠标或方向键移动挡板。"
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
