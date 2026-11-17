#!/usr/bin/env python3
"""
Game Generator - 统一游戏生成器
整合所有游戏类型的生成功能
"""

import argparse
import json
import html
import os
import sys

# ========== 统一的速度公式 ==========
# 所有游戏使用统一的速度计算方式
# speed: 1-10, 越高越快
# interval: 毫秒，越低越快

def calculate_interval(speed: int) -> int:
    """统一的速度计算公式：interval = 500 - speed * 40
    
    speed=1  -> 460ms (慢)
    speed=5  -> 300ms (中)
    speed=10 -> 100ms (快)
    """
    return max(100, 500 - speed * 40)


# ========== 贪吃蛇模板 ==========
SNAKE_TEMPLATE = '''<!DOCTYPE html>
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
    </style>
</head>
<body>
    <div id="gameContainer">
        <h1>{title}</h1>
        <div id="score">Score: 0</div>
        <canvas id="gameCanvas" width="{width}" height="{height}"></canvas>
    </div>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreDisplay = document.getElementById('score');
        const gridSize = 20;
        const cols = Math.floor(canvas.width / gridSize);
        const rows = Math.floor(canvas.height / gridSize);
        const interval = {interval};
        
        let snake, direction, food, score, gameOver, paused;
        
        function init() {{
            snake = [{{x: 5, y: 5}}];
            direction = {{x: 1, y: 0}};
            score = 0;
            gameOver = false;
            paused = false;
            scoreDisplay.textContent = 'Score: 0';
            placeFood();
        }}
        
        function placeFood() {{
            food = {{
                x: Math.floor(Math.random() * cols),
                y: Math.floor(Math.random() * rows)
            }};
            while (snake.some(seg => seg.x === food.x && seg.y === food.y)) {{
                food.x = Math.floor(Math.random() * cols);
                food.y = Math.floor(Math.random() * rows);
            }}
        }}
        
        function update() {{
            if (paused || gameOver) return;
            
            const head = {{
                x: snake[0].x + direction.x,
                y: snake[0].y + direction.y
            }};
            
            if (head.x < 0 || head.x >= cols || head.y < 0 || head.y >= rows) {{
                gameOver = true;
                return;
            }}
            
            if (snake.some(seg => seg.x === head.x && seg.y === head.y)) {{
                gameOver = true;
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
            
            ctx.fillStyle = '#ff4757';
            ctx.fillRect(food.x * gridSize + 2, food.y * gridSize + 2, gridSize - 4, gridSize - 4);
            
            snake.forEach((segment, index) => {{
                ctx.fillStyle = index === 0 ? '#00ff88' : '#00cc6a';
                ctx.fillRect(segment.x * gridSize + 1, segment.y * gridSize + 1, gridSize - 2, gridSize - 2);
            }});
            
            if (gameOver) {{
                ctx.fillStyle = 'rgba(0,0,0,0.7)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#ff4757';
                ctx.font = 'bold 36px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('GAME OVER', canvas.width/2, canvas.height/2);
            }}
            
            requestAnimationFrame(draw);
        }}
        
        document.addEventListener('keydown', (e) => {{
            if (e.key === ' ' || e.key === 'p') {{ paused = !paused; return; }}
            if (e.key === 'r' || e.key === 'R') {{ init(); return; }}
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
        
        init();
        setInterval(update, interval);
        draw();
    </script>
</body>
</html>'''


