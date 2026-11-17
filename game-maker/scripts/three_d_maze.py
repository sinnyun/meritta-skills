#!/usr/bin/env python3
"""
3D 第一人称迷宫游戏生成器
探索迷宫，找到出口
"""

import argparse
import json
import os
import html

THREE_JS_URL = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r160/three.min.js"

MAZE_GAME_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
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
        #info h3 {{ margin-bottom: 10px; color: #ffd93d; }}
        #minimap {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            background: rgba(0,0,0,0.8);
            padding: 10px;
            border-radius: 10px;
        }}
        #winScreen {{
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #fff;
            text-align: center;
            background: rgba(0,0,0,0.9);
            padding: 40px;
            border-radius: 20px;
        }}
        #winScreen h2 {{ color: #00ff88; font-size: 36px; margin-bottom: 20px; }}
        .btn {{
            background: linear-gradient(135deg, #00ff88, #00aa55);
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            color: #fff;
            border-radius: 30px;
            cursor: pointer;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div id="info">
        <h3>{title}</h3>
        <p>Time: <span id="time">0</span>s</p>
        <p>Steps: <span id="steps">0</span></p>
        <p>WASD/Arrows to move</p>
    </div>
    <div id="minimap"><canvas id="mapCanvas" width="150" height="150"></canvas></div>
    <div id="winScreen">
        <h2>YOU WIN!</h2>
        <p>Time: <span id="finalTime">0</span>s</p>
        <p>Steps: <span id="finalSteps">0</span></p>
        <button class="btn" onclick="restartGame()">PLAY AGAIN</button>
    </div>
    <script src="{three_js_url}"></script>
    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);
        
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth/window.innerHeight, 0.1, 1000);
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        scene.add(new THREE.AmbientLight(0x404040));
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.6);
        dirLight.position.set(5, 10, 5);
        scene.add(dirLight);
        
        const mapSize = 15;
        const cellSize = 4;
        const maze = [];
        const walls = [];
        
        function generateMaze() {{
            for(let i = 0; i < mapSize; i++) {{
                maze[i] = [];
                for(let j = 0; j < mapSize; j++) {{
                    maze[i][j] = 0;
                }}
            }}
            
            function carve(x, y) {{
                maze[y][x] = 1;
                const dirs = [[0,-2],[0,2],[-2,0],[2,0]].sort(() => Math.random() - 0.5);
                for(const [dx, dy] of dirs) {{
                    const nx = x + dx, ny = y + dy;
                    if(nx > 0 && nx < mapSize - 1 && ny > 0 && ny < mapSize - 1 && maze[ny][nx] === 0) {{
                        maze[y + dy/2][x + dx/2] = 1;
                        carve(nx, ny);
                    }}
                }}
            }}
            carve(1, 1);
            maze[mapSize-2][mapSize-2] = 1;
        }}
        
        generateMaze();
        
        const wallGeometry = new THREE.BoxGeometry(cellSize, cellSize * 2, cellSize);
        const wallMaterial = new THREE.MeshStandardMaterial({{ color: 0x4444aa }});
        
        for(let i = 0; i < mapSize; i++) {{
            for(let j = 0; j < mapSize; j++) {{
                if(maze[i][j] === 0) {{
                    const wall = new THREE.Mesh(wallGeometry, wallMaterial);
                    wall.position.set(j * cellSize - mapSize * cellSize / 2, cellSize, i * cellSize - mapSize * cellSize / 2);
                    scene.add(wall);
                    walls.push({{ mesh: wall, x: wall.position.x, z: wall.position.z, radius: cellSize / 2 }});
                }}
            }}
        }}
        
        const playerGeometry = new THREE.SphereGeometry(0.5, 16, 16);
        const playerMaterial = new THREE.MeshStandardMaterial({{ color: 0x00ff88 }});
        const player = new THREE.Mesh(playerGeometry, playerMaterial);
        player.position.set(cellSize - mapSize * cellSize / 2, 1, cellSize - mapSize * cellSize / 2);
        scene.add(player);
        
        const goalGeometry = new THREE.BoxGeometry(2, 3, 2);
        const goalMaterial = new THREE.MeshStandardMaterial({{ color: 0xffdd00, emissive: 0x443300 }});
        const goal = new THREE.Mesh(goalGeometry, goalMaterial);
        goal.position.set((mapSize - 2) * cellSize - mapSize * cellSize / 2, 1.5, (mapSize - 2) * cellSize - mapSize * cellSize / 2);
        scene.add(goal);
        
        let time = 0;
        let steps = 0;
        let gameWon = false;
        const keys = {{}};
        
        document.addEventListener('keydown', (e) => keys[e.key] = true);
        document.addEventListener('keyup', (e) => keys[e.key] = false);
        
        function checkWallCollision(newX, newZ) {{
            for(const wall of walls) {{
                const dx = newX - wall.x;
                const dz = newZ - wall.z;
                if(Math.sqrt(dx*dx + dz*dz) < wall.radius + 0.5) return true;
            }}
            return false;
        }}
        
        function updateMinimap() {{
            const canvas = document.getElementById('mapCanvas');
            const ctx = canvas.getContext('2d');
            ctx.fillStyle = '#000';
            ctx.fillRect(0, 0, 150, 150);
            
            const scale = 150 / (mapSize * cellSize);
            const offsetX = 75 - player.position.x * scale;
            const offsetZ = 75 - player.position.z * scale;
            
            ctx.fillStyle = '#4444aa';
            for(let i = 0; i < mapSize; i++) {{
                for(let j = 0; j < mapSize; j++) {{
                    if(maze[i][j] === 0) {{
                        ctx.fillRect(j * cellSize * scale + offsetX, i * cellSize * scale + offsetZ, cellSize * scale, cellSize * scale);
                    }}
                }}
            }}
            
            ctx.fillStyle = '#00ff88';
            ctx.beginPath();
            ctx.arc(75, 75, 5, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = '#ffdd00';
            ctx.beginPath();
            ctx.arc((mapSize - 2) * cellSize * scale + offsetX, (mapSize - 2) * cellSize * scale + offsetZ, 5, 0, Math.PI * 2);
            ctx.fill();
        }}
        
        function checkWin() {{
            const dx = player.position.x - goal.position.x;
            const dz = player.position.z - goal.position.z;
            if(Math.sqrt(dx*dx + dz*dz) < 2) {{
                gameWon = true;
                document.getElementById('finalTime').textContent = time;
                document.getElementById('finalSteps').textContent = steps;
                document.getElementById('winScreen').style.display = 'block';
            }}
        }}
        
        function restartGame() {{
            player.position.set(cellSize - mapSize * cellSize / 2, 1, cellSize - mapSize * cellSize / 2);
            time = 0;
            steps = 0;
            gameWon = false;
            generateMaze();
            document.getElementById('winScreen').style.display = 'none';
        }}
        
        function animate() {{
            requestAnimationFrame(animate);
            
            if(!gameWon) {{
                time += 0.016;
                document.getElementById('time').textContent = Math.floor(time);
                
                const speed = 0.1;
                let moved = false;
                
                if(keys['w'] || keys['W'] || keys['ArrowUp']) {{
                    if(!checkWallCollision(player.position.x, player.position.z - speed)) {{
                        player.position.z -= speed;
                        moved = true;
                    }}
                }}
                if(keys['s'] || keys['S'] || keys['ArrowDown']) {{
                    if(!checkWallCollision(player.position.x, player.position.z + speed)) {{
                        player.position.z += speed;
                        moved = true;
                    }}
                }}
                if(keys['a'] || keys['A'] || keys['ArrowLeft']) {{
                    if(!checkWallCollision(player.position.x - speed, player.position.z)) {{
                        player.position.x -= speed;
                        moved = true;
                    }}
                }}
                if(keys['d'] || keys['D'] || keys['ArrowRight']) {{
                    if(!checkWallCollision(player.position.x + speed, player.position.z)) {{
                        player.position.x += speed;
                        moved = true;
                    }}
                }}
                
                if(moved) steps++;
                
                camera.position.set(player.position.x, 2, player.position.z + 5);
                camera.lookAt(player.position.x, 1.5, player.position.z);
                
                checkWin();
                updateMinimap();
            }}
            
            goal.rotation.y += 0.02;
            
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


def generate_maze_game(title: str, difficulty: str, output: str) -> dict:
    """生成3D第一人称迷宫游戏"""
    title = html.escape(title)
    
    # 路径安全校验：禁止路径遍历
    if ".." in output:
        raise ValueError(f"Path traversal detected: {output}")
    
    html_content = MAZE_GAME_TEMPLATE.format(
        title=title,
        three_js_url=THREE_JS_URL
    )
    
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return {
        "status": "success",
        "game_type": "3d-maze",
        "title": title,
        "output_file": output,
        "controls": ["WASD/Arrows: move"],
        "features": ["procedural_maze", "first_person_view", "minimap", "timer"]
    }


def main():
    parser = argparse.ArgumentParser(description='Generate 3D Maze Game')
    parser.add_argument('--title', default='3D Maze', help='Game title')
    parser.add_argument('--difficulty', '-d', default='normal', choices=['easy', 'normal', 'hard'])
    parser.add_argument('--output', '-o', default='maze3d.html', help='Output file')
    
    args = parser.parse_args()
    
    try:
        result = generate_maze_game(args.title, args.difficulty, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
        exit(1)


if __name__ == '__main__':
    main()
