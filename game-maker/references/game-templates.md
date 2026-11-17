# 游戏模板索引

本文档列出 web-game-dev 技能支持的游戏类型和模板信息。

## 已实现的游戏类型

| 游戏类型 | 脚本 | 状态 | 说明 |
|---------|------|------|------|
| 贪吃蛇 | `snake_game.py` | ✅ 已实现 | 支持速度调节、移动端控制 |
| 打砖块 | `breakout_game.py` | ✅ 已实现 | 支持简单/普通/困难难度 |
| 俄罗斯方块 | `tetris_game.py` | ✅ 已实现 | 支持宽高和速度调节 |
| 3D弹球 | `three_d_scene.py --type sphere` | ✅ 已实现 | 收集物品、障碍物碰撞 |
| 3D跑酷 | `three_d_scene.py --type cube` | ✅ 已实现 | 无限跑酷、障碍物躲避 |
| 3D迷宫 | `three_d_scene.py --type maze` | ✅ 已实现 | 自动迷宫生成、小地图 |

## 游戏生成示例

### 贪吃蛇
```bash
python scripts/snake_game.py --speed 8 --title "My Snake"
```

### 打砖块
```bash
python scripts/breakout_game.py --difficulty hard
```

### 俄罗斯方块
```bash
python scripts/tetris_game.py --width 300 --height 600 --speed 7
```

### 3D游戏
```bash
python scripts/three_d_scene.py --type maze --title "My Maze"
```

## 统一游戏生成器

使用 `game_generator.py` 可以生成所有支持的类型：

```bash
python scripts/game_generator.py --type snake --speed 5
python scripts/game_generator.py --type breakout --speed 8
python scripts/game_generator.py --type tetris --speed 6
python scripts/game_generator.py --type 3d-sphere
```

## 技术规格

### 2D游戏
- **渲染**: HTML5 Canvas 2D API
- **无外部依赖**: 所有代码内联在单个HTML文件中
- **浏览器兼容**: 使用 fillRect 替代 roundRect，支持所有现代浏览器

### 3D游戏
- **渲染**: Three.js r128 (通过CDN加载)
- **网络要求**: 需要网络连接加载Three.js库
- **兼容性**: WebGL支持的所有浏览器

## 统一速度公式

所有游戏使用相同的速度计算公式，确保一致的体验：

```
interval = 500 - speed * 40 (毫秒)
```

| Speed | Interval |
|-------|----------|
| 1     | 460ms    |
| 5     | 300ms    |
| 10    | 100ms    |

## 导出配置

游戏生成脚本支持以下通用参数：

| 参数 | 说明 | 范围 |
|------|------|------|
| `--width` | 画布宽度 | 2D: 200-1920, 3D: 固定 |
| `--height` | 画布高度 | 2D: 200-1080, 3D: 固定 |
| `--speed` | 游戏速度 | 1-10 |
| `--title` | 游戏标题 | 任意字符串(自动转义) |
| `--output` | 输出文件 | 相对路径 |
