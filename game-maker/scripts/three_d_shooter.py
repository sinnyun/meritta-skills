#!/usr/bin/env python3
"""
3D 射击游戏生成器
第一人称射击靶标，支持粒子特效、音效和触摸控制
"""

import argparse
import json
import os
import html

THREE_JS_URL = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r160/three.min.js"

SHOOTER_GAME_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>{title}</title>
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ overflow: hidden; font-family: 'Segoe UI', sans-serif; background: #111; }}
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
            pointer-events: none;
        }}
        #ui div {{ background: rgba(0,0,0,0.7); padding: 10px 20px; border-radius: 10px; }}
        #crosshair {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 30px;
            height: 30px;
            pointer-events: none;
        }}
        #crosshair::before, #crosshair::after {{
            content: '';
            position: absolute;
            background: rgba(255,255,255,0.8);
        }}
        #crosshair::before {{ width: 2px; height: 100%; left: 50%; transform: translateX(-50%); }}
        #crosshair::after {{ width: 100%; height: 2px; top: 50%; transform: translateY(-50%); }}
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
        #startScreen h1, #gameOverScreen h2 {{ color: #ff4444; font-size: 36px; margin-bottom: 20px; }}
        #startScreen p {{ font-size: 16px; margin: 10px 0; color: #aaa; }}
        .btn {{
            background: linear-gradient(135deg, #ff4444, #cc0000);
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
        #ammo {{ color: #ffaa00; }}
        #hitMarker {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #fff;
            font-size: 24px;
            opacity: 0;
            pointer-events: none;
        }}
        #reload {{
            position: absolute;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            color: #ffaa00;
            font-size: 18px;
            display: none;
        }}
    </style>
