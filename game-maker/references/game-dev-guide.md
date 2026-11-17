# 游戏开发原理指南

## 目录
1. [游戏循环原理](#游戏循环原理)
2. [碰撞检测](#碰撞检测)
3. [游戏状态管理](#游戏状态管理)
4. [渲染优化](#渲染优化)
5. [常见问题解决方案](#常见问题解决方案)

---

## 游戏循环原理

### 什么是游戏循环
游戏循环是游戏运行的"心脏"，它持续不断地执行以下三个步骤：
1. **输入处理** - 读取玩家操作
2. **逻辑更新** - 更新游戏状态
3. **渲染绘制** - 将画面绘制到屏幕

### 实现方式

#### 方式一：setInterval（传统方式）
```javascript
function gameLoop() {
    processInput();
    updateGame();
    render();
}
setInterval(gameLoop, 1000/60); // 60 FPS
```

#### 方式二：requestAnimationFrame（推荐）
```javascript
function gameLoop(timestamp) {
    const deltaTime = timestamp - lastTime;
    lastTime = timestamp;
    
    processInput();
    updateGame(deltaTime);
    render();
    
    requestAnimationFrame(gameLoop);
}
requestAnimationFrame(gameLoop);
```

### 为什么推荐 requestAnimationFrame
- 自动与显示器刷新率同步（通常60Hz）
- 页面不可见时自动暂停，节省性能
- 提供精确的时间戳，便于计算动画

---

## 碰撞检测

### 矩形碰撞检测（最常用）
```javascript
function rectCollision(rect1, rect2) {
    return rect1.x < rect2.x + rect2.width &&
           rect1.x + rect1.width > rect2.x &&
           rect1.y < rect2.y + rect2.height &&
           rect1.y + rect1.height > rect2.y;
}
```

### 圆形碰撞检测
```javascript
function circleCollision(circle1, circle2) {
    const dx = circle1.x - circle2.x;
    const dy = circle1.y - circle2.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    return distance < circle1.radius + circle2.radius;
}
```

### 像素级碰撞（高级）
适用于不规则形状，需要预先渲染碰撞图。

---

## 游戏状态管理

### 简单状态机
```javascript
const GameState = {
    MENU: 'menu',
    PLAYING: 'playing',
    PAUSED: 'paused',
    GAME_OVER: 'gameOver'
};

let currentState = GameState.MENU;

function update() {
    switch(currentState) {
        case GameState.MENU:
            // 菜单逻辑
            break;
        case GameState.PLAYING:
            // 游戏逻辑
            break;
        case GameState.PAUSED:
            // 暂停逻辑
            break;
        case GameState.GAME_OVER:
            // 游戏结束逻辑
            break;
    }
}
```

### 分数和生命值管理
```javascript
const gameData = {
    score: 0,
    lives: 3,
    level: 1,
    highScore: localStorage.getItem('highScore') || 0
};

function addScore(points) {
    gameData.score += points;
    if (gameData.score > gameData.highScore) {
        gameData.highScore = gameData.score;
        localStorage.setItem('highScore', gameData.highScore);
    }
}

function loseLife() {
    gameData.lives--;
    if (gameData.lives <= 0) {
        currentState = GameState.GAME_OVER;
    }
}
```

---

## 渲染优化

### 双缓冲
防止画面闪烁，使用离屏Canvas：
```javascript
const offscreenCanvas = document.createElement('canvas');
const offCtx = offscreenCanvas.getContext('2d');
const displayCanvas = document.getElementById('game');
const ctx = displayCanvas.getContext('2d');

// 先画到离屏Canvas
offCtx.fillRect(0, 0, 800, 600);
// ... 更多绘制

// 一次性复制到显示Canvas
ctx.drawImage(offscreenCanvas, 0, 0);
```

### 脏矩形渲染
只重绘变化区域：
```javascript
const dirtyRects = [];

function markDirty(x, y, width, height) {
    dirtyRects.push({x, y, width, height});
}

function renderDirty() {
    dirtyRects.forEach(rect => {
        ctx.fillRect(rect.x, rect.y, rect.width, rect.height);
        // 重绘该区域内容
    });
    dirtyRects.length = 0; // 清空
}
```

### 对象池
避免频繁创建和销毁对象：
```javascript
class ObjectPool {
    constructor(createFn, resetFn, initialSize = 10) {
        this.createFn = createFn;
        this.resetFn = resetFn;
        this.pool = [];
        this.active = [];
        
        for (let i = 0; i < initialSize; i++) {
            this.pool.push(createFn());
        }
    }
    
    get() {
        const obj = this.pool.pop() || this.createFn();
        this.active.push(obj);
        return obj;
    }
    
    release(obj) {
        const index = this.active.indexOf(obj);
        if (index > -1) {
            this.active.splice(index, 1);
            this.resetFn(obj);
            this.pool.push(obj);
        }
    }
}
```

---

## 常见问题解决方案

### Q1: 游戏运行很卡怎么办？
**检查清单：**
1. 是否在 gameLoop 中创建新对象？（应该在外部预创建）
2. 是否有大量离屏 Canvas 操作？
3. 是否有不必要的 DOM 操作？
4. requestAnimationFrame 是否正确使用？

**优化建议：**
- 使用对象池复用对象
- 限制同屏对象数量
- 使用 CSS 替代 Canvas 绘制静态元素

### Q2: 碰撞检测不准确？
**常见原因：**
1. 碰撞箱尺寸与视觉尺寸不匹配
2. 位置更新顺序问题
3. 坐标系统不一致

**解决方案：**
```javascript
// 统一使用中心点坐标
const player = { x: 100, y: 100, width: 50, height: 50 };
const getBounds = (obj) => ({
    left: obj.x - obj.width / 2,
    right: obj.x + obj.width / 2,
    top: obj.y - obj.height / 2,
    bottom: obj.y + obj.height / 2
});
```

### Q3: 移动端触控如何实现？
```javascript
let touchStartX, touchStartY;

canvas.addEventListener('touchstart', (e) => {
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
});

canvas.addEventListener('touchend', (e) => {
    const dx = e.changedTouches[0].clientX - touchStartX;
    const dy = e.changedTouches[0].clientY - touchStartY;
    
    // 判断滑动方向
    if (Math.abs(dx) > Math.abs(dy)) {
        if (dx > 30) player.moveRight();
        else if (dx < -30) player.moveLeft();
    } else {
        if (dy > 30) player.moveDown();
        else if (dy < -30) player.moveUp();
    }
});
```

### Q4: 如何保存游戏进度？
```javascript
// 使用 localStorage
function saveGame() {
    const saveData = {
        score: gameData.score,
        level: gameData.level,
        playerPosition: player.getPosition()
    };
    localStorage.setItem('saveGame', JSON.stringify(saveData));
}

function loadGame() {
    const saveData = localStorage.getItem('saveGame');
    if (saveData) {
        const data = JSON.parse(saveData);
        gameData.score = data.score;
        gameData.level = data.level;
        player.setPosition(data.playerPosition);
    }
}
```

### Q5: 3D游戏性能差？
**Three.js 优化技巧：**
1. 使用几何体复用（InstancedMesh）
2. 减少 Draw Calls
3. 使用 LOD（细节层次）
4. 适时使用 2D 替代 3D

```javascript
// LOD 示例
const lod = new THREE.LOD();
lod.addLevel(highDetailMesh, 0);
lod.addLevel(mediumDetailMesh, 50);
lod.addLevel(lowDetailMesh, 100);
scene.add(lod);
```

---

## 游戏闭环设计（重要）

### 什么是游戏闭环

游戏闭环是指从**开始界面** → **游戏过程** → **结束界面** → **重玩** 的完整流程。每一个游戏都必须形成闭环，否则用户体验会断裂。

### 闭环状态机

```
┌─────────┐   click start   ┌───────────┐
│  IDLE   │ ──────────────►│  PLAYING  │
│ (开始)  │                │  (进行中) │
└─────────┘                └───────────┘
     ▲                            │
     │                            │ condition met
     │       click restart        │ (条件达成)
     │                            ▼
     │                      ┌───────────┐
     └──────────────────────│  GAMEOVER │
         (重新开始)          │   (结束)  │
                            └───────────┘
```

### 完整闭环代码模板

```javascript
// ========== 状态定义 ==========
const GameState = {
    IDLE: 0,      // 开始界面
    PLAYING: 1,   // 游戏进行中
    GAMEOVER: 2   // 游戏结束
};
let currentState = GameState.IDLE;

// ========== 游戏数据 ==========
const gameData = {
    score: 0,
    lives: 3,
    level: 1
};

// ========== 初始化 ==========
function init() {
    currentState = GameState.IDLE;
    gameData.score = 0;
    gameData.lives = 3;
    resetGameObjects();
}

// ========== 状态重置（关键！） ==========
function resetGameObjects() {
    player.reset();
    obstacles.length = 0;
    collectibles.length = 0;
}

// ========== 主循环 ==========
function gameLoop() {
    switch(currentState) {
        case GameState.IDLE:
            renderStartScreen();
            break;
        case GameState.PLAYING:
            update();
            render();
            break;
        case GameState.GAMEOVER:
            renderGameOver();
            break;
    }
    requestAnimationFrame(gameLoop);
}

// ========== 游戏逻辑 ==========
function update() {
    processInput();
    updatePhysics();
    checkCollisions();  // ← 碰撞检测必须有效实现！
    checkWinCondition();
    checkLoseCondition();
}

function checkCollisions() {
    obstacles.forEach((obs, index) => {
        if (player.collidesWith(obs)) {
            handleCollision(obs, index);
        }
    });
    
    // ⚠️ 注意：删除元素时使用安全的遍历方式
    // 错误方式：obstacles.forEach + splice（会跳过元素）
    // 正确方式：反向遍历
    for (let i = obstacles.length - 1; i >= 0; i--) {
        if (obstacles[i].shouldRemove) {
            obstacles.splice(i, 1);
        }
    }
}

function checkLoseCondition() {
    if (gameData.lives <= 0) {
        currentState = GameState.GAMEOVER;
    }
}

// ========== 渲染函数 ==========
function renderStartScreen() {
    ctx.fillStyle = '#1a1a2e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#fff';
    ctx.font = '48px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('游戏标题', canvas.width/2, canvas.height/2 - 50);
    
    ctx.font = '24px Arial';
    ctx.fillText('点击开始游戏', canvas.width/2, canvas.height/2 + 20);
}

function renderGameOver() {
    ctx.fillStyle = 'rgba(0,0,0,0.8)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    ctx.fillStyle = '#ff4444';
    ctx.font = '48px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('游戏结束', canvas.width/2, canvas.height/2 - 40);
    
    ctx.fillStyle = '#fff';
    ctx.font = '32px Arial';
    ctx.fillText(`得分: ${gameData.score}`, canvas.width/2, canvas.height/2 + 20);
    
    ctx.font = '24px Arial';
    ctx.fillText('点击重新开始', canvas.width/2, canvas.height/2 + 70);
}

// ========== 输入处理 ==========
canvas.addEventListener('click', (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    switch(currentState) {
        case GameState.IDLE:
            currentState = GameState.PLAYING;
            break;
        case GameState.GAMEOVER:
            init();  // 重置所有状态
            currentState = GameState.PLAYING;
            break;
    }
});

// ========== 开始游戏 ==========
init();
requestAnimationFrame(gameLoop);
```

### 闭环验证清单

生成游戏后，**必须**验证以下要素：

| 检查项 | 说明 | 验证方法 |
|-------|------|---------|
| ✅ 有开始界面 | 显示游戏标题和开始提示 | 代码中有 IDLE 状态渲染 |
| ✅ 状态转换正确 | IDLE → PLAYING → GAMEOVER → IDLE | 点击事件正确切换状态 |
| ✅ 碰撞检测有效 | 声明的碰撞必须实际生效 | 游戏对象能检测到碰撞 |
| ✅ 结束条件明确 | 失败/胜利有清晰判定 | 有 GAMEOVER 状态触发 |
| ✅ 重玩机制可用 | 可以从结束回到开始 | init() 函数重置所有状态 |
| ✅ 视觉效果对应 | 碰撞/得分有视觉反馈 | 粒子/音效/动画 |

### 常见闭环问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 点击开始没反应 | 事件绑定在错误状态 | 确保 IDLE 状态响应点击 |
| 碰撞后不结束 | 碰撞检测未实现 | 添加有效的碰撞检测函数 |
| 重玩后数据残留 | resetGameObjects 不完整 | init() 必须重置所有数据 |
| forEach+splice 跳过元素 | 遍历中删除元素问题 | 改用反向 for 循环 |

---

## 推荐学习资源

| 资源 | 说明 |
|------|------|
| MDN Canvas Tutorial | https://developer.mozilla.org/zh-CN/docs/Web/API/Canvas_API |
| Three.js 官方文档 | https://threejs.org/docs/ |
| Game Development Patterns | 游戏开发设计模式经典参考 |

---

## 总结

游戏开发的核心概念：
1. **游戏循环** - 驱动游戏运行的核心
2. **碰撞检测** - 判断交互的基础
3. **状态管理** - 控制游戏流程
4. **渲染优化** - 保证流畅体验
5. **游戏闭环** - 完整的用户体验旅程

掌握这些原理，就能开发出各种类型的网页游戏！
