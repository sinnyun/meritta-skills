#!/usr/bin/env python3
"""
3D 平台跳跃游戏生成器
控制角色在3D平台间跳跃，收集金币
"""

import argparse
import json
import os
import html

THREE_JS_URL = "https://cdnjs.cloudflare.com/ajax/libs/three.js/r160/three.min.js"

PLATFORM_GAME_TEMPLATE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>{title}</title>
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ overflow: hidden; font-family: 'Segoe UI', sans-serif; background: #1a1a2e; }}
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
        #startScreen h1, #gameOverScreen h2 {{ color: #00ff88; font-size: 36px; margin-bottom: 20px; }}
        #startScreen p, #gameOverScreen p {{ font-size: 16px; margin: 10px 0; color: #aaa; }}
        .btn {{
            background: linear-gradient(135deg, #00ff88, #00aa55);
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
        #jumpHint {{
            position: absolute;
            bottom: 30px;
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
        <div>Level: <span id="level">1</span></div>
        <div>Lives: <span id="lives">{lives}</span></div>
    </div>
    
    <div id="startScreen">
        <h1>PLATFORM JUMP 3D</h1>
        <p>Jump between platforms and collect coins!</p>
        <p>SPACE to jump | A/D or Left/Right to move</p>
        <button class="btn" onclick="startGame()">START</button>
    </div>
    
    <div id="gameOverScreen">
        <h2>GAME OVER</h2>
        <p>Final Score: <span id="finalScore">0</span></p>
        <p>Best: <span id="bestScore">0</span></p>
        <button class="btn" onclick="restartGame()">TRY AGAIN</button>
    </div>
    
    <div id="jumpHint">SPACE or TAP to jump</div>
    
    <script src="{three_js_url}"></script>
    <script>
        // 音效系统
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        
        function playSound(type) {{
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            
            if (type === 'jump') {{
                osc.type = 'sine';
                osc.frequency.setValueAtTime(300, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(600, audioCtx.currentTime + 0.15);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
                osc.start(audioCtx.currentTime);
                osc.stop(audioCtx.currentTime + 0.15);
            }} else if (type === 'coin') {{
                osc.type = 'sine';
                osc.frequency.setValueAtTime(880, audioCtx.currentTime);
                osc.frequency.setValueAtTime(1100, audioCtx.currentTime + 0.1);
                gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
                osc.start(audioCtx.currentTime);
                osc.stop(audioCtx.currentTime + 0.2);
            }} else if (type === 'land') {{
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(150, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
                osc.start(audioCtx.currentTime);
                osc.stop(audioCtx.currentTime + 0.1);
            }} else if (type === 'die') {{
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(400, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(100, audioCtx.currentTime + 0.5);
                gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);
                osc.start(audioCtx.currentTime);
                osc.stop(audioCtx.currentTime + 0.5);
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
                    const geometry = new THREE.SphereGeometry(0.1, 6, 6);
                    const material = new THREE.MeshBasicMaterial({{ color: color }});
                    const particle = new THREE.Mesh(geometry, material);
                    particle.position.copy(position);
                    particle.velocity = new THREE.Vector3(
                        (Math.random() - 0.5) * 0.3,
                        Math.random() * 0.3,
                        (Math.random() - 0.5) * 0.3
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
                    if (p.life <= 0) {{
                        this.scene.remove(p);
                        this.particles.splice(i, 1);
                    }}
                }}
            }}
        }}
        
        // 游戏配置
        const INITIAL_LIVES = {lives};
        
        // Three.js 场景
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);
        scene.fog = new THREE.Fog(0x1a1a2e, 30, 100);
        
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);
        
        // 灯光
        scene.add(new THREE.AmbientLight(0x606080, 0.5));
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(10, 20, 10);
        scene.add(dirLight);
        
        // 玩家
        const playerGeometry = new THREE.BoxGeometry(0.8, 1.2, 0.8);
        const playerMaterial = new THREE.MeshStandardMaterial({{ 
            color: 0x00ff88, 
            emissive: 0x004422
        }});
        const player = new THREE.Mesh(playerGeometry, playerMaterial);
        player.position.set(0, 2, 0);
        scene.add(player);
        
        // 玩家眼睛
        const eyeGeometry = new THREE.SphereGeometry(0.15, 8, 8);
        const eyeMaterial = new THREE.MeshBasicMaterial({{ color: 0xffffff }});
        const leftEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        leftEye.position.set(-0.2, 0.3, 0.35);
        player.add(leftEye);
        const rightEye = new THREE.Mesh(eyeGeometry, eyeMaterial);
        rightEye.position.set(0.2, 0.3, 0.35);
        player.add(rightEye);
        
        // 平台
        const platforms = [];
        const platformGeometry = new THREE.BoxGeometry(4, 0.5, 4);
        const platformMaterial = new THREE.MeshStandardMaterial({{ 
            color: 0x4488ff, 
            emissive: 0x112244,
            metalness: 0.3,
            roughness: 0.7
        }});
        
        // 金币
        const coins = [];
        const coinGeometry = new THREE.CylinderGeometry(0.3, 0.3, 0.1, 16);
        const coinMaterial = new THREE.MeshStandardMaterial({{ 
            color: 0xffdd00, 
            emissive: 0x443300,
            metalness: 0.9,
            roughness: 0.1
        }});
        
        // 粒子系统
        const particleSystem = new ParticleSystem(scene);
        
        // 游戏状态
        let score = 0;
        let lives = INITIAL_LIVES;
        let level = 1;
        let gameState = 'start';
        let bestScore = parseInt(localStorage.getItem('platform3d_best') || '0');
        
        // 物理状态
        let velocityY = 0;
        let isOnGround = false;
        let currentPlatform = null;
        const gravity = 0.015;
        const jumpForce = 0.35;
        let moveDirection = 0;
        
        // 移动控制
        const keys = {{}};
        document.addEventListener('keydown', (e) => {{
            keys[e.code] = true;
            if (e.code === 'Space' && isOnGround) {{
                jump();
            }}
        }});
        document.addEventListener('keyup', (e) => keys[e.code] = false);
        
        // 触摸控制
        let touchStartX = 0;
        document.addEventListener('touchstart', (e) => {{
            touchStartX = e.touches[0].clientX;
            if (isOnGround) jump();
        }});
        document.addEventListener('touchmove', (e) => {{
            const diff = e.touches[0].clientX - touchStartX;
            if (Math.abs(diff) > 30) {{
                moveDirection = diff > 0 ? 1 : -1;
            }}
        }});
        document.addEventListener('touchend', () => moveDirection = 0);
        
        function jump() {{
            if (!isOnGround) return;
            velocityY = jumpForce;
            isOnGround = false;
            playSound('jump');
        }}
        
        function createPlatform(x, y, z, width = 4) {{
            const geometry = new THREE.BoxGeometry(width, 0.5, 4);
            const material = platformMaterial.clone();
            const platform = new THREE.Mesh(geometry, material);
            platform.position.set(x, y, z);
            scene.add(platform);
            platforms.push({{
                mesh: platform,
                bounds: {{
                    minX: x - width / 2,
                    maxX: x + width / 2,
                    minZ: z - 2,
                    maxZ: z + 2,
                    top: y + 0.25
                }}
            }});
            return platform;
        }}
        
        function createCoin(x, y, z) {{
            const coin = new THREE.Mesh(coinGeometry, coinMaterial.clone());
            coin.position.set(x, y, z);
            scene.add(coin);
            coins.push({{ mesh: coin, collected: false, baseY: y }});
        }}
        
        function generateLevel() {{
            // 清空
            for (const p of platforms) scene.remove(p.mesh);
            platforms.length = 0;
            for (const c of coins) scene.remove(c.mesh);
            coins.length = 0;
            
            // 起始平台
            createPlatform(0, 0, 0, 5);
            
            // 生成平台
            let lastX = 0, lastY = 0, lastZ = 0;
            const platformCount = 10 + level * 3;
            
            for (let i = 0; i < platformCount; i++) {{
                const gap = 3 + Math.random() * 2;
                const heightChange = (Math.random() - 0.3) * 2;
                
                lastX += (Math.random() - 0.5) * 4;
                lastY = Math.max(0, lastY + heightChange);
                lastZ -= gap;
                
                const width = 2 + Math.random() * 3;
                createPlatform(lastX, lastY, lastZ, width);
                
                // 在平台上放置金币
                if (Math.random() > 0.4) {{
                    createCoin(lastX, lastY + 1.5, lastZ);
                }}
            }}
            
            currentPlatform = platforms[0];
        }}
        
        function startGame() {{
            gameState = 'playing';
            score = 0;
            lives = INITIAL_LIVES;
            level = 1;
            player.position.set(0, 2, 0);
            velocityY = 0;
            document.getElementById('score').textContent = '0';
            document.getElementById('level').textContent = '1';
            document.getElementById('lives').textContent = lives;
            document.getElementById('startScreen').style.display = 'none';
            document.getElementById('gameOverScreen').style.display = 'none';
            
            generateLevel();
        }}
        
        function loseLife() {{
            lives--;
            document.getElementById('lives').textContent = lives;
            playSound('die');
            particleSystem.emit(player.position.clone(), 0xff4444, 30);
            
            if (lives <= 0) {{
                gameOver();
            }} else {{
                // 重置位置
                player.position.set(0, 2, 0);
                velocityY = 0;
                camera.position.set(0, 5, 10);
            }}
        }}
        
        function nextLevel() {{
            level++;
            document.getElementById('level').textContent = level;
            generateLevel();
            player.position.set(0, 2, 0);
            velocityY = 0;
            playSound('land');
        }}
        
        function gameOver() {{
            gameState = 'over';
            if (score > bestScore) {{
                bestScore = score;
                localStorage.setItem('platform3d_best', bestScore.toString());
            }}
            document.getElementById('finalScore').textContent = score;
            document.getElementById('bestScore').textContent = bestScore;
            document.getElementById('gameOverScreen').style.display = 'block';
        }}
        
        function restartGame() {{
            startGame();
        }}
        
        // 碰撞检测
        function checkPlatformCollision() {{
            const playerBottom = player.position.y - 0.6;
            const playerBox = {{
                minX: player.position.x - 0.4,
                maxX: player.position.x + 0.4,
                minZ: player.position.z - 0.4,
                maxZ: player.position.z + 0.4
            }};
            
            for (const platform of platforms) {{
                const b = platform.bounds;
                
                // 检测是否在平台上
                if (playerBox.maxX > b.minX && playerBox.minX < b.maxX &&
                    playerBox.maxZ > b.minZ && playerBox.minZ < b.maxZ) {{
                    
                    // 下落时踩到平台
                    if (velocityY <= 0 && playerBottom <= b.top && playerBottom >= b.top - 0.5) {{
                        player.position.y = b.top + 0.6;
                        velocityY = 0;
                        isOnGround = true;
                        currentPlatform = platform;
                        if (Math.random() > 0.8) playSound('land');
                        return;
                    }}
                }}
            }}
            
            isOnGround = false;
            currentPlatform = null;
        }}
        
        function checkCoinCollision() {{
            for (const coin of coins) {{
                if (coin.collected) continue;
                
                const dx = player.position.x - coin.mesh.position.x;
                const dy = player.position.y - coin.mesh.position.y;
                const dz = player.position.z - coin.mesh.position.z;
                const dist = Math.sqrt(dx*dx + dy*dy + dz*dz);
                
                if (dist < 1) {{
                    coin.collected = true;
                    coin.mesh.visible = false;
                    score += 5;
                    document.getElementById('score').textContent = score;
                    playSound('coin');
                    particleSystem.emit(coin.mesh.position.clone(), 0xffdd00, 15);
                }}
            }}
        }}
        
        // 游戏循环
        let lastTime = 0;
        let cameraOffset = new THREE.Vector3(0, 5, 10);
        function animate(time) {{
            requestAnimationFrame(animate);
            const delta = (time - lastTime) / 1000;
            lastTime = time;
            
            if (gameState === 'playing') {{
                // 移动
                if (keys['KeyA'] || keys['ArrowLeft'] || moveDirection < 0) {{
                    player.position.x -= 0.1;
                    player.rotation.y = Math.PI / 2;
                }}
                if (keys['KeyD'] || keys['ArrowRight'] || moveDirection > 0) {{
                    player.position.x += 0.1;
                    player.rotation.y = -Math.PI / 2;
                }}
                
                // 重力
                velocityY -= gravity;
                player.position.y += velocityY;
                
                // 碰撞检测
                checkPlatformCollision();
                checkCoinCollision();
                
                // 掉落检测
                if (player.position.y < -10) {{
                    loseLife();
                }}
                
                // 检查是否到达终点
                if (currentPlatform === platforms[platforms.length - 1] && isOnGround) {{
                    nextLevel();
                }}
                
                // 玩家动画
                player.rotation.x = isOnGround ? 0 : -0.3;
                
                // 金币动画
                for (const coin of coins) {{
                    if (!coin.collected) {{
                        coin.mesh.rotation.y += 0.03;
                        coin.mesh.position.y = coin.baseY + Math.sin(time * 0.003) * 0.2;
                    }}
                }}
                
                // 相机跟随
                camera.position.x = player.position.x * 0.5;
                camera.position.y = player.position.y + 5;
                camera.position.z = player.position.z + 10;
                camera.lookAt(player.position);
                
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


def generate_platform_game(title: str, difficulty: str, output: str) -> dict:
    """
    生成3D平台跳跃游戏
    
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
    
    # 根据难度设置初始生命
    lives_map = {'easy': 5, 'normal': 3, 'hard': 1}
    lives = lives_map[difficulty]
    
    # 路径安全校验
    # 路径安全校验：禁止路径遍历
    if ".." in output:
        raise ValueError(f"Path traversal detected: {output}")
    
    # 生成HTML
    html_content = PLATFORM_GAME_TEMPLATE.format(
        title=title,
        three_js_url=THREE_JS_URL,
        lives=lives,
        difficulty=difficulty
    )
    
    # 写入文件
    with open(output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return {
        "status": "success",
        "game_type": "3d-platform",
        "title": title,
        "difficulty": difficulty,
        "initial_lives": lives,
        "output_file": output,
        "controls": ["A/D or Left/Right: move", "SPACE/Tap: jump"],
        "features": ["level_progression", "coin_collection", "particle_effects", "sound_effects", "touch_support"]
    }


def main():
    parser = argparse.ArgumentParser(description='Generate 3D Platform Jumping Game')
    parser.add_argument('--title', default='Platform Jump 3D', help='Game title')
    parser.add_argument('--difficulty', '-d', default='normal', 
                       choices=['easy', 'normal', 'hard'],
                       help='Game difficulty (affects starting lives)')
    parser.add_argument('--output', '-o', default='platform3d.html', help='Output HTML file')
    
    args = parser.parse_args()
    
    try:
        result = generate_platform_game(args.title, args.difficulty, args.output)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
        exit(1)


if __name__ == '__main__':
    main()
