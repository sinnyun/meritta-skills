# web-game-dev 技术架构文档

## 1. 概述

### 1.1 项目定位

web-game-dev 是一个面向 AI Agent 的网页游戏开发技能包，通过 Python 脚本生成可在浏览器直接运行的 HTML5 小游戏。目标用户是希望快速创建 2D/3D 小游戏的开发者，核心价值是**零部署成本**和**开箱即用**。

### 1.2 核心指标

| 指标 | 数值 |
|------|------|
| 脚本数量 | 5个 Python 脚本 |
| 代码总量 | ~2753 行 |
| 支持游戏类型 | 6种（贪吃蛇、打砖块、俄罗斯方块、3D弹球、3D方块、3D迷宫） |
| 输出格式 | 单个 HTML 文件 |
| 运行时依赖 | 2D: 无 / 3D: Three.js CDN |

### 1.3 技术栈

```
生成层 (Python)
├── argparse      - CLI 参数解析
├── html.escape   - XSS 防护
└── json          - 结构化输出

运行时层 (HTML/JavaScript)
├── HTML5 Canvas  - 2D 游戏渲染
├── Three.js r128 - 3D 游戏渲染
├── localStorage  - 数据持久化
└── requestAnimationFrame - 游戏循环
```

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        AI Agent                              │
│  (用户交互层 - 自然语言理解、需求分析、代码生成)              │
└─────────────────────┬───────────────────────────────────────┘
                      │ 请求
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                      SKILL.md                               │
│  (入口文档 - 定义工作流程、示例、工具说明)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ 加载
                      ▼
┌─────────────────────────────────────────────────────────────┐
│               scripts/game_generator.py                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  门面层 (Facade) - 统一入口，分发请求                │   │
│  │  - 参数验证    - 游戏类型路由    - 统一错误处理      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
          ┌───────────┼───────────┬───────────┬───────────┐
          │           │           │           │           │
          ▼           ▼           ▼           ▼           ▼
    ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
    │  snake   │ │ breakout │ │ tetris   │ │ three_d  │ │ (扩展)   │
    │ _game.py │ │ _game.py │ │ _game.py │ │ _scene.py│ │          │
    └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘
         │             │             │             │            │
         └─────────────┴──────┬──────┴─────────────┘            │
                              ▼
                    ┌──────────────────┐
                    │   HTML 模板层     │
                    │  (游戏核心逻辑)   │
                    └────────┬─────────┘
                             │ 输出
                             ▼
                    ┌──────────────────┐
                    │   单个 HTML 文件  │
                    │  (浏览器直接运行) │
                    └──────────────────┘
```

### 2.2 模块职责

| 模块 | 职责 | 依赖关系 |
|------|------|----------|
| SKILL.md | AI Agent 交互协议、用户引导、示例 | 无 |
| game_generator.py | 统一入口、路由分发、参数校验 | 调用其他模块 |
| snake_game.py | 贪吃蛇游戏生成 | 无 |
| breakout_game.py | 打砖块游戏生成 | 无 |
| tetris_game.py | 俄罗斯方块游戏生成 | 无 |
| three_d_scene.py | 3D场景游戏生成 | Three.js CDN |
| game-dev-guide.md | 游戏开发原理知识 | 无 |
| game-templates.md | 模板参考代码 | 无 |

---

## 3. 核心模块设计

### 3.1 游戏生成器 (game_generator.py)

```python
# 架构: 门面模式 (Facade Pattern)
class GameGenerator:
    def __init__(self):
        self.generators = {
            'snake': self.generate_snake,
            'breakout': self.generate_breakout,
            'tetris': self.generate_tetris,
            '3d-sphere': self.generate_3d_sphere,
            '3d-cube': self.generate_3d_cube,
            '3d-maze': self.generate_3d_maze,
        }
    
    def route(self, game_type: str):
        """根据游戏类型分发到对应生成器"""
        if game_type not in self.generators:
            raise ValueError(f"不支持的游戏类型: {game_type}")
        return self.generators[game_type]()
```

**设计理由**:
- 门面模式提供统一入口，降低调用方复杂度
- 路由字典支持 O(1) 复杂度游戏类型查找
- 集中参数校验，避免重复代码

### 3.2 独立游戏脚本

每个独立脚本采用**模板方法模式**:

```python
# 命令模式 + 模板方法
def main():
    args = parse_arguments()      # 1. 解析参数
    validate_args(args)            # 2. 校验参数
    template = load_template()     # 3. 加载模板
    html = interpolate(template)   # 4. 填充内容
    write_output(html, args.output) # 5. 输出文件
    print_json_result(args)       # 6. 输出JSON

