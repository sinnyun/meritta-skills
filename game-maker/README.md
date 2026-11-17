# web-game-dev 项目说明

> AI 驱动的网页小游戏生成器 - 让每个人都能轻松创建自己的游戏

## 项目简介

web-game-dev 是一个基于 AI Agent 的技能包，通过 Python 脚本生成可在浏览器直接运行的 HTML5 小游戏。无需安装任何依赖（2D游戏），浏览器打开即可玩。

### 核心特性

- **零部署成本** - 生成单个 HTML 文件，双击即可运行
- **AI 辅助开发** - 结合 AI Agent 提供从设计到调试的全流程支持
- **多游戏支持** - 贪吃蛇、打砖块、俄罗斯方块、3D场景
- **安全可靠** - XSS防护、路径校验、参数验证
- **跨平台兼容** - 支持所有现代浏览器

## 快速开始

### 环境要求

- Python >= 3.8
- 现代浏览器 (Chrome/Firefox/Safari/Edge)

### 安装

```bash
# 克隆项目
git clone <repository>
cd web-game-dev

# 无需安装任何依赖！
```

### 使用示例

#### 贪吃蛇游戏

```bash
python scripts/snake_game.py --output snake.html
# 浏览器打开 snake.html 即可游玩
```

#### 打砖块游戏

```bash
python scripts/breakout_game.py --difficulty hard --output breakout.html
```

#### 俄罗斯方块

```bash
python scripts/tetris_game.py -w 300 -H 600 --output tetris.html
```

#### 3D 场景游戏

```bash
python scripts/three_d_scene.py --type maze --output maze.html
```

#### 统一生成器

```bash
python scripts/game_generator.py --type snake --speed 5 --title "我的贪吃蛇"
```

## 游戏列表

### 2D 游戏

| 游戏 | 命令 | 说明 |
|------|------|------|
| 贪吃蛇 | `snake_game.py` | 经典贪吃蛇，支持速度调节 |
| 打砖块 | `breakout_game.py` | 三种难度，5/3/1条命 |
| 俄罗斯方块 | `tetris_game.py` | 自定义画布尺寸 |

### 3D 游戏

| 游戏 | 命令 | 说明 |
|------|------|------|
| 3D 弹球 | `three_d_scene.py --type sphere` | 收集物品得分 |
| 3D 方块 | `three_d_scene.py --type cube` | 穿越障碍 |
| 3D 迷宫 | `three_d_scene.py --type maze` | 第一人称迷宫探索 |

## 命令行参数

### 通用参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--output`, `-o` | 输出文件路径 | game.html |
| `--title`, `-t` | 游戏标题 | 游戏默认名 |

### 游戏专属参数

#### snake_game.py

```bash
python scripts/snake_game.py [options]
  --speed, -s    速度 1-10 (越大约快)  [default: 5]
  --width, -w    画布宽度 像素         [default: 400]
  --height, -H   画布高度 像素          [default: 400]
```

#### breakout_game.py

```bash
python scripts/breakout_game.py [options]
  --difficulty, -d  难度 easy/normal/hard  [default: normal]
```

#### tetris_game.py

```bash
python scripts/tetris_game.py [options]
  --width, -w    画布宽度 像素  [default: 300]
  --height, -H   画布高度 像素  [default: 600]
```

#### three_d_scene.py

```bash
python scripts/three_d_scene.py [options]
  --type, -t   场景类型: sphere/cube/maze  [default: sphere]
```

## 游戏操作说明

### 贪吃蛇

- **方向键** - 控制蛇的移动方向
- **吃到食物** - 得分 +10，蛇身增长
- **撞墙/撞自己** - 游戏结束
- **空格键** - 重新开始

### 打砖块

- **方向键/鼠标** - 控制挡板移动
- **打破所有砖块** - 胜利
- **球落到底部** - 失去一条命
- **R 键** - 重新开始

### 俄罗斯方块

- **方向键** - 移动方块
- **上箭头/空格** - 旋转方块
- **下方箭头** - 加速下落
- **消除满行** - 得分

### 3D 迷宫

- **WASD** - 移动
- **鼠标** - 视角转向
- **收集绿色球** - 得分
- **避开红色障碍** - 碰撞则减分

## 安全特性

| 安全措施 | 说明 |
|----------|------|
| XSS 防护 | 所有用户输入经过 HTML 转义 |
| 路径隔离 | 禁止写入系统目录和父目录 |
| 参数校验 | 范围检查、类型验证 |
| CSP 策略 | 内置内容安全策略 |

## 项目结构

```
web-game-dev/
├── SKILL.md                      # AI Agent 入口文档
├── ARCHITECTURE.md               # 技术架构文档
├── scripts/
│   ├── game_generator.py         # 统一生成器
│   ├── snake_game.py            # 贪吃蛇
│   ├── breakout_game.py         # 打砖块
│   ├── tetris_game.py           # 俄罗斯方块
│   └── three_d_scene.py         # 3D 场景
├── references/
│   ├── ARCHITECTURE.md          # 技术架构
│   ├── game-dev-guide.md        # 游戏开发指南
│   └── game-templates.md        # 模板参考
└── assets/
    └── game-templates/          # 扩展模板目录(预留)
```

## 开发指南

### 添加新游戏

1. 在 `scripts/` 创建新脚本
2. 参考现有脚本的结构
3. 添加参数解析和验证
4. 更新 `game_generator.py` 注册新游戏
5. 更新本文档

### 本地测试

```bash
# 生成所有游戏
for script in scripts/*.py; do
    name=$(basename "$script" .py)
    python "$script" --output "/tmp/test_$name.html"
done

# 验证生成结果
ls -la /tmp/test_*.html
```

## 技术栈

| 层级 | 技术 |
|------|------|
| 生成层 | Python 3.8+ |
| 渲染层 | HTML5 Canvas / Three.js r128 |
| 输出格式 | 单 HTML 文件 |

## 性能指标

| 指标 | 数值 |
|------|------|
| 贪吃蛇延迟 | 50-140ms (可调) |
| 3D 场景 FPS | 60 FPS |
| 生成时间 | <100ms |
| 输出文件大小 | 2D: 8-15KB / 3D: 20-30KB |

## 常见问题

### Q: 生成的 3D 游戏无法显示？

A: 3D 游戏依赖 Three.js CDN，需要网络连接。内网环境请使用 2D 游戏。

### Q: 如何调整游戏难度？

A: 使用 `--speed` 参数调整速度，或使用 `--difficulty` 选择预设难度。

### Q: 游戏在手机上无法运行？

A: 部分游戏支持触摸控制，建议在桌面浏览器体验完整功能。

### Q: 如何添加自定义游戏？

A: 参考 `game-dev-guide.md` 中的开发指南，或使用 AI Agent 辅助开发。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing`)
5. 创建 Pull Request

## 许可证

MIT License

## 更新日志

### v1.0 (2025-05-17)

- 初始版本发布
- 支持 6 种游戏类型
- XSS 和路径安全修复

---

**Made with ❤️ by AI Agent**