</head>
<body>
    <div id="ui">
        <div>Score: <span id="score">0</span></div>
        <div>Ammo: <span id="ammo">{max_ammo}</span>/<span id="maxAmmo">{max_ammo}</span></div>
        <div>Time: <span id="time">60</span>s</div>
    </div>
    <div id="crosshair"></div>
    <div id="hitMarker">+10</div>
    <div id="reload">RELOADING...</div>
    
    <div id="startScreen">
        <h1>TARGET SHOOTER 3D</h1>
        <p>First-person shooting range</p>
        <p>Click to shoot | WASD to move | R to reload</p>
        <p>Ammo: {max_ammo} | Time: 60s</p>
        <button class="btn" onclick="startGame()">START</button>
    </div>
    
    <div id="gameOverScreen">
        <h2>TIME'S UP!</h2>
        <p>Final Score: <span id="finalScore">0</span></p>
        <p>Targets Hit: <span id="targetsHit">0</span></p>
        <p>Accuracy: <span id="accuracy">0</span>%</p>
        <p>Best: <span id="bestScore">0</span></p>
        <button class="btn" onclick="restartGame()">PLAY AGAIN</button>
    </div>
    
    <script src="{three_js_url}"></script>
    <script>
        // 音效系统
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        function playSound(type) {{
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            
            if (type === 'shoot') {{
                osc.type = 'square';
                osc.frequency.setValueAtTime(150, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(50, audioCtx.currentTime + 0.1);
                gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
                osc.start(audioCtx.currentTime);
                osc.stop(audioCtx.currentTime + 0.1);
            }} else if (type === 'hit') {{
                osc.type = 'sine';
                osc.frequency.setValueAtTime(800, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(400, audioCtx.currentTime + 0.2);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
                osc.start(audioCtx.currentTime);
                osc.stop(audioCtx.currentTime + 0.2);
            }} else if (type === 'reload') {{
                osc.frequency.setValueAtTime(300, audioCtx.currentTime);
                osc.frequency.linearRampToValueAtTime(600, audioCtx.currentTime + 0.3);
                gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
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
            
            emit(position, color, count = 15) {{
                for (let i = 0; i < count; i++) {{
                    const geometry = new THREE.SphereGeometry(0.08, 6, 6);
                    const material = new THREE.MeshBasicMaterial({{ color: color }});
                    const particle = new THREE.Mesh(geometry, material);
                    particle.position.copy(position);
                    particle.velocity = new THREE.Vector3(
                        (Math.random() - 0.5) * 0.4,
                        (Math.random() - 0.5) * 0.4,
                        (Math.random() - 0.5) * 0.4
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
                    p.life -= delta * 3;
                    if (p.life <= 0) {{
                        this.scene.remove(p);
                        this.particles.splice(i, 1);
                    }}
                }}
            }}
        }}
        
        // 游戏配置
        const MAX_AMMO = {max_ammo};
        const GAME_TIME = 60;
        
        // Three.js 场景
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);
        
        // 射击场环境
        const floorGeometry = new THREE.PlaneGeometry(100, 100);
        const floorMaterial = new THREE.MeshStandardMaterial({{ color: 0x222233, roughness: 0.8 }});
        const floor = new THREE.Mesh(floorGeometry, floorMaterial);
        floor.rotation.x = -Math.PI / 2;
        floor.position.y = 0;
        scene.add(floor);
        
        // 墙壁
        const wallMaterial = new THREE.MeshStandardMaterial({{ color: 0x333344 }});
        const backWall = new THREE.Mesh(new THREE.PlaneGeometry(100, 30), wallMaterial);
        backWall.position.set(0, 15, -50);
        scene.add(backWall);
        
        // 左侧墙
        const leftWall = new THREE.Mesh(new THREE.PlaneGeometry(100, 30), wallMaterial);
        leftWall.position.set(-50, 15, 0);
        leftWall.rotation.y = Math.PI / 2;
        scene.add(leftWall);
        
        // 右侧墙
        const rightWall = new THREE.Mesh(new THREE.PlaneGeometry(100, 30), wallMaterial);
        rightWall.position.set(50, 15, 0);
        rightWall.rotation.y = -Math.PI / 2;
        scene.add(rightWall);
        
        // 灯光
        scene.add(new THREE.AmbientLight(0x404060, 0.5));
        const spotLight = new THREE.SpotLight(0xffffff, 1);
        spotLight.position.set(0, 20, 0);
        spotLight.target.position.set(0, 0, -30);
        scene.add(spotLight);
        scene.add(spotLight.target);
        
        // 相机（第一人称）
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 2, 5);
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        // 靶标
        const targets = [];
        const targetGeometry = new THREE.CylinderGeometry(1.5, 1.5, 0.3, 32);
        
        function createTarget() {{
            const targetMaterial = new THREE.MeshStandardMaterial({{ color: 0xff0000, emissive: 0x330000 }});
            const target = new THREE.Mesh(targetGeometry, targetMaterial);
            
            // 随机位置
            target.position.x = (Math.random() - 0.5) * 60;
            target.position.y = Math.random() * 8 + 2;
            target.position.z = -Math.random() * 30 - 10;
            target.rotation.x = 0;
            
            // 靶心
            const centerGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.35, 16);
            const centerMaterial = new THREE.MeshStandardMaterial({{ color: 0xffff00 }});
            const center = new THREE.Mesh(centerGeometry, centerMaterial);
            center.rotation.x = 0;
            target.add(center);
            
            scene.add(target);
            targets.push({{ mesh: target, active: true, points: 10 }});
        }}
        
        // 移动靶标
        const movingTargets = [];
        function createMovingTarget() {{
            const targetMaterial = new THREE.MeshStandardMaterial({{ color: 0x00ff00, emissive: 0x003300 }});
            const target = new THREE.Mesh(targetGeometry, targetMaterial);
            
            target.position.x = (Math.random() - 0.5) * 40;
            target.position.y = Math.random() * 5 + 3;
            target.position.z = -Math.random() * 20 - 15;
            
            const centerGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.35, 16);
            const centerMaterial = new THREE.MeshStandardMaterial({{ color: 0xffffff }});
            const center = new THREE.Mesh(centerGeometry, centerMaterial);
            target.add(center);
            
            scene.add(target);
            movingTargets.push({{ 
                mesh: target, 
                active: true, 
                points: 25,
                speed: Math.random() * 0.02 + 0.01,
                direction: Math.random() > 0.5 ? 1 : -1
            }});
        }}
        
        // 粒子系统
        const particleSystem = new ParticleSystem(scene);
        
        // 游戏状态
        let score = 0;
        let ammo = MAX_AMMO;
        let timeLeft = GAME_TIME;
        let gameState = 'start';
        let shotsFired = 0;
        let targetsHit = 0;
        let bestScore = parseInt(localStorage.getItem('shooter3d_best') || '0');
        let isReloading = false;
        
        // 移动控制
        const keys = {{}};
        document.addEventListener('keydown', (e) => {{
            keys[e.key.toLowerCase()] = true;
            if (e.key.toLowerCase() === 'r' && !isReloading) {{
                reload();
            }}
        }});
        document.addEventListener('keyup', (e) => keys[e.key.toLowerCase()] = false);
        
        function reload() {{
            if (isReloading || ammo === MAX_AMMO) return;
            isReloading = true;
            document.getElementById('reload').style.display = 'block';
            playSound('reload');
            
            setTimeout(() => {{
                ammo = MAX_AMMO;
                document.getElementById('ammo').textContent = ammo;
                document.getElementById('reload').style.display = 'none';
                isReloading = false;
            }}, 1500);
        }}
        
        function shoot() {{
            if (gameState !== 'playing' || ammo <= 0 || isReloading) return;
            
            playSound('shoot');
            ammo--;
            shotsFired++;
            document.getElementById('ammo').textContent = ammo;
            
            // 自动换弹
            if (ammo === 0) {{
                reload();
            }}
            
            // 射线检测
            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
            
            // 检测固定靶标
            for (const target of targets) {{
                if (!target.active) continue;
                const intersects = raycaster.intersectObject(target.mesh);
                if (intersects.length > 0) {{
                    target.active = false;
                    target.mesh.visible = false;
                    score += target.points;
                    targetsHit++;
                    document.getElementById('score').textContent = score;
                    playSound('hit');
                    particleSystem.emit(intersects[0].point, 0xffff00, 20);
                    showHitMarker('+10');
                    return;
                }}
            }}
            
            // 检测移动靶标
            for (const target of movingTargets) {{
                if (!target.active) continue;
                const intersects = raycaster.intersectObject(target.mesh);
                if (intersects.length > 0) {{
                    target.active = false;
                    target.mesh.visible = false;
                    score += target.points;
                    targetsHit++;
                    document.getElementById('score').textContent = score;
                    playSound('hit');
                    particleSystem.emit(intersects[0].point, 0x00ff00, 25);
                    showHitMarker('+25');
                    return;
                }}
            }}
        }}
        
        function showHitMarker(text) {{
            const marker = document.getElementById('hitMarker');
            marker.textContent = text;
            marker.style.opacity = 1;
            marker.style.transform = 'translate(-50%, -50%) scale(1.5)';
            setTimeout(() => {{
                marker.style.opacity = 0;
                marker.style.transform = 'translate(-50%, -50%) scale(1)';
            }}, 200);
        }}
        
        // 点击射击
        document.addEventListener('click', shoot);
        document.addEventListener('touchstart', (e) => {{ e.preventDefault(); shoot(); }});
        
        // 鼠标视角控制
        let cameraRotationY = 0;
        let cameraRotationX = 0;
        
        document.addEventListener('mousemove', (e) => {{
            if (gameState !== 'playing') return;
            cameraRotationY -= e.movementX * 0.002;
            cameraRotationX -= e.movementY * 0.002;
            cameraRotationX = Math.max(-Math.PI / 3, Math.min(Math.PI / 3, cameraRotationX));
        }});
        
        document.addEventListener('pointerlockchange', () => {{
            if (document.pointerLockElement) {{
                document.body.requestPointerLock();
            }}
        }});
        
        function startGame() {{
            gameState = 'playing';
            score = 0;
            ammo = MAX_AMMO;
            timeLeft = GAME_TIME;
            shotsFired = 0;
            targetsHit = 0;
            document.getElementById('score').textContent = '0';
            document.getElementById('ammo').textContent = ammo;
            document.getElementById('time').textContent = timeLeft;
            document.getElementById('startScreen').style.display = 'none';
            document.getElementById('gameOverScreen').style.display = 'none';
            
            // 清空靶标
            for (const t of targets) {{
                scene.remove(t.mesh);
            }}
            targets.length = 0;
            for (const t of movingTargets) {{
                scene.remove(t.mesh);
            }}
            movingTargets.length = 0;
            
            // 生成初始靶标
            for (let i = 0; i < 8; i++) createTarget();
            for (let i = 0; i < 3; i++) createMovingTarget();
            
            document.body.requestPointerLock();
        }}
        
        function gameOver() {{
            gameState = 'over';
            document.exitPointerLock();
            
            if (score > bestScore) {{
                bestScore = score;
                localStorage.setItem('shooter3d_best', bestScore.toString());
            }}
            
            const accuracy = shotsFired > 0 ? Math.round((targetsHit / shotsFired) * 100) : 0;
            document.getElementById('finalScore').textContent = score;
            document.getElementById('targetsHit').textContent = targetsHit;
            document.getElementById('accuracy').textContent = accuracy;
            document.getElementById('bestScore').textContent = bestScore;
            document.getElementById('gameOverScreen').style.display = 'block';
        }}
        
        function restartGame() {{
            startGame();
        }}
        
        // 游戏循环
        let lastTime = 0;
        let spawnTimer = 0;
        function animate(time) {{
            requestAnimationFrame(animate);
            const delta = (time - lastTime) / 1000;
            lastTime = time;
            
            if (gameState === 'playing') {{
                // 玩家移动
                const moveSpeed = 0.15;
                if (keys['w'] || keys['arrowup']) {{
                    camera.position.z -= moveSpeed;
                    camera.position.z = Math.max(-40, camera.position.z);
                }}
                if (keys['s'] || keys['arrowdown']) {{
                    camera.position.z += moveSpeed;
                    camera.position.z = Math.min(10, camera.position.z);
                }}
                if (keys['a'] || keys['arrowleft']) {{
                    camera.position.x -= moveSpeed;
                    camera.position.x = Math.max(-40, camera.position.x);
                }}
                if (keys['d'] || keys['arrowright']) {{
                    camera.position.x += moveSpeed;
                    camera.position.x = Math.min(40, camera.position.x);
                }}
                
                // 相机旋转
                camera.rotation.set(cameraRotationX, cameraRotationY, 0, 'YXZ');
                
                // 移动靶标
                for (const target of movingTargets) {{
                    if (!target.active) continue;
                    target.mesh.position.y += target.speed * target.direction;
                    target.mesh.rotation.y += 0.02;
                    
                    if (target.mesh.position.y > 10 || target.mesh.position.y < 2) {{
                        target.direction *= -1;
                    }}
                }}
                
                // 生成新靶标
                spawnTimer += delta;
                if (spawnTimer > 3) {{
                    spawnTimer = 0;
                    if (targets.length < 8) createTarget();
                    if (movingTargets.length < 3 && Math.random() > 0.5) createMovingTarget();
                }}
                
                // 计时器
                if (timeLeft > 0) {{
                    setTimeout(() => {{
                        timeLeft--;
                        document.getElementById('time').textContent = timeLeft;
                        if (timeLeft <= 0) gameOver();
                    }}, 1000);
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


def generate_shooter_game(title: str, difficulty: str, output: str) -> dict:
    """
    生成3D射击游戏
    
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
    
    # 根据难度设置弹药数
    ammo_map = {'easy': 30, 'normal': 15, 'hard': 10}
    max_ammo = ammo_map[difficulty]
    
    # 路径安全校验
    # 路径安全校验：禁止路径遍历
    if ".." in output:
        raise ValueError(f"Path traversal detected: {output}")
    
    # 生成HTML
    html_content = SHOOTER_GAME_TEMPLATE.format(
        title=title,
        three_js_url=THREE_JS_URL,
        max_ammo=max_ammo,
        difficulty=difficulty
    )
    
    # 写入文件
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return {
        "status": "success",
        "game_type": "3d-shooter",
        "title": title,
        "difficulty": difficulty,
        "max_ammo": max_ammo,
        "output_file": output,
        "controls": ["WASD/Arrows: move", "Mouse: aim", "Click: shoot", "R: reload"],
        "features": ["first_person_view", "particle_effects", "sound_effects", "moving_targets", "score_leaderboard"]
    }


def main():
    parser = argparse.ArgumentParser(description='Generate 3D Shooter Game')
    parser.add_argument('--title', default='Target Shooter 3D', help='Game title')
    parser.add_argument('--difficulty', '-d', default='normal', 
                       choices=['easy', 'normal', 'hard'],
                       help='Game difficulty (affects ammo count)')
    parser.add_argument('--output', '-o', default='shooter3d.html', help='Output HTML file')
    
    args = parser.parse_args()
    
    try:
        result = generate_shooter_game(args.title, args.difficulty, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
        exit(1)


if __name__ == '__main__':
    main()