if __name__ == "__main__":
    main()
```

### 3.3 HTML 游戏模板结构

```html
<!DOCTYPE html>
<html>
<head>
    <!-- 1. 元数据 (title, charset, viewport) -->
    <style>/* 2. 样式 */</style>
</head>
<body>
    <canvas id="gameCanvas"></canvas>
    <script>
        // 3. 游戏状态初始化
        const state = { /* ... */ };
        
        // 4. 输入处理 (键盘/触摸)
        document.addEventListener('keydown', handleInput);
        
        // 5. 游戏循环
        function gameLoop() {
            update();  // 更新状态
            render();  // 渲染画面
            requestAnimationFrame(gameLoop);
        }
        
        // 6. 启动游戏
        gameLoop();
    </script>
</body>
</html>
```

---

## 4. 数据流

### 4.1 请求处理流程

```
用户请求
    │
    ▼
┌─────────────────┐
│ 1. 解析参数     │ ← CLI: python script.py --arg value
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. 输入校验     │ ← XSS转义、路径验证、范围检查
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. 生成游戏     │ ← 模板插值、参数替换
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. 文件写入     │ ← try-catch保护、原子写入
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. JSON响应     │ ← {"status": "success", "output_file": "..."}
└─────────────────┘
```

### 4.2 状态管理 (2D游戏)

```javascript
// 贪吃蛇游戏状态
const gameState = {
    snake: [{ x: 10, y: 10 }],  // 蛇身坐标数组
    food: { x: 15, y: 15 },     // 食物位置
    direction: { dx: 1, dy: 0 }, // 移动方向
    score: 0,
    gameOver: false,
    speed: 100  // 移动间隔(ms)
};
```

### 4.3 状态管理 (3D游戏)

```javascript
// Three.js 3D场景状态
const sceneState = {
    player: { x: 0, y: 1.6, z: 5 },  // 玩家位置(相机)
    obstacles: [],                       // 障碍物列表
    collectibles: [],                   // 可收集物品
    score: 0,
    isGameOver: false
};
```

---

## 5. 安全性设计

### 5.1 安全威胁模型

| 威胁 | 攻击向量 | 防护措施 |
|------|----------|----------|
| XSS注入 | title 参数嵌入恶意脚本 | `html.escape()` 转义 |
| 路径遍历 | output 参数 `../../etc` | 禁止 `..` + 敏感目录白名单 |
| 文件覆盖 | 写入系统关键文件 | 工作目录限制 |
| 内容注入 | 恶意HTML/JS内容 | 输出全量生成，无用户内容拼接 |

### 5.2 XSS 防护实现

```python
import html

def sanitize_title(title: str) -> str:
    """
    转义HTML特殊字符，防止XSS注入
    
    输入:  <script>alert(1)</script>
    输出:  &lt;script&gt;alert(1)&lt;/script&gt;
    """
    return html.escape(title, quote=True)
```

### 5.3 路径安全实现

```python
import os

def validate_output_path(output: str) -> str:
    """
    验证输出路径安全:
    1. 禁止路径遍历 (..)
    2. 禁止写入敏感目录
    3. 限制在当前工作目录内
    """
    # 解析为绝对路径
    abs_path = os.path.abspath(output)
    
    # 禁止路径遍历
    if '..' in output:
        raise ValueError("Path traversal detected")
    
    # 禁止敏感目录
    forbidden = ['/etc', '/var', '/usr', '/bin', '/sbin', '/sys', '/proc']
    for forbidden_dir in forbidden:
        if abs_path.startswith(forbidden_dir):
            raise ValueError(f"Cannot write to system directory: {forbidden_dir}")
    
    # 限制在当前工作目录
    cwd = os.getcwd()
    if not abs_path.startswith(cwd):
        raise ValueError("Path must be within current directory")
    
    return abs_path
```

### 5.4 CSP 内容安全策略

```html
<head>
    <meta http-equiv="Content-Security-Policy" 
          content="default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com;">
