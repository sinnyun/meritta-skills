#!/usr/bin/env python3
"""
3D 赛车躲避游戏生成器
控制赛车躲避迎面而来的障碍物
"""

import argparse
import json
import os
import html

THREE_JS_URL = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r160/three.min.js"

RACING_GAME_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>{title}</title>
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ overflow: hidden; font-family: 'Segoe UI', sans-serif; background: #0a0a1a; }}
        #ui {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            color: #fff;
            font-size: 20px;
            z-index: 100;
        }}
        #ui div {{ background: rgba(0,0,0,0.7); padding: 10px 20px; border-radius: 10px; }}
        #speedometer {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            color: #00ff88;
            font-size: 32px;
            font-weight: bold;
            background: rgba(0,0,0,0.8);
            padding: 15px 25px;
            border-radius: 15px;
            border: 2px solid #00ff88;
        }}
        #speedometer span {{ font-size: 14px; color: #888; }}
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
            z-index: 200;
        }}
        #startScreen h1, #gameOverScreen h2 {{ color: #ff8800; font-size: 36px; margin-bottom: 20px; }}
        #startScreen p, #gameOverScreen p {{ font-size: 16px; margin: 10px 0; color: #aaa; }}
        .btn {{
            background: linear-gradient(135deg, #ff8800, #ff5500);
            border: none;
            padding: 15px 40px;
            font-size: 20px;
            color: #fff;
            border-radius: 30px;
            cursor: pointer;
            margin-top: 20px;
        }}
        .btn:hover {{ transform: scale(1.05); }}
        #gameOverScreen {{ display: none; }}
        #touchHint {{
            position: absolute;
            bottom: 80px;
            left: 50%;
            transform: translateX(-50%);
            color: rgba(255,255,255,0.5);
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div id="ui">
        <div>Score: <span id="score">0</span></div>
        <div>Distance: <span id="distance">0</span>m</div>
    </div>
    <div id="speedometer"><span>SPEED</span><br><span id="speed">0</span> km/h</div>
    
    <div id="startScreen">
        <h1>RACING RUSH 3D</h1>
        <p>Dodge obstacles and survive!</p>
        <p>A/D or Left/Right to steer</p>
        <p>Touch left/right side on mobile</p>
        <button class="btn" onclick="startGame()">START</button>
    </div>
    
    <div id="gameOverScreen">
        <h2>GAME OVER</h2>
        <p>Final Score: <span id="finalScore">0</span></p>
        <p>Distance: <span id="finalDistance">0</span>m</p>
        <p>Best: <span id="bestScore">0</span></p>
        <button class="btn" onclick="restartGame()">TRY AGAIN</button>
    </div>
    
    <div id="touchHint">Tap left/right side to steer</div>
    
    <script src="{three_js_url}"></script>
    <script>
        // 音效系统
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        function playSound(type) {{
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            
            if (type === 'engine') {{
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(80 + currentSpeed * 2, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
            }} else if (type === 'crash') {{
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(200, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(30, audioCtx.currentTime + 0.5);
                gain.gain.setValueAtTime(0.4, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);
                osc.start(audioCtx.currentTime);
                osc.stop(audioCtx.currentTime + 0.5);
            }} else if (type === 'nearMiss') {{
                osc.type = 'sine';
                osc.frequency.setValueAtTime(600, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(800, audioCtx.currentTime + 0.1);
                gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
                osc.start(audioCtx.currentTime);
                osc.stop(audioCtx.currentTime + 0.1);
            }}
        }}
        
        // 粒子系统
        class ParticleSystem {{
            constructor(scene) {{
                this.scene = scene;
                this.particles = [];
            }}
            
            emit(position, color, count = 30) {{
                for (let i = 0; i < count; i++) {{
                    const geometry = new THREE.SphereGeometry(0.1, 6, 6);
                    const material = new THREE.MeshBasicMaterial({{ color: color }});
                    const particle = new THREE.Mesh(geometry, material);
                    particle.position.copy(position);
                    particle.velocity = new THREE.Vector3(
                        (Math.random() - 0.5) * 0.5,
                        Math.random() * 0.5,
                        (Math.random() - 0.5) * 0.5
                    );
                    particle.life = 1.0;
                    this.scene.add(particle);
                    this.particles.push(particle);
                }}
            }}
            
            update(delta) {{
                for (let i = this.particles.length - 1; i >= 0; i--) {{
                    const p = this.particles[i];
                    p.position.add(p.velocity);
                    p.life -= delta * 2;
                    if (p.life <= 0) {{
                        this.scene.remove(p);
                        this.particles.splice(i, 1);
                    }}
                }}
            }}
        }}
        
        // 游戏配置
        const INITIAL_SPEED = {initial_speed};
        const ROAD_WIDTH = 12;
        const LANE_COUNT = 3;
        const LANE_WIDTH = ROAD_WIDTH / LANE_COUNT;
        
        // Three.js 场景
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0a1a);
        scene.fog = new THREE.Fog(0x0a0a1a, 30, 150);
        
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 5, 10);
        camera.lookAt(0, 0, -20);
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        // 灯光
        scene.add(new THREE.AmbientLight(0x404060, 0.5));
        const spotLight = new THREE.SpotLight(0xffffff, 1);
        spotLight.position.set(0, 30, 0);
        scene.add(spotLight);
        
        // 道路
        const roadGeometry = new THREE.PlaneGeometry(ROAD_WIDTH, 500);
        const roadMaterial = new THREE.MeshStandardMaterial({{ color: 0x222233, roughness: 0.9 }});
        const road = new THREE.Mesh(roadGeometry, roadMaterial);
        road.rotation.x = -Math.PI / 2;
        road.position.z = -200;
        scene.add(road);
        
        // 车道线
        function createLaneLines() {{
            const lineMaterial = new THREE.MeshBasicMaterial({{ color: 0xffff00 }});
            for (let i = -1; i <= 1; i += 2) {{
                for (let z = 0; z > -500; z -= 10) {{
                    const lineGeometry = new THREE.BoxGeometry(0.2, 0.1, 4);
                    const line = new THREE.Mesh(lineGeometry, lineMaterial);
                    line.position.set(i * LANE_WIDTH / 2, 0.05, z);
                    scene.add(line);
                }}
            }}
        }}
        createLaneLines();
        
        // 路边装饰
        function createRoadSide() {{
            const sideMaterial = new THREE.MeshStandardMaterial({{ color: 0x4444ff }});
            for (let z = 0; z > -500; z -= 20) {{
                const leftPole = new THREE.Mesh(new THREE.BoxGeometry(0.3, 2, 0.3), sideMaterial);
                leftPole.position.set(-ROAD_WIDTH / 2 - 1, 1, z);
                scene.add(leftPole);
                
                const rightPole = new THREE.Mesh(new THREE.BoxGeometry(0.3, 2, 0.3), sideMaterial);
                rightPole.position.set(ROAD_WIDTH / 2 + 1, 1, z);
                scene.add(rightPole);
            }}
        }}
        createRoadSide();
        
        // 赛车
        const carGroup = new THREE.Group();
        
        // 车身
        const bodyGeometry = new THREE.BoxGeometry(1.5, 0.6, 3);
        const bodyMaterial = new THREE.MeshStandardMaterial({{ 
            color: 0xff4444, 
            emissive: 0x220000,
            metalness: 0.8,
            roughness: 0.2
        }});
        const carBody = new THREE.Mesh(bodyGeometry, bodyMaterial);
        carBody.position.y = 0.5;
        carGroup.add(carBody);
        
        // 车顶
        const roofGeometry = new THREE.BoxGeometry(1.2, 0.5, 1.5);
        const roof = new THREE.Mesh(roofGeometry, bodyMaterial);
        roof.position.set(0, 1, -0.2);
        carGroup.add(roof);
        
        // 车轮
        const wheelGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.2, 16);
        const wheelMaterial = new THREE.MeshStandardMaterial({{ color: 0x111111 }});
        const wheelPositions = [[-0.8, 0.3, 1], [0.8, 0.3, 1], [-0.8, 0.3, -1], [0.8, 0.3, -1]];
        wheelPositions.forEach(pos => {{
            const wheel = new THREE.Mesh(wheelGeometry, wheelMaterial);
            wheel.rotation.z = Math.PI / 2;
            wheel.position.set(...pos);
            carGroup.add(wheel);
        }});
        
        carGroup.position.set(0, 0, 5);
        scene.add(carGroup);
        
        // 障碍物
        const obstacles = [];
        const obstacleColors = [0x00ff88, 0xff8800, 0x8800ff, 0x00ffff];
        
        function createObstacle() {{
            const lane = Math.floor(Math.random() * LANE_COUNT) - 1;
            const color = obstacleColors[Math.floor(Math.random() * obstacleColors.length)];
            
            const obstacleGeometry = new THREE.BoxGeometry(
                1.5 + Math.random(),
                1 + Math.random() * 2,
                1.5 + Math.random()
            );
            const obstacleMaterial = new THREE.MeshStandardMaterial({{ 
                color: color, 
                emissive: Math.max(0, color - 0x444444),
                metalness: 0.5,
                roughness: 0.5
            }});
            const obstacle = new THREE.Mesh(obstacleGeometry, obstacleMaterial);
            obstacle.position.set(lane * LANE_WIDTH, obstacle.geometry.parameters.height / 2, -100);
            scene.add(obstacle);
            
            obstacles.push({{ mesh: obstacle, lane: lane }});
        }}
        
        // 粒子系统
        const particleSystem = new ParticleSystem(scene);
        
        // 游戏状态
        let score = 0;
        let distance = 0;
        let gameState = 'start';
        let currentSpeed = INITIAL_SPEED;
        let bestScore = parseInt(localStorage.getItem('racing3d_best') || '0');
        let steerDirection = 0;
        
        // 控制
        document.addEventListener('keydown', (e) => {{
            if (e.key === 'a' || e.key === 'A' || e.key === 'ArrowLeft') steerDirection = -1;
            if (e.key === 'd' || e.key === 'D' || e.key === 'ArrowRight') steerDirection = 1;
        }});
        document.addEventListener('keyup', (e) => {{
            if ((e.key === 'a' || e.key === 'A' || e.key === 'ArrowLeft') && steerDirection === -1) steerDirection = 0;
            if ((e.key === 'd' || e.key === 'D' || e.key === 'ArrowRight') && steerDirection === 1) steerDirection = 0;
        }});
        
        // 触摸控制
        document.addEventListener('touchstart', (e) => {{
            const x = e.touches[0].clientX;
            if (x < window.innerWidth / 2) steerDirection = -1;
            else steerDirection = 1;
        }});
        document.addEventListener('touchend', () => steerDirection = 0);
        
        function startGame() {{
            gameState = 'playing';
            score = 0;
            distance = 0;
            currentSpeed = INITIAL_SPEED;
            carGroup.position.set(0, 0, 5);
            
            document.getElementById('score').textContent = '0';
            document.getElementById('distance').textContent = '0';
            document.getElementById('speed').textContent = Math.round(currentSpeed * 10);
            document.getElementById('startScreen').style.display = 'none';
            document.getElementById('gameOverScreen').style.display = 'none';
            
            // 清空障碍物
            for (const obs of obstacles) scene.remove(obs.mesh);
            obstacles.length = 0;
        }}
        
        function gameOver() {{
            gameState = 'over';
            playSound('crash');
            particleSystem.emit(carGroup.position.clone(), 0xff0000, 50);
            
            if (score > bestScore) {{
                bestScore = score;
                localStorage.setItem('racing3d_best', bestScore.toString());
            }}
            
            document.getElementById('finalScore').textContent = score;
            document.getElementById('finalDistance').textContent = Math.round(distance);
            document.getElementById('bestScore').textContent = bestScore;
            document.getElementById('gameOverScreen').style.display = 'block';
        }}
        
        function restartGame() {{
            startGame();
        }}
        
        // 碰撞检测
        function checkCollision() {{
            const carBounds = {{
                minX: carGroup.position.x - 0.7,
                maxX: carGroup.position.x + 0.7,
                minZ: carGroup.position.z - 1.5,
                maxZ: carGroup.position.z + 1.5
            }};
            
            for (const obs of obstacles) {{
                const obsPos = obs.mesh.position;
                const obsSize = obs.mesh.geometry.parameters;
                
                const obsBounds = {{
                    minX: obsPos.x - obsSize.width / 2,
                    maxX: obsPos.x + obsSize.width / 2,
                    minZ: obsPos.z - obsSize.depth / 2,
                    maxZ: obsPos.z + obsSize.depth / 2
                }};
                
                if (carBounds.maxX > obsBounds.minX && carBounds.minX < obsBounds.maxX &&
                    carBounds.maxZ > obsBounds.minZ && carBounds.minZ < obsBounds.maxZ) {{
                    return true;
                }}
                
                // 近距离错过检测
                const nearDist = Math.abs(carBounds.minZ - obsBounds.maxZ);
                if (nearDist < 1 && Math.abs(carBounds.maxX - obsBounds.minX) < 0.5) {{
                    playSound('nearMiss');
                }}
            }}
            return false;
        }}
        
        // 游戏循环
        let lastTime = 0;
        let spawnTimer = 0;
        function animate(time) {{
            requestAnimationFrame(animate);
            const delta = (time - lastTime) / 1000;
            lastTime = time;
            
            if (gameState === 'playing') {{
                // 加速
                currentSpeed += 0.01;
                currentSpeed = Math.min(currentSpeed, INITIAL_SPEED * 2);
                
                // 移动
                const moveSpeed = steerDirection * 0.15;
                carGroup.position.x += moveSpeed;
                carGroup.position.x = Math.max(-ROAD_WIDTH / 2 + 1, Math.min(ROAD_WIDTH / 2 - 1, carGroup.position.x));
                
                // 倾斜
                carGroup.rotation.z = -steerDirection * 0.1;
                
                // 更新障碍物
                for (let i = obstacles.length - 1; i >= 0; i--) {{
                    const obs = obstacles[i];
                    obs.mesh.position.z += currentSpeed;
                    obs.mesh.rotation.y += 0.01;
                    
                    if (obs.mesh.position.z > 20) {{
                        scene.remove(obs.mesh);
                        obstacles.splice(i, 1);
                        score += 10;
                        document.getElementById('score').textContent = score;
                    }}
                }}
                
                // 距离
                distance += currentSpeed * 0.1;
                document.getElementById('distance').textContent = Math.round(distance);
                document.getElementById('speed').textContent = Math.round(currentSpeed * 10);
                
                // 生成障碍物
                spawnTimer += currentSpeed;
                const spawnThreshold = {spawn_threshold};
                if (spawnTimer > spawnThreshold) {{
                    spawnTimer = 0;
                    createObstacle();
                }}
                
                // 碰撞检测
                if (checkCollision()) {{
                    gameOver();
                }}
                
                // 更新粒子
                particleSystem.update(delta);
            }}
            
            renderer.render(scene, camera);
        }}
        
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
        
        animate(0);
    </script>
</body>
</html>'''


def generate_racing_game(title: str, difficulty: str, output: str) -> dict:
    """
    生成3D赛车躲避游戏
    
    Args:
        title: 游戏标题
        difficulty: 难度 easy/normal/hard
        output: 输出文件路径
    
    Returns:
        包含生成结果的字典
    """
    # 输入校验
    title = html.escape(title)
    difficulty = difficulty.lower()
    if difficulty not in ['easy', 'normal', 'hard']:
        difficulty = 'normal'
    
    # 根据难度设置速度
    speed_map = {'easy': 0.3, 'normal': 0.5, 'hard': 0.7}
    initial_speed = speed_map[difficulty]
    
    # 根据难度设置障碍物生成间隔
    spawn_map = {'easy': 80, 'normal': 50, 'hard': 30}
    spawn_threshold = spawn_map[difficulty]
    
    # 路径安全校验
    # 路径安全校验：禁止路径遍历
    if ".." in output:
        raise ValueError(f"Path traversal detected: {output}")
    
    # 生成HTML
    html_content = RACING_GAME_TEMPLATE.format(
        title=title,
        three_js_url=THREE_JS_URL,
        initial_speed=initial_speed,
        spawn_threshold=spawn_threshold,
        difficulty=difficulty
    )
    
    # 写入文件
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return {
        "status": "success",
        "game_type": "3d-racing",
        "title": title,
        "difficulty": difficulty,
        "initial_speed": initial_speed,
        "output_file": output,
        "controls": ["A/D or Left/Right: steer", "Touch: tap left/right side"],
        "features": ["progressive_speed", "particle_effects", "sound_effects", "touch_support", "near_miss_bonus"]
    }


def main():
    parser = argparse.ArgumentParser(description='Generate 3D Racing Dodge Game')
    parser.add_argument('--title', default='Racing Rush 3D', help='Game title')
    parser.add_argument('--difficulty', '-d', default='normal', 
                       choices=['easy', 'normal', 'hard'],
                       help='Game difficulty (affects speed and obstacle frequency)')
    parser.add_argument('--output', '-o', default='racing3d.html', help='Output HTML file')
    
    args = parser.parse_args()
    
    try:
        result = generate_racing_game(args.title, args.difficulty, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
        exit(1)


if __name__ == '__main__':
    main()
