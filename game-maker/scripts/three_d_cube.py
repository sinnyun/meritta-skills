#!/usr/bin/env python3
"""
3D 方块跑酷游戏生成器
无限跑酷，躲避障碍物
"""

import argparse
import json
import os
import html

THREE_JS_URL = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r160/three.min.js"

CUBE_GAME_TEMPLATE = '''<!DOCTYPE html>
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
        #info h3 {{ margin-bottom: 10px; color: #ff6b6b; }}
        #gameOver {{
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
        #gameOver h2 {{ color: #ff6b6b; font-size: 48px; margin-bottom: 20px; }}
        #gameOver p {{ font-size: 24px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div id="info">
        <h3>{title}</h3>
        <p>Score: <span id="score">0</span></p>
        <p>Distance: <span id="distance">0</span>m</p>
        <p>Controls: A/D or Left/Right to move</p>
    </div>
    <div id="gameOver">
        <h2>GAME OVER</h2>
        <p>Final Score: <span id="finalScore">0</span></p>
        <p>Press R to Restart</p>
    </div>
    <script src="{three_js_url}"></script>
    <script>
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0f0f23);
        
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        scene.add(new THREE.AmbientLight(0x404040));
        const light = new THREE.DirectionalLight(0xffffff, 1);
        light.position.set(0, 10, 10);
        scene.add(light);
        
        const player = new THREE.Mesh(
            new THREE.BoxGeometry(1, 1, 1),
            new THREE.MeshStandardMaterial({{ color: 0x00ffff, emissive: 0x004444 }})
        );
        player.position.set(0, 0.5, 0);
        scene.add(player);
        
        const roadLength = 200;
        const roadGeometry = new THREE.PlaneGeometry(12, roadLength);
        const road = new THREE.Mesh(road, new THREE.MeshStandardMaterial({{ color: 0x222233 }}));
        road.rotation.x = -Math.PI / 2;
        road.position.z = -roadLength / 2 + 10;
        scene.add(road);
        
        const obstacles = [];
        const coins = [];
        let score = 0;
        let distance = 0;
        let gameOver = false;
        let playerLane = 0;
        const laneWidth = 3;
        const keys = {{}};
        
        document.addEventListener('keydown', (e) => keys[e.key] = true);
        document.addEventListener('keyup', (e) => keys[e.key] = false);
        
        function spawnObstacle() {{
            const lane = Math.floor(Math.random() * 3) - 1;
            const obstacle = new THREE.Mesh(
                new THREE.BoxGeometry(2, 2, 2),
                new THREE.MeshStandardMaterial({{ color: 0xff4444 }})
            );
            obstacle.position.set(lane * laneWidth, 1, -100);
            scene.add(obstacle);
            obstacles.push(obstacle);
        }}
        
        function spawnCoin() {{
            const lane = Math.floor(Math.random() * 3) - 1;
            const coin = new THREE.Mesh(
                new THREE.TorusGeometry(0.4, 0.1, 8, 16),
                new THREE.MeshStandardMaterial({{ color: 0xffdd00, emissive: 0x443300 }})
            );
            coin.position.set(lane * laneWidth, 1, -100);
            scene.add(coin);
            coins.push(coin);
        }}
        
        for(let i = 0; i < 5; i++) spawnObstacle();
        
        function updateDisplay() {{
            document.getElementById('score').textContent = score;
            document.getElementById('distance').textContent = Math.floor(distance);
        }}
        
        function checkCollision(pos1, pos2) {{
            return Math.abs(pos1.x - pos2.x) < 1.5 && Math.abs(pos1.z - pos2.z) < 1.5;
        }}
        
        function animate() {{
            requestAnimationFrame(animate);
            if (gameOver) return;
            
            distance += 0.1;
            
            if(keys['a'] || keys['A'] || keys['ArrowLeft']) playerLane = Math.max(-1, playerLane - 1);
            if(keys['d'] || keys['D'] || keys['ArrowRight']) playerLane = Math.min(1, playerLane + 1);
            
            player.position.x += (playerLane * laneWidth - player.position.x) * 0.1;
            
            for(let i = obstacles.length - 1; i >= 0; i--) {{
                obstacles[i].position.z += 0.3;
                obstacles[i].rotation.y += 0.02;
                
                if(checkCollision(player.position, obstacles[i].position)) {{
                    gameOver = true;
                    document.getElementById('finalScore').textContent = score;
                    document.getElementById('gameOver').style.display = 'block';
                }}
                
                if(obstacles[i].position.z > 10) {{
                    scene.remove(obstacles[i]);
                    obstacles.splice(i, 1);
                    score += 5;
                }}
            }}
            
            for(let i = coins.length - 1; i >= 0; i--) {{
                coins[i].position.z += 0.3;
                coins[i].rotation.x += 0.05;
                coins[i].rotation.y += 0.02;
                
                if(checkCollision(player.position, coins[i].position)) {{
                    scene.remove(coins[i]);
                    coins.splice(i, 1);
                    score += 20;
                }} else if(coins[i].position.z > 10) {{
                    scene.remove(coins[i]);
                    coins.splice(i, 1);
                }}
            }}
            
            if(Math.random() < 0.02) spawnObstacle();
            if(Math.random() < 0.01) spawnCoin();
            
            camera.position.set(player.position.x, 5, 10);
            camera.lookAt(player.position.x, 0, -10);
            
            updateDisplay();
            renderer.render(scene, camera);
        }}
        
        document.addEventListener('keydown', (e) => {{
            if(e.key === 'r' || e.key === 'R') {{
                if(gameOver) {{
                    gameOver = false;
                    score = 0;
                    distance = 0;
                    playerLane = 0;
                    player.position.set(0, 0.5, 0);
                    for(const o of obstacles) scene.remove(o);
                    obstacles.length = 0;
                    for(const c of coins) scene.remove(c);
                    coins.length = 0;
                    for(let i = 0; i < 5; i++) spawnObstacle();
                    document.getElementById('gameOver').style.display = 'none';
                }}
            }}
        }});
        
        animate();
        
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>'''


def generate_cube_game(title: str, difficulty: str, output: str) -> dict:
    """生成3D方块跑酷游戏"""
    title = html.escape(title)
    
    # 路径安全校验：禁止路径遍历
    if ".." in output:
        raise ValueError(f"Path traversal detected: {output}")
    
    html_content = CUBE_GAME_TEMPLATE.format(
        title=title,
        three_js_url=THREE_JS_URL
    )
    
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return {
        "status": "success",
        "game_type": "3d-cube",
        "title": title,
        "output_file": output,
        "controls": ["A/D or Left/Right: change lane", "R: restart"],
        "features": ["endless_runner", "obstacle_avoidance", "coin_collection"]
    }


def main():
    parser = argparse.ArgumentParser(description='Generate 3D Cube Runner Game')
    parser.add_argument('--title', default='Cube Runner 3D', help='Game title')
    parser.add_argument('--difficulty', '-d', default='normal', choices=['easy', 'normal', 'hard'])
    parser.add_argument('--output', '-o', default='cube3d.html', help='Output file')
    
    args = parser.parse_args()
    
    try:
        result = generate_cube_game(args.title, args.difficulty, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
        exit(1)


if __name__ == '__main__':
    main()