# ========== 打砖块模板 ==========
BREAKOUT_TEMPLATE = '''<!DOCTYPE html>
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
        h1 {{ color: #3498db; margin-bottom: 15px; }}
        canvas {{ border: 3px solid #3498db; border-radius: 10px; }}
        #score {{ color: #fff; font-size: 20px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div id="gameContainer">
        <h1>{title}</h1>
        <div id="score">Score: 0 | Lives: {lives}</div>
        <canvas id="gameCanvas" width="{width}" height="{height}"></canvas>
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
        
        let paddleX = (canvas.width - 100) / 2;
        const ballRadius = 10;
        let ballX = canvas.width / 2;
        let ballY = canvas.height - 50;
        let ballDX = {ball_speed};
        let ballDY = -{ball_speed};
        
        let score = 0;
        let lives = {lives};
        let gameOver = false;
        let rightPressed = false;
        let leftPressed = false;
        
        const bricks = [];
        const colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#3498db'];
        
        for(let c = 0; c < brickColumnCount; c++) {{
            bricks[c] = [];
            for(let r = 0; r < brickRowCount; r++) {{
                bricks[c][r] = {{ x: 0, y: 0, status: 1, color: colors[r % colors.length] }};
            }}
        }}
        
        document.addEventListener('keydown', (e) => {{
            if(e.key === 'ArrowRight') rightPressed = true;
            if(e.key === 'ArrowLeft') leftPressed = true;
            if(e.key === 'r' || e.key === 'R') location.reload();
        }});
        document.addEventListener('keyup', (e) => {{
            if(e.key === 'ArrowRight') rightPressed = false;
            if(e.key === 'ArrowLeft') leftPressed = false;
        }});
        
        function draw() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
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
            
            ctx.beginPath();
            ctx.arc(ballX, ballY, ballRadius, 0, Math.PI * 2);
            ctx.fillStyle = '#fff';
            ctx.fill();
            ctx.closePath();
            
            ctx.fillStyle = '#3498db';
            ctx.fillRect(paddleX, canvas.height - 15, 100, 15);
            
            if(ballX + ballDX > canvas.width - ballRadius || ballX + ballDX < ballRadius) ballDX = -ballDX;
            if(ballY + ballDY < ballRadius) ballDY = -ballDY;
            else if(ballY + ballDY > canvas.height - ballRadius - 15) {{
                if(ballX > paddleX && ballX < paddleX + 100) ballDY = -ballDY;
            }}
            
            if(ballY > canvas.height) {{
                lives--;
                scoreDisplay.textContent = 'Score: ' + score + ' | Lives: ' + lives;
                if(!lives) gameOver = true;
                else {{
                    ballX = canvas.width / 2;
                    ballY = canvas.height - 50;
                    ballDX = {ball_speed} * (Math.random() > 0.5 ? 1 : -1);
                    ballDY = -{ball_speed};
                }}
            }}
            
            for(let c = 0; c < brickColumnCount; c++) {{
                for(let r = 0; r < brickRowCount; r++) {{
                    if(bricks[c][r].status === 1) {{
                        if(ballX > bricks[c][r].x && ballX < bricks[c][r].x + brickWidth &&
                           ballY > bricks[c][r].y && ballY < bricks[c][r].y + brickHeight) {{
                            ballDY = -ballDY;
                            bricks[c][r].status = 0;
                            score += 10;
                            scoreDisplay.textContent = 'Score: ' + score + ' | Lives: ' + lives;
                        }}
                    }}
                }}
            }}
            
            ballX += ballDX;
            ballY += ballDY;
            
            if(rightPressed && paddleX < canvas.width - 100) paddleX += 7;
            else if(leftPressed && paddleX > 0) paddleX -= 7;
            
            if(gameOver) {{
                ctx.fillStyle = 'rgba(0,0,0,0.8)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#e74c3c';
                ctx.font = 'bold 36px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('GAME OVER', canvas.width/2, canvas.height/2);
            }}
            
            if(!gameOver) requestAnimationFrame(draw);
        }}
        
        draw();
    </script>
</body>
</html>'''