</head>
```

---

## 6. 扩展机制

### 6.1 添加新游戏类型

**步骤 1**: 在 `game_generator.py` 添加生成函数

```python
def generate_flappy_bird(self, args):
    """生成 Flappy Bird 游戏"""
    return generate_game('flappy_bird', FLAPPY_BIRD_TEMPLATE, args)
```

**步骤 2**: 在字典注册

```python
self.generators['flappy-bird'] = lambda: self.generate_flappy_bird(args)
```

**步骤 3**: 更新文档

- SKILL.md: 添加游戏类型说明
- game-templates.md: 添加模板参考

### 6.2 外部模板加载 (预留)

```python
# assets/game-templates/ 目录结构
assets/
└── game-templates/
    ├── flappy-bird.html    # 模板文件
    ├── sudoku.html
    └── puzzle.html
```

```python
def load_external_template(game_type: str) -> str:
    """从外部目录加载模板"""
    template_path = f"assets/game-templates/{game_type}.html"
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            return f.read()
    return None  # 回退到内置模板
```

### 6.3 配置化扩展 (未来规划)

```yaml
# games.yaml - 游戏配置文件
games:
  snake:
    name: "贪吃蛇"
    template: "snake"
    default_speed: 5
    speed_range: [1, 10]
    
  breakout:
    name: "打砖块"
    template: "breakout"
    difficulties:
      easy: { ball_speed: 3, lives: 5 }
      normal: { ball_speed: 5, lives: 3 }
      hard: { ball_speed: 7, lives: 1 }
```

---

## 7. 技术选型

### 7.1 为什么选择 Python

| 考量 | Python | Node.js | Go |
|------|--------|---------|-----|
| AI Agent 原生支持 | ✅ | ⚠️ 需额外配置 | ❌ |
| 脚本编写效率 | ✅ | ⚠️ | ⚠️ |
| 跨平台兼容性 | ✅ | ✅ | ✅ |
| 字符串处理 | ✅ | ✅ | ⚠️ |
| 学习曲线 | ✅ | ⚠️ | ⚠️ |

### 7.2 为什么选择 HTML5 Canvas

| 考量 | Canvas | WebGL | SVG |
|------|--------|-------|-----|
| 2D 性能 | ✅ | ⚠️ 过度 | ❌ 差 |
| API 复杂度 | ✅ 简单 | ⚠️ 复杂 | ✅ 简单 |
| 浏览器支持 | ✅ 99%+ | ✅ 95%+ | ✅ 99%+ |
| 游戏类型覆盖 | ✅ 2D全支持 | ✅ 3D | ⚠️ 有限 |

### 7.3 为什么选择 Three.js

| 考量 | Three.js | Babylon.js | 原生 WebGL |
|------|----------|------------|------------|
| 上手难度 | ✅ 简单 | ⚠️ 中等 | ❌ 困难 |
| 社区生态 | ✅ 庞大 | ⚠️ 中等 | ❌ 无 |
| CDN 可用性 | ✅ cdnjs | ✅ cdnjs | N/A |
| 学习资源 | ✅ 丰富 | ⚠️ 一般 | ❌ 稀少 |

### 7.4 版本锁定策略

```html
<!-- 锁定到稳定版本，避免未来Breaking Change -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<!-- Three.js r128 发布于 2021-01， LTS 稳定版本 -->
```

---

## 8. 性能优化

### 8.1 2D 游戏优化

```javascript
// ❌ 每次重绘网格线
function render() {
    ctx.clearRect(0, 0, width, height);
    drawGrid();      // 重复绘制
    drawSnake();
    drawFood();
}

// ✅ 离屏 Canvas 缓存静态元素
const gridCanvas = document.createElement('canvas');
const gridCtx = gridCanvas.getContext('2d');
function drawGridOnce() {
    // 只绘制一次
    for (let x = 0; x < width; x += gridSize) {
        gridCtx.moveTo(x, 0);
        gridCtx.lineTo(x, height);
    }
    gridCtx.stroke();
}
function render() {
    ctx.clearRect(0, 0, width, height);
    ctx.drawImage(gridCanvas, 0, 0);  // 复用缓存
    drawSnake();
    drawFood();
}
```

### 8.2 3D 碰撞检测优化

```javascript
// ❌ 全量检测
function checkCollisions() {
    for (const obstacle of obstacles) {
        if (distance(player, obstacle) < threshold) {
            // 碰撞处理
        }
    }
}

