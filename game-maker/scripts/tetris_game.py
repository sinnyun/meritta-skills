#!/usr/bin/env python3
"""
Tetris Game Generator - 俄罗斯方块游戏生成器
快速生成经典的俄罗斯方块网页游戏
"""

import argparse
import json
import html
import os

# 俄罗斯方块游戏模板（已移除roundRect，使用fillRect兼容旧浏览器）
TETRIS_GAME_TEMPLATE = '''<!DOCTYPE html>
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
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 100%);
            font-family: 'Segoe UI', sans-serif;
        }}
        #gameContainer {{
            display: flex;
            gap: 20px;
            align-items: flex-start;
        }}
        h1 {{ color: #9b59b6; text-align: center; margin-bottom: 15px; text-shadow: 0 0 15px rgba(155,89,182,0.6); }}
        canvas {{ border: 3px solid #9b59b6; border-radius: 10px; box-shadow: 0 0 30px rgba(155,89,182,0.3); }}
        #sidePanel {{ color: #fff; }}
        .info-box {{ background: rgba(155,89,182,0.2); padding: 15px; border-radius: 10px; margin-bottom: 15px; }}
        .info-box h3 {{ color: #9b59b6; margin-bottom: 10px; }}
        .info-box p {{ margin: 5px 0; font-size: 14px; }}
        #nextCanvas {{ border: 2px solid #9b59b6; border-radius: 5px; display: block; margin: 10px auto; }}
        #instructions {{ color: #666; font-size: 12px; margin-top: 10px; }}
    </style>
</head>
<body>
    <div id="gameContainer">
        <div>
            <h1>{title}</h1>
            <canvas id="gameCanvas" width="{width}" height="{height}"></canvas>
        </div>
        <div id="sidePanel">
            <div class="info-box"><h3>Score</h3><p id="score">0</p></div>
            <div class="info-box"><h3>Level</h3><p id="level">1</p></div>
            <div class="info-box"><h3>Lines</h3><p id="lines">0</p></div>
            <div class="info-box"><h3>Next</h3><canvas id="nextCanvas" width="100" height="100"></canvas></div>
            <div id="instructions">Arrow Keys: Move | Up: Rotate<br>Space: Drop | P: Pause | R: Restart</div>
        </div>
    </div>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const nextCanvas = document.getElementById('nextCanvas');
        const nextCtx = nextCanvas.getContext('2d');
        
        const blockSize = {block_size};
        const cols = Math.floor(canvas.width / blockSize);
        const rows = Math.floor(canvas.height / blockSize);
        
        const pieces = [
            {{ shape: [[1,1,1,1]], color: '#00ffff' }},
            {{ shape: [[1,1],[1,1]], color: '#ffff00' }},
            {{ shape: [[0,1,0],[1,1,1]], color: '#9b59b6' }},
            {{ shape: [[1,0,0],[1,1,1]], color: '#3498db' }},
            {{ shape: [[0,0,1],[1,1,1]], color: '#e67e22' }},
            {{ shape: [[0,1,1],[1,1,0]], color: '#2ecc71' }},
            {{ shape: [[1,1,0],[0,1,1]], color: '#e74c3c' }}
        ];
        
        let board, currentPiece, nextPiece, score, level, lines, gameOver, paused;
        let dropInterval = {drop_interval};
        let lastDrop = 0;
        
        function init() {{
            board = Array(rows).fill().map(() => Array(cols).fill(0));
            score = 0;
            level = 1;
            lines = 0;
            gameOver = false;
            paused = false;
            dropInterval = {drop_interval};
            currentPiece = newPiece();
            nextPiece = newPiece();
            updateDisplay();
        }}
        
        function newPiece() {{
            const piece = pieces[Math.floor(Math.random() * pieces.length)];
            return {{
                shape: piece.shape.map(row => [...row]),
                color: piece.color,
                x: Math.floor(cols / 2) - Math.floor(piece.shape[0].length / 2),
                y: 0
            }};
        }}
        
        function rotate(shape) {{
            const n = shape.length;
            const rotated = Array(n).fill().map(() => Array(shape[0].length).fill(0));
            for(let i = 0; i < n; i++) {{
                for(let j = 0; j < shape[0].length; j++) {{
                    rotated[j][n - 1 - i] = shape[i][j];
                }}
            }}
            return rotated;
        }}
        
        function validMove(piece, offsetX, offsetY, newShape) {{
            const shape = newShape || piece.shape;
            for(let i = 0; i < shape.length; i++) {{
                for(let j = 0; j < shape[i].length; j++) {{
                    if(shape[i][j]) {{
                        const newX = piece.x + j + offsetX;
                        const newY = piece.y + i + offsetY;
                        if(newX < 0 || newX >= cols || newY >= rows) return false;
                        if(newY >= 0 && board[newY][newX]) return false;
                    }}
                }}
            }}
            return true;
        }}
        
        function lockPiece() {{
            for(let i = 0; i < currentPiece.shape.length; i++) {{
                for(let j = 0; j < currentPiece.shape[i].length; j++) {{
                    if(currentPiece.shape[i][j]) {{
                        if(currentPiece.y + i < 0) {{
                            gameOver = true;
                            return;
                        }}
                        board[currentPiece.y + i][currentPiece.x + j] = currentPiece.color;
                    }}
                }}
            }}
            clearLines();
            currentPiece = nextPiece;
            nextPiece = newPiece();
            if(!validMove(currentPiece, 0, 0)) {{
                gameOver = true;
            }}
        }}
        
        function clearLines() {{
            for(let i = rows - 1; i >= 0; i--) {{
                if(board[i].every(cell => cell !== 0)) {{
                    board.splice(i, 1);
                    board.unshift(Array(cols).fill(0));
                    lines++;
                    score += 100 * level;
                    if(lines % 10 === 0) {{
                        level++;
                        dropInterval = Math.max(100, dropInterval - 50);
                    }}
                    updateDisplay();
                    i++;
                }}
            }}
        }}
        
        function updateDisplay() {{
            document.getElementById('score').textContent = score;
            document.getElementById('level').textContent = level;
            document.getElementById('lines').textContent = lines;
        }}
        
        function drawBlock(x, y, color, context, size) {{
            context.fillStyle = color;
            context.fillRect(x * size + 1, y * size + 1, size - 2, size - 2);
            context.fillStyle = 'rgba(255,255,255,0.3)';
            context.fillRect(x * size + 1, y * size + 1, size - 2, 4);
            context.fillStyle = 'rgba(0,0,0,0.2)';
            context.fillRect(x * size + 1, y * size + size - 5, size - 2, 4);
        }}
        
        function draw() {{
            ctx.fillStyle = '#0a0a1a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            ctx.strokeStyle = '#1a1a3e';
            for(let i = 0; i <= cols; i++) {{
                ctx.beginPath();
                ctx.moveTo(i * blockSize, 0);
                ctx.lineTo(i * blockSize, canvas.height);
                ctx.stroke();
            }}
            for(let i = 0; i <= rows; i++) {{
                ctx.beginPath();
                ctx.moveTo(0, i * blockSize);
                ctx.lineTo(canvas.width, i * blockSize);
                ctx.stroke();
            }}
            
            for(let i = 0; i < rows; i++) {{
                for(let j = 0; j < cols; j++) {{
                    if(board[i][j]) {{
                        drawBlock(j, i, board[i][j], ctx, blockSize);
                    }}
                }}
            }}
            
            if(!gameOver && !paused) {{
                for(let i = 0; i < currentPiece.shape.length; i++) {{
                    for(let j = 0; j < currentPiece.shape[i].length; j++) {{
                        if(currentPiece.shape[i][j]) {{
                            drawBlock(currentPiece.x + j, currentPiece.y + i, currentPiece.color, ctx, blockSize);
                        }}
                    }}
                }}
            }}
            
            nextCtx.fillStyle = '#0a0a1a';
            nextCtx.fillRect(0, 0, nextCanvas.width, nextCanvas.height);
            const nextSize = 20;
            for(let i = 0; i < nextPiece.shape.length; i++) {{
                for(let j = 0; j < nextPiece.shape[i].length; j++) {{
                    if(nextPiece.shape[i][j]) {{
                        nextCtx.fillStyle = nextPiece.color;
                        nextCtx.fillRect(j * nextSize + 20, i * nextSize + 20, nextSize - 2, nextSize - 2);
                    }}
                }}
            }}
            
            if(gameOver) {{
                ctx.fillStyle = 'rgba(0,0,0,0.8)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#e74c3c';
                ctx.font = 'bold 36px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('GAME OVER', canvas.width/2, canvas.height/2);
                ctx.fillStyle = '#fff';
                ctx.font = '20px Arial';
                ctx.fillText('Score: ' + score, canvas.width/2, canvas.height/2 + 40);
            }}
            
            if(paused && !gameOver) {{
                ctx.fillStyle = 'rgba(0,0,0,0.5)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#9b59b6';
                ctx.font = 'bold 36px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('PAUSED', canvas.width/2, canvas.height/2);
            }}
        }}
        
        function update(timestamp) {{
            if(!lastDrop) lastDrop = timestamp;
            if(timestamp - lastDrop > dropInterval && !gameOver && !paused) {{
                if(validMove(currentPiece, 0, 1)) {{
                    currentPiece.y++;
                }} else {{
                    lockPiece();
                }}
                lastDrop = timestamp;
            }}
            draw();
            requestAnimationFrame(update);
        }}
        
        document.addEventListener('keydown', (e) => {{
            if(e.key === 'r' || e.key === 'R') {{ init(); return; }}
            if(e.key === 'p' || e.key === 'P') {{ paused = !paused; return; }}
            if(gameOver || paused) return;
            
            if(e.key === 'ArrowLeft' && validMove(currentPiece, -1, 0)) {{
                currentPiece.x--;
            }} else if(e.key === 'ArrowRight' && validMove(currentPiece, 1, 0)) {{
                currentPiece.x++;
            }} else if(e.key === 'ArrowDown' && validMove(currentPiece, 0, 1)) {{
                currentPiece.y++;
            }} else if(e.key === 'ArrowUp') {{
                const rotated = rotate(currentPiece.shape);
                if(validMove(currentPiece, 0, 0, rotated)) {{
                    currentPiece.shape = rotated;
                }}
            }} else if(e.key === ' ') {{
                while(validMove(currentPiece, 0, 1)) {{
                    currentPiece.y++;
                    score += 2;
                }}
                updateDisplay();
                lockPiece();
            }}
        }});
        
        init();
        requestAnimationFrame(update);
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


def generate_tetris_game(width: int = 300, height: int = 600, speed: int = 5, 
                         title: str = "Tetris"):
    """生成俄罗斯方块游戏HTML
    
    Args:
        width: 游戏区域宽度 (150-600)
        height: 游戏区域高度 (300-800)
        speed: 下落速度 (1-10, 越高越快)
        title: 游戏标题 (会自动转义)
    
    Returns:
        str: HTML内容
    """
    # 参数校验
    width = max(150, min(600, width))
    height = max(300, min(800, height))
    speed = max(1, min(10, speed))
    
    # XSS防护
    safe_title = html.escape(title, quote=True)
    
    # 计算方块大小，确保游戏可玩
    block_size = min(30, max(15, min(width // 10, height // 20)))
    
    # 速度与下落间隔（统一公式）
    drop_interval = max(100, 1000 - speed * 80)
    
    return TETRIS_GAME_TEMPLATE.format(
        title=safe_title,
        width=width,
        height=height,
        block_size=block_size,
        drop_interval=drop_interval
    )


def main():
    parser = argparse.ArgumentParser(
        description='Tetris Game Generator - 生成俄罗斯方块网页游戏',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python tetris_game.py                         # 默认设置
  python tetris_game.py --speed 8              # 快速下落
  python tetris_game.py -w 240 -H 480          # 自定义尺寸
  python tetris_game.py -t "My Tetris"         # 自定义标题
        '''
    )
    parser.add_argument('--width', '-w', type=int, default=300, 
                        help='游戏区域宽度 (150-600, 默认300)')
    parser.add_argument('--height', '-H', type=int, default=600, 
                        help='游戏区域高度 (300-800, 默认600)')
    parser.add_argument('--speed', '-s', type=int, default=5, choices=range(1, 11), 
                        help='下落速度 1-10 (默认5)')
    parser.add_argument('--title', '-t', type=str, default='Tetris', 
                        help='游戏标题 (默认Tetris)')
    parser.add_argument('--output', '-o', type=str, default='tetris-game.html', 
                        help='输出文件名 (默认tetris-game.html)')
    
    args = parser.parse_args()
    
    try:
        safe_output = validate_output_path(args.output)
        
        html_content = generate_tetris_game(
            width=args.width,
            height=args.height,
            speed=args.speed,
            title=args.title
        )
        
        with open(safe_output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        result = {
            "status": "success",
            "game": "tetris",
            "output_file": safe_output,
            "config": {
                "width": args.width,
                "height": args.height,
                "speed": args.speed,
                "title": args.title
            },
            "instructions": f"在浏览器中打开 {safe_output} 即可游玩。"
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