# ========== 俄罗斯方块模板 ==========
TETRIS_TEMPLATE = '''<!DOCTYPE html>
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
        #gameContainer {{ display: flex; gap: 20px; }}
        h1 {{ color: #9b59b6; text-align: center; margin-bottom: 15px; }}
        canvas {{ border: 3px solid #9b59b6; border-radius: 10px; }}
        #sidePanel {{ color: #fff; }}
        .info-box {{ background: rgba(155,89,182,0.2); padding: 15px; border-radius: 10px; margin-bottom: 10px; }}
        .info-box h3 {{ color: #9b59b6; margin-bottom: 5px; }}
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
        </div>
    </div>
    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const blockSize = {block_size};
        const cols = Math.floor(canvas.width / blockSize);
        const rows = Math.floor(canvas.height / blockSize);
        const dropInterval = {drop_interval};
        
        const pieces = [
            {{ shape: [[1,1,1,1]], color: '#00ffff' }},
            {{ shape: [[1,1],[1,1]], color: '#ffff00' }},
            {{ shape: [[0,1,0],[1,1,1]], color: '#9b59b6' }},
            {{ shape: [[1,0,0],[1,1,1]], color: '#3498db' }},
            {{ shape: [[0,0,1],[1,1,1]], color: '#e67e22' }}
        ];
        
        let board, currentPiece, score, level, gameOver, lastDrop;
        
        function init() {{
            board = Array(rows).fill().map(() => Array(cols).fill(0));
            score = 0;
            level = 1;
            gameOver = false;
            lastDrop = Date.now();
            currentPiece = newPiece();
            updateDisplay();
        }}
        
        function newPiece() {{
            const piece = pieces[Math.floor(Math.random() * pieces.length)];
            return {{
                shape: piece.shape.map(row => [...row]),
                color: piece.color,
                x: Math.floor(cols / 2) - 1,
                y: 0
            }};
        }}
        
        function rotate(shape) {{
            const n = shape.length;
            return shape[0].map((_, i) => shape.map(row => row[i])).reverse();
        }}
        
        function validMove(piece, dx, dy, newShape) {{
            const shape = newShape || piece.shape;
            for(let i = 0; i < shape.length; i++) {{
                for(let j = 0; j < shape[i].length; j++) {{
                    if(shape[i][j]) {{
                        const nx = piece.x + j + dx;
                        const ny = piece.y + i + dy;
                        if(nx < 0 || nx >= cols || ny >= rows) return false;
                        if(ny >= 0 && board[ny][nx]) return false;
                    }}
                }}
            }}
            return true;
        }}
        
        function lockPiece() {{
            for(let i = 0; i < currentPiece.shape.length; i++) {{
                for(let j = 0; j < currentPiece.shape[i].length; j++) {{
                    if(currentPiece.shape[i][j]) {{
                        if(currentPiece.y + i < 0) {{ gameOver = true; return; }}
                        board[currentPiece.y + i][currentPiece.x + j] = currentPiece.color;
                    }}
                }}
            }}
            clearLines();
            currentPiece = newPiece();
            if(!validMove(currentPiece, 0, 0)) gameOver = true;
        }}
        
        function clearLines() {{
            for(let i = rows - 1; i >= 0; i--) {{
                if(board[i].every(cell => cell !== 0)) {{
                    board.splice(i, 1);
                    board.unshift(Array(cols).fill(0));
                    score += 100;
                    level = Math.floor(score / 500) + 1;
                    updateDisplay();
                    i++;
                }}
            }}
        }}
        
        function updateDisplay() {{
            document.getElementById('score').textContent = score;
            document.getElementById('level').textContent = level;
        }}
        
        function draw() {{
            ctx.fillStyle = '#0a0a1a';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            for(let i = 0; i < rows; i++) {{
                for(let j = 0; j < cols; j++) {{
                    if(board[i][j]) {{
                        ctx.fillStyle = board[i][j];
                        ctx.fillRect(j * blockSize, i * blockSize, blockSize - 1, blockSize - 1);
                    }}
                }}
            }}
            
            if(!gameOver) {{
                for(let i = 0; i < currentPiece.shape.length; i++) {{
                    for(let j = 0; j < currentPiece.shape[i].length; j++) {{
                        if(currentPiece.shape[i][j]) {{
                            ctx.fillStyle = currentPiece.color;
                            ctx.fillRect((currentPiece.x + j) * blockSize, (currentPiece.y + i) * blockSize, blockSize - 1, blockSize - 1);
                        }}
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
            }}
            
            requestAnimationFrame(draw);
        }}
        
        document.addEventListener('keydown', (e) => {{
            if(gameOver) return;
            if(e.key === 'ArrowLeft' && validMove(currentPiece, -1, 0)) currentPiece.x--;
            if(e.key === 'ArrowRight' && validMove(currentPiece, 1, 0)) currentPiece.x++;
            if(e.key === 'ArrowDown' && validMove(currentPiece, 0, 1)) currentPiece.y++;
            if(e.key === 'ArrowUp') {{
                const rotated = rotate(currentPiece.shape);
                if(validMove(currentPiece, 0, 0, rotated)) currentPiece.shape = rotated;
            }}
            if(e.key === ' ') {{
                while(validMove(currentPiece, 0, 1)) currentPiece.y++;
                lockPiece();
            }}
        }});
        
        function update() {{
            if(gameOver) return;
            if(Date.now() - lastDrop > dropInterval) {{
                if(validMove(currentPiece, 0, 1)) currentPiece.y++;
                else lockPiece();
                lastDrop = Date.now();
            }}
            setTimeout(update, 50);
        }}
        
        init();
        update();
        draw();
    </script>
</body>
</html>'''