// ✅ 空间哈希 (简化实现)
function checkNearbyCollisions() {
    const gridX = Math.floor(player.x / GRID_SIZE);
    const gridY = Math.floor(player.z / GRID_SIZE);
    
    // 只检测相邻格子内的物体
    for (let dx = -1; dx <= 1; dx++) {
        for (let dz = -1; dz <= 1; dz++) {
            const cell = spatialHash.get(`${gridX+dx},${gridY+dz}`);
            if (cell) {
                // 检测碰撞
            }
        }
    }
}
```

---

## 9. 错误处理

### 9.1 分层错误处理

```python
def main():
    try:
        args = parse_arguments()
        validate_args(args)
        html = generate_game(args)
        write_output(html, args.output)
        print_success(args)
    except ValidationError as e:
        print_error(f"参数错误: {e}")
        sys.exit(1)
    except FileAccessError as e:
        print_error(f"文件写入失败: {e}")
        sys.exit(2)
    except Exception as e:
        print_error(f"未知错误: {e}")
        sys.exit(3)
```

### 9.2 参数校验规则

| 参数 | 类型 | 范围 | 默认值 |
|------|------|------|--------|
| speed | int | 1-10 | 5 |
| width | int | 100-800 (tetris有效) | 300 |
| height | int | 200-600 (tetris有效) | 600 |
| difficulty | str | easy/normal/hard | normal |
| title | str | 1-50字符 | 游戏名 |
| output | path | 当前目录内 | game.html |

---

## 10. 测试策略

### 10.1 单元测试覆盖

```python
import unittest

class TestSnakeGame(unittest.TestCase):
    def test_xss_protection(self):
        """XSS防护测试"""
        result = generate_snake(title='<script>alert(1)</script>')
        self.assertNotIn('<script>', result)
        self.assertIn('&lt;script&gt;', result)
    
    def test_path_traversal_blocked(self):
        """路径遍历防护测试"""
        with self.assertRaises(ValueError):
            validate_output('/etc/cron.d/malicious')
    
    def test_speed_range(self):
        """速度参数范围测试"""
        with self.assertRaises(ValidationError):
            generate_snake(speed=0)  # 超出范围
```

### 10.2 生成物测试

```bash
# 自动化生成 + 浏览器测试
for script in scripts/*.py; do
    python "$script" --output "/tmp/test.html"
    # 使用 puppeteer 验证页面加载
    node test-browser.js "/tmp/test.html"
done
```

---

## 11. 未来规划

| 阶段 | 功能 | 优先级 |
|------|------|--------|
| v1.1 | 添加 Flappy Bird 游戏 | P1 |
| v1.1 | 添加消消乐游戏 | P1 |
| v1.2 | 外部模板加载机制 | P2 |
| v1.2 | 配置文件扩展 | P2 |
| v1.3 | 游戏皮肤/主题系统 | P3 |
| v1.3 | 排行榜功能 | P3 |
| v2.0 | 多人对战支持 | P4 |

---

## 12. 附录

### A. 文件清单

```
web-game-dev/
├── SKILL.md                      # 入口文档 (186行)
├── ARCHITECTURE.md               # 本文档
├── scripts/
│   ├── game_generator.py         # 统一生成器 (819行)
│   ├── snake_game.py            # 贪吃蛇 (370行)
│   ├── breakout_game.py         # 打砖块 (387行)
│   ├── tetris_game.py           # 俄罗斯方块 (428行)
│   └── three_d_scene.py         # 3D场景 (749行)
├── references/
│   ├── game-dev-guide.md         # 开发指南
│   └── game-templates.md         # 模板参考
└── assets/
    └── game-templates/          # 扩展模板目录(预留)
```

### B. 依赖清单

| 依赖 | 版本 | 用途 |
|------|------|------|
| Python | >=3.8 | 运行时 |
| argparse | 内置 | CLI解析 |
| html | 内置 | XSS防护 |

### C. CDN 资源

| 库 | URL | 版本 |
|----|-----|------|
| Three.js | cdnjs.cloudflare.com | r128 |

### D. 浏览器兼容性

| 浏览器 | 最低版本 | 支持功能 |
|--------|----------|----------|
| Chrome | 65+ | 全部 |
| Firefox | 62+ | 全部 |
| Safari | 11.1+ | 全部 |
| Edge | 79+ | 全部 |
| IE | 不支持 | - |
