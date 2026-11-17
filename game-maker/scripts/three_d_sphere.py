#!/usr/bin/env python3
"""
3D 弹球收集游戏生成器
控制角色收集物品，躲避障碍物
"""

import argparse
import json
import os
import html

THREE_JS_URL = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r160/three.min.js"

SPHERE_GAME_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ overflow: hidden; font-family: 'Segoe UI', sans-serif; background: #1a1a2e; }}
        #ui {{
            position: absolute;
            top: 20px;
            left: 20px;
            color: #fff;
            background: rgba(0,0,0,0.7);
            padding: 15px;
            border-radius: 10px;
        }}
        #ui h3 {{ color: #00ffff; margin-bottom: 10px; }}
        #ui p {{ margin: 5px 0; }}
        #startScreen, #gameOverScreen {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            color: #fff;
            background: rgba(0,0,0,0.9);
            padding: 40px 60px;
            border-radius: 20px;
        }}
        #startScreen h1, #gameOverScreen h2 {{ color: #00ffff; margin-bottom: 20px; }}
        #startScreen p {{ margin: 10px 0; color: #aaa; }}
        .btn {{
            background: linear-gradient(135deg, #00ffff, #0088ff);
            border: none;
            padding: 15px 40px;
            font-size: 18px;
            color: #fff;
            border-radius: 30px;
            cursor: pointer;
            margin-top: 20px;
        }}
        .btn:hover {{ transform: scale(1.05); }}
        #gameOverScreen {{ display: none; }}
    </style>
</head>
<body>
    <div id="ui">
        <h3>{title}</h3>
        <p>Score: <span id="score">0</span></p>
        <p>Level: <span id="level">1</span></p>
        <p>WASD to move</p>
    </div>
    
    <div id="startScreen">
        <h1>3D BALL COLLECTION</h1>
        <p>Collect items, avoid obstacles!</p>
        <button class="btn" onclick="startGame()">START</button>
    </div>
    
    <div id="gameOverScreen">
        <h2>GAME OVER</h2>
        <p>Final Score: <span id="finalScore">0</span></p>
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
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(5, 10, 5);
        scene.add(dirLight);
        
        const playerGeometry = new THREE.SphereGeometry(0.5, 16, 16);
        const playerMaterial = new THREE.MeshStandardMaterial({{ color: 0x00ffff, emissive: 0x004444 }});
        const player = new THREE.Mesh(playerGeometry, playerMaterial);
        scene.add(player);
        
        const collectibles = [];
        const obstacles = [];
        
        function spawnCollectible() {{
            const geometry = new THREE.OctahedronGeometry(0.4);
            const material = new THREE.MeshStandardMaterial({{ color: 0xffdd00, emissive: 0x443300 }});
            const collectible = new THREE.Mesh(geometry, material);
            collectible.position.x = (Math.random() - 0.5) * 30;
            collectible.position.z = (Math.random() - 0.5) * 30;
            collectible.position.y = 0.5;
            scene.add(collectible);
            collectibles.push(collectible);
        }}
        
        for(let i = 0; i < 10; i++) spawnCollectible();
        
        const obstacleGeometry = new THREE.BoxGeometry(1, 1, 1);
        for(let i = 0; i < 15; i++) {{
            const material = new THREE.MeshStandardMaterial({{ color: 0x6666ff }});
            const obstacle = new THREE.Mesh(obstacleGeometry, material);
            obstacle.position.x = (Math.random() - 0.5) * 30;
            obstacle.position.z = (Math.random() - 0.5) * 30;
            scene.add(obstacle);
            obstacles.push({{ mesh: obstacle, radius: 0.7 }});
        }}
        
        let score = 0;
        let level = 1;
        const keys = {{}};
        
        document.addEventListener('keydown', (e) => keys[e.key] = true);
        document.addEventListener('keyup', (e) => keys[e.key] = false);
        
        function updateDisplay() {{
            document.getElementById('score').textContent = score;
            document.getElementById('level').textContent = level;
        }}
        
        function checkCollision(pos1, pos2, radius) {{
            const dx = pos1.x - pos2.x;
            const dz = pos1.z - pos2.z;
            return Math.sqrt(dx*dx + dz*dz) < radius;
        }}
        
        function startGame() {{
            score = 0; level = 1;
            player.position.set(0, 0.5, 0);
            document.getElementById('startScreen').style.display = 'none';
            document.getElementById('gameOverScreen').style.display = 'none';
            updateDisplay();
            for(const c of collectibles) scene.remove(c);
            collectibles.length = 0;
            for(let i = 0; i < 10; i++) spawnCollectible();
        }}
        
        function gameOver() {{
            document.getElementById('finalScore').textContent = score;
            document.getElementById('gameOverScreen').style.display = 'block';
        }}
        
        function restartGame() {{ startGame(); }}
        
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
                if(checkCollision(player.position, obs.mesh.position, obs.radius + 0.5)) {{
                    if(player.position.x < obs.mesh.position.x) player.position.x -= 0.5;
                    else player.position.x += 0.5;
                }}
            }}
            
            for(let i = collectibles.length - 1; i >= 0; i--) {{
                collectibles[i].rotation.y += 0.02;
                collectibles[i].position.y = 0.8 + Math.sin(Date.now() * 0.003 + i) * 0.2;
                
                if(checkCollision(player.position, collectibles[i].position, 0.8)) {{
                    scene.remove(collectibles[i]);
                    collectibles.splice(i, 1);
                    score += 10;
                    updateDisplay();
                    
                    if(collectibles.length === 0) {{
                        level++;
                        for(let j = 0; j < 10 + level * 5; j++) spawnCollectible();
                    }}
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


def generate_sphere_game(title: str, difficulty: str, output: str) -> dict:
    """生成3D弹球收集游戏"""
    title = html.escape(title)
    
    # 路径安全校验：禁止路径遍历
    if ".." in output:
        raise ValueError(f"Path traversal detected: {output}")
    
    html_content = SPHERE_GAME_TEMPLATE.format(
        title=title,
        three_js_url=THREE_JS_URL
    )
    
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return {
        "status": "success",
        "game_type": "3d-sphere",
        "title": title,
        "output_file": output,
        "controls": ["WASD/Arrows: move"],
        "features": ["collection_system", "obstacle_avoidance", "level_progression"]
    }


def main():
    parser = argparse.ArgumentParser(description='Generate 3D Sphere Collection Game')
    parser.add_argument('--title', default='3D Ball Collection', help='Game title')
    parser.add_argument('--difficulty', '-d', default='normal', choices=['easy', 'normal', 'hard'])
    parser.add_argument('--output', '-o', default='sphere3d.html', help='Output file')
    
    args = parser.parse_args()
    
    try:
        result = generate_sphere_game(args.title, args.difficulty, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
        exit(1)


if __name__ == '__main__':
    main()