# ========== Three.js 3D模板 ==========
THREE_JS_CDN = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"

THREE_JS_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com">
    <style>
        * {{ margin: 0; padding: 0; }}
        body {{ overflow: hidden; font-family: 'Segoe UI', sans-serif; }}
        #info {{
            position: absolute;
            top: 20px;
            left: 20px;
            color: #fff;
            background: rgba(0,0,0,0.7);
            padding: 15px;
            border-radius: 10px;
        }}
        #info h3 {{ margin-bottom: 10px; color: #00ff88; }}
    </style>
</head>
<body>
    <div id="info">
        <h3>{title}</h3>
        <p>Controls: WASD to move</p>
    </div>
    <script src="{three_js_url}"></script>
    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);
        
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        camera.position.set(0, 5, 10);
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        scene.add(new THREE.AmbientLight(0x404040));
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(5, 10, 5);
        scene.add(dirLight);
        
        const floorGeometry = new THREE.PlaneGeometry(50, 50);
        const floorMaterial = new THREE.MeshStandardMaterial({{ color: 0x222233, side: THREE.DoubleSide }});
        scene.add(new THREE.Mesh(floorGeometry, floorMaterial));
        scene.add(new THREE.GridHelper(50, 50, 0x00ff88, 0x333355));
        
        const playerGeometry = new THREE.SphereGeometry(0.5, 32, 32);
        const playerMaterial = new THREE.MeshStandardMaterial({{ color: 0x00ff88, emissive: 0x004400 }});
        const player = new THREE.Mesh(playerGeometry, playerMaterial);
        player.position.y = 0.5;
        scene.add(player);
        
        const obstacles = [];
        const obstacleGeometry = new THREE.BoxGeometry(1, 1, 1);
        for(let i = 0; i < 10; i++) {{
            const material = new THREE.MeshStandardMaterial({{ color: 0x6666ff }});
            const obstacle = new THREE.Mesh(obstacleGeometry, material);
            obstacle.position.set((Math.random() - 0.5) * 20, 0.5, (Math.random() - 0.5) * 20);
            scene.add(obstacle);
            obstacles.push({{ mesh: obstacle, radius: 0.7 }});
        }}
        
        const keys = {{}};
        document.addEventListener('keydown', (e) => keys[e.key] = true);
        document.addEventListener('keyup', (e) => keys[e.key] = false);
        
        function animate() {{
            requestAnimationFrame(animate);
            
            const speed = 0.15;
            if(keys['w'] || keys['ArrowUp']) player.position.z -= speed;
            if(keys['s'] || keys['ArrowDown']) player.position.z += speed;
            if(keys['a'] || keys['ArrowLeft']) player.position.x -= speed;
            if(keys['d'] || keys['ArrowRight']) player.position.x += speed;
            
            player.position.x = Math.max(-24, Math.min(24, player.position.x));
            player.position.z = Math.max(-24, Math.min(24, player.position.z));
            
            for(const obs of obstacles) {{
                const dx = player.position.x - obs.mesh.position.x;
                const dz = player.position.z - obs.mesh.position.z;
                if(Math.sqrt(dx*dx + dz*dz) < obs.radius + 0.5) {{
                    if(dx > 0) player.position.x += 0.5;
                    else player.position.x -= 0.5;
                }}
            }}
            
            camera.position.x = player.position.x;
            camera.position.z = player.position.z + 10;
            camera.lookAt(player.position);
            
            renderer.render(scene, camera);
        }}
        
        animate();
        
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
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
    """生成贪吃蛇游戏"""
    width = max(200, min(1920, width))
    height = max(200, min(1080, height))
    speed = max(1, min(10, speed))
    
    safe_title = html.escape(title, quote=True)
    interval = calculate_interval(speed)
    
    return SNAKE_TEMPLATE.format(
        title=safe_title,
        width=width,
        height=height,
        interval=interval
    )


