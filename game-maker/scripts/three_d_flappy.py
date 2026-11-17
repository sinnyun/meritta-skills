#!/usr/bin/env python3
"""
3D Flappy Bird 游戏生成器
控制飞行器穿越3D圆环，支持粒子特效、音效和触摸控制
"""

import argparse
import json
import os
import html

THREE_JS_URL = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r160/three.min.js"

FLAPPY3D_GAME_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>{title}</title>
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ overflow: hidden; font-family: 'Segoe UI', sans-serif; background: #1a0a2e; }}
        #ui {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            color: #fff;
            font-size: 24px;
            text-shadow: 0 0 10px rgba(0,255,255,0.5);
            z-index: 100;
        }}
        #ui span {{ background: rgba(0,0,0,0.5); padding: 10px 20px; border-radius: 10px; }}
        #startScreen, #gameOverScreen {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            color: #fff;
            background: rgba(0,0,0,0.8);
            padding: 40px 60px;
            border-radius: 20px;
            z-index: 200;
        }}
        #startScreen h1, #gameOverScreen h2 {{ color: #00ffff; font-size: 36px; margin-bottom: 20px; text-shadow: 0 0 20px #00ffff; }}
        #startScreen p, #gameOverScreen p {{ font-size: 18px; margin: 10px 0; color: #aaa; }}
        .btn {{
            background: linear-gradient(135deg, #00ffff, #0088ff);
            border: none;
            padding: 15px 40px;
            font-size: 20px;
            color: #fff;
            border-radius: 30px;
            cursor: pointer;
            margin-top: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .btn:hover {{ transform: scale(1.05); box-shadow: 0 0 30px rgba(0,255,255,0.5); }}
        #gameOverScreen {{ display: none; }}
        #difficulty {{ color: #ff6b6b; font-weight: bold; }}
        #touchHint {{ position: absolute; bottom: 50px; left: 50%; transform: translateX(-50%); color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <div id="ui">
        <span>Score: <span id="score">0</span></span>
        <span id="difficulty">NORMAL</span>
    </div>
    
    <div id="startScreen">
        <h1>FLAPPY 3D</h1>
        <p>Control the aircraft through 3D rings</p>
        <p>Tap/Click or Press SPACE to fly up</p>
        <p>Difficulty: <span id="difficulty">{difficulty}</span></p>
        <button class="btn" onclick="startGame()">START</button>
    </div>
    
    <div id="gameOverScreen">
        <h2>GAME OVER</h2>
        <p>Final Score: <span id="finalScore">0</span></p>
        <p>Best Score: <span id="bestScore">0</span></p>
        <button class="btn" onclick="restartGame()">PLAY AGAIN</button>
    </div>
    
    <div id="touchHint">Tap anywhere to fly</div>
    
    <script src="{three_js_url}"></script>
    <script>
        // 音效系统
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        function playSound(type) {{
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            
            if (type === 'flap') {{
                osc.frequency.setValueAtTime(400, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(600, audioCtx.currentTime + 0.1);
                gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
                osc.start(audioCtx.currentTime);
                osc.stop(audioCtx.currentTime + 0.1);
            }} else if (type === 'score') {{
                osc.frequency.setValueAtTime(800, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(1200, audioCtx.currentTime + 0.15);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
                osc.start(audioCtx.currentTime);
                osc.stop(audioCtx.currentTime + 0.15);
            }} else if (type === 'hit') {{
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(200, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(50, audioCtx.currentTime + 0.3);
                gain.gain.setValueAtTime(0.4, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);
                osc.start(audioCtx.currentTime);
                osc.stop(audioCtx.currentTime + 0.3);
            }}
        }}
        
        // 粒子系统
        class ParticleSystem {{
            constructor(scene) {{
                this.scene = scene;
                this.particles = [];
            }}
            
            emit(position, color, count = 20) {{
                for (let i = 0; i < count; i++) {{
                    const geometry = new THREE.SphereGeometry(0.1, 8, 8);
                    const material = new THREE.MeshBasicMaterial({{ color: color }});
                    const particle = new THREE.Mesh(geometry, material);
                    particle.position.copy(position);
                    particle.velocity = new THREE.Vector3(
                        (Math.random() - 0.5) * 0.5,
                        Math.random() * 0.3,
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
                    p.velocity.y -= 0.01;
                    p.life -= delta * 2;
                    p.material.opacity = p.life;
                    p.scale.setScalar(p.life);
                    
                    if (p.life <= 0) {{
                        this.scene.remove(p);
                        this.particles.splice(i, 1);
                    }}
                }}
            }}
        }}
        
        // 游戏配置
        const DIFFICULTY = '{difficulty}';
        const difficultySettings = {{
            easy: {{ ringSpeed: 0.08, ringGap: 8, ringInterval: 2000 }},
            normal: {{ ringSpeed: 0.12, ringGap: 6, ringInterval: 1500 }},
            hard: {{ ringSpeed: 0.18, ringGap: 5, ringInterval: 1200 }}
        }};
        const settings = difficultySettings[DIFFICULTY] || difficultySettings.normal;
        
        // Three.js 场景
        const scene = new THREE.Scene();
        scene.fog = new THREE.Fog(0x1a0a2e, 20, 80);
        
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 0, 10);
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        document.body.appendChild(renderer.domElement);
        
        // 光照
        scene.add(new THREE.AmbientLight(0x404080, 0.5));
        const dirLight = new THREE.DirectionalLight(0xffffff, 1);
        dirLight.position.set(5, 10, 5);
        scene.add(dirLight);
        
        // 背景星星
        const starGeometry = new THREE.BufferGeometry();
        const starCount = 1000;
        const starPositions = new Float32Array(starCount * 3);
        for (let i = 0; i < starCount * 3; i += 3) {{
            starPositions[i] = (Math.random() - 0.5) * 200;
            starPositions[i + 1] = (Math.random() - 0.5) * 200;
            starPositions[i + 2] = (Math.random() - 0.5) * 200;
        }}
        starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
        const starMaterial = new THREE.PointsMaterial({{ color: 0xffffff, size: 0.5 }});
        const stars = new THREE.Points(starGeometry, starMaterial);
        scene.add(stars);
        
        // 飞行器
        const aircraftGeometry = new THREE.ConeGeometry(0.5, 1.5, 8);
        const aircraftMaterial = new THREE.MeshStandardMaterial({{ 
            color: 0x00ffff, 
            emissive: 0x004444,
            metalness: 0.8,
            roughness: 0.2
        }});
        const aircraft = new THREE.Mesh(aircraftGeometry, aircraftMaterial);
        aircraft.rotation.x = Math.PI / 2;
        aircraft.position.set(0, 0, 0);
        scene.add(aircraft);
        
        // 飞行器尾焰
        const flameGeometry = new THREE.ConeGeometry(0.2, 0.8, 8);
        const flameMaterial = new THREE.MeshBasicMaterial({{ color: 0xff6600 }});
        const flame = new THREE.Mesh(flameGeometry, flameMaterial);
        flame.rotation.x = -Math.PI / 2;
        flame.position.z = 0.8;
        aircraft.add(flame);
        
        // 圆环
        const rings = [];
        const ringGroup = new THREE.Group();
        scene.add(ringGroup);
        
        function createRing() {{
            const ringGeometry = new THREE.TorusGeometry(2, 0.2, 16, 32);
            const ringMaterial = new THREE.MeshStandardMaterial({{ 
                color: 0xff00ff, 
                emissive: 0x440044,
                metalness: 0.9,
                roughness: 0.1,
                side: THREE.DoubleSide
            }});
            const ring = new THREE.Mesh(ringGeometry, ringMaterial);
            
            // 随机偏移
            ring.position.y = (Math.random() - 0.5) * settings.ringGap * 2;
            ring.position.x = -30;
            ring.rotation.y = Math.PI / 2;
            
            ringGroup.add(ring);
            rings.push(ring);
            return ring;
        }}
        
        // 粒子系统
        const particleSystem = new ParticleSystem(scene);
        
        // 游戏状态
        let velocity = 0;
        let score = 0;
        let gameState = 'start'; // start, playing, over
        let bestScore = parseInt(localStorage.getItem('flappy3d_best') || '0');
        let lastRingTime = 0;
        const gravity = 0.4;
        const flapStrength = -6;
        
        // 触摸/点击控制
        function flap() {{
            if (gameState === 'playing') {{
                velocity = flapStrength;
                playSound('flap');
                particleSystem.emit(aircraft.position.clone(), 0x00ffff, 10);
            }}
        }}
        
        document.addEventListener('click', flap);
        document.addEventListener('touchstart', (e) => {{ e.preventDefault(); flap(); }});
        document.addEventListener('keydown', (e) => {{
            if (e.code === 'Space') {{
                e.preventDefault();
                flap();
            }}
        }});
        
        function startGame() {{
            gameState = 'playing';
            score = 0;
            velocity = 0;
            aircraft.position.set(0, 0, 0);
            document.getElementById('startScreen').style.display = 'none';
            document.getElementById('gameOverScreen').style.display = 'none';
            document.getElementById('score').textContent = '0';
            
            // 清空圆环
            for (const ring of rings) {{
                ringGroup.remove(ring);
            }}
            rings.length = 0;
            lastRingTime = Date.now();
        }}
        
        function gameOver() {{
            gameState = 'over';
            playSound('hit');
            particleSystem.emit(aircraft.position.clone(), 0xff0000, 50);
            
            if (score > bestScore) {{
                bestScore = score;
                localStorage.setItem('flappy3d_best', bestScore.toString());
            }}
            
            document.getElementById('finalScore').textContent = score;
            document.getElementById('bestScore').textContent = bestScore;
            document.getElementById('gameOverScreen').style.display = 'block';
        }}
        
        function restartGame() {{
            startGame();
        }}
        
        // 游戏循环
        let lastTime = 0;
        function animate(time) {{
            requestAnimationFrame(animate);
            const delta = (time - lastTime) / 1000;
            lastTime = time;
            
            if (gameState === 'playing') {{
                // 物理更新
                velocity += gravity;
                aircraft.position.y += velocity * 0.1;
                
                // 限制角度
                aircraft.rotation.z = velocity * 0.05;
                
                // 边界检测
                if (aircraft.position.y > 15 || aircraft.position.y < -15) {{
                    gameOver();
                }}
                
                // 相机跟随
                camera.position.y = aircraft.position.y * 0.3;
                camera.lookAt(aircraft.position.x, aircraft.position.y, aircraft.position.z);
                
                // 生成圆环
                if (Date.now() - lastRingTime > settings.ringInterval) {{
                    createRing();
                    lastRingTime = Date.now();
                }}
                
                // 更新圆环
                for (let i = rings.length - 1; i >= 0; i--) {{
                    const ring = rings[i];
                    ring.position.x += settings.ringSpeed * 60;
                    ring.rotation.z += 0.02;
                    
                    // 检测碰撞
                    const dx = ring.position.x - aircraft.position.x;
                    const dy = ring.position.y - aircraft.position.y;
                    const distToCenter = Math.sqrt(dx * dx + dy * dy);
                    
                    // 通过圆环
                    if (dx > -0.5 && dx < 0.5 && distToCenter > 1.8 && distToCenter < 2.2) {{
                        if (!ring.passed) {{
                            ring.passed = true;
                            ring.material.color.setHex(0x00ff00);
                            ring.material.emissive.setHex(0x004400);
                            score += 10;
                            document.getElementById('score').textContent = score;
                            playSound('score');
                            particleSystem.emit(aircraft.position.clone(), 0x00ff00, 15);
                        }}
                    }}
                    
                    // 碰撞圆环边缘
                    if (Math.abs(dx) < 1 && distToCenter > 1.7 && distToCenter < 2.3) {{
                        gameOver();
                    }}
                    
                    // 移除出界圆环
                    if (ring.position.x > 20) {{
                        ringGroup.remove(ring);
                        rings.splice(i, 1);
                    }}
                }}
                
                // 更新粒子
                particleSystem.update(delta);
                
                // 背景星星移动
                stars.position.z += 0.1;
                if (stars.position.z > 50) stars.position.z = 0;
            }}
            
            // 飞行器尾焰动画
            flame.scale.y = 1 + Math.sin(time * 0.02) * 0.3;
            
            renderer.render(scene, camera);
        }}
        
        // 窗口大小调整
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
        
        animate(0);
    </script>
</body>
</html>'''


def generate_flappy3d_game(title: str, difficulty: str, output: str) -> dict:
    """
    生成3D Flappy Bird游戏
    
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
    
    # 路径安全校验
    # 路径安全校验：禁止路径遍历
    if ".." in output:
        raise ValueError(f"Path traversal detected: {output}")
    
    # 生成HTML
    html_content = FLAPPY3D_GAME_TEMPLATE.format(
        title=title,
        three_js_url=THREE_JS_URL,
        difficulty=difficulty
    )
    
    # 写入文件
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return {
        "status": "success",
        "game_type": "3d-flappy3d",
        "title": title,
        "difficulty": difficulty,
        "output_file": output,
        "controls": ["SPACE/Click/Tap to flap"],
        "features": ["particle_effects", "sound_effects", "touch_support", "score_leaderboard"]
    }


def main():
    parser = argparse.ArgumentParser(description='Generate 3D Flappy Bird Game')
    parser.add_argument('--title', default='Flappy 3D', help='Game title')
    parser.add_argument('--difficulty', '-d', default='normal', 
                       choices=['easy', 'normal', 'hard'],
                       help='Game difficulty')
    parser.add_argument('--output', '-o', default='flappy3d.html', help='Output HTML file')
    
    args = parser.parse_args()
    
    try:
        result = generate_flappy3d_game(args.title, args.difficulty, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
        exit(1)


if __name__ == '__main__':
    main()