def generate_breakout_game(width: int = 800, height: int = 600, speed: int = 5, title: str = "Breakout"):
    """生成打砖块游戏"""
    width = max(200, min(1920, width))
    height = max(200, min(1080, height))
    speed = max(1, min(10, speed))
    
    safe_title = html.escape(title, quote=True)
    
    # 根据速度调整难度
    if speed <= 3:
        brick_rows, lives, ball_speed = 4, 5, 3
    elif speed <= 7:
        brick_rows, lives, ball_speed = 6, 3, 4
    else:
        brick_rows, lives, ball_speed = 8, 2, 6
    
    return BREAKOUT_TEMPLATE.format(
        title=safe_title,
        width=width,
        height=height,
        brick_rows=brick_rows,
        lives=lives,
        ball_speed=ball_speed
    )


def generate_tetris_game(width: int = 300, height: int = 600, speed: int = 5, title: str = "Tetris"):
    """生成俄罗斯方块游戏"""
    width = max(150, min(600, width))
    height = max(300, min(800, height))
    speed = max(1, min(10, speed))
    
    safe_title = html.escape(title, quote=True)
    block_size = min(30, max(15, min(width // 10, height // 20)))
    drop_interval = calculate_interval(speed)
    
    return TETRIS_TEMPLATE.format(
        title=safe_title,
        width=width,
        height=height,
        block_size=block_size,
        drop_interval=drop_interval
    )


def generate_3d_scene(width: int = 800, height: int = 600, speed: int = 5, title: str = "3D Game"):
    """生成3D游戏"""
    safe_title = html.escape(title, quote=True)
    
    return THREE_JS_TEMPLATE.format(
        title=safe_title,
        three_js_url=THREE_JS_CDN
    )


# 游戏注册表
GENERATORS = {
    'snake': generate_snake_game,
    'breakout': generate_breakout_game,
    'tetris': generate_tetris_game,
    '3d-sphere': generate_3d_scene,
    '3d-cube': generate_3d_scene,
    '3d-maze': generate_3d_scene,
}


def main():
    parser = argparse.ArgumentParser(
        description='Game Generator - 统一游戏生成器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
支持的类型:
  snake      - 贪吃蛇
  breakout   - 打砖块
  tetris     - 俄罗斯方块
  3d-sphere  - 3D弹球
  3d-cube    - 3D跑酷
  3d-maze    - 3D迷宫

示例:
  python game_generator.py --type snake
  python game_generator.py --type breakout --speed 8
  python game_generator.py -t tetris -w 240 -H 480
        '''
    )
    parser.add_argument('--type', type=str, required=True,
                        help='游戏类型: snake, breakout, tetris, 3d-sphere, 3d-cube, 3d-maze')
    parser.add_argument('--width', '-w', type=int, default=800,
                        help='画布宽度 (默认800)')
    parser.add_argument('--height', '-H', type=int, default=600,
                        help='画布高度 (默认600)')
    parser.add_argument('--speed', '-s', type=int, default=5, choices=range(1, 11),
                        help='游戏速度 1-10 (默认5)')
    parser.add_argument('--title', '-t', type=str, default='Game',
                        help='游戏标题 (默认Game)')
    parser.add_argument('--output', '-o', type=str, default='game.html',
                        help='输出文件名 (默认game.html)')
    
    args = parser.parse_args()
    
    try:
        safe_output = validate_output_path(args.output)
        
        if args.type not in GENERATORS:
            print(json.dumps({
                "status": "error",
                "error": f"Unknown game type: {args.type}",
                "help": f"Available types: {list(GENERATORS.keys())}"
            }, ensure_ascii=False))
            sys.exit(1)
        
        html_content = GENERATORS[args.type](
            width=args.width,
            height=args.height,
            speed=args.speed,
            title=args.title
        )
        
        with open(safe_output, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(json.dumps({
            "status": "success",
            "game": args.type,
            "output_file": safe_output,
            "file_size": len(html_content),
            "config": {
                "type": args.type,
                "width": args.width,
                "height": args.height,
                "speed": args.speed,
                "title": args.title
            }
        }, ensure_ascii=False))
        
    except ValueError as e:
        print(json.dumps({
            "status": "error",
            "error": str(e),
            "help": "检查参数是否正确"
        }, ensure_ascii=False))
        sys.exit(1)
    except IOError as e:
        print(json.dumps({
            "status": "error",
            "error": f"文件写入失败: {str(e)}",
            "help": "检查目录权限"
        }, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
