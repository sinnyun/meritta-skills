# 已知连接器故障模式

本文件包含常见连接器的故障模式匹配和面向电脑小白用户的详细修复步骤。

AI 在输出手动修复方案时，优先参考本文件中的步骤模板，根据实际诊断上下文调整细节。**手动安装方案须同时提供命令行方案（终端粘贴执行的完整命令）与图形化方案（浏览器下载→双击安装→向导）两种方式**，用户任选其一。

## 目录

- [通用指南](#通用指南)
  - [应用内连接器操作指南](#应用内连接器操作指南)
  - [通过自定义连接器弹框修改配置](#通过自定义连接器弹框修改配置)
  - [运行时自动安装矩阵](#运行时自动安装矩阵)
  - [Node.js 安装指南](#nodejs-安装指南)
  - [mcp_settings.json 手动编辑](#mcp_settingsjson-手动编辑)
  - [网络问题排查](#网络问题排查)
  - [Windows 安全软件排查](#windows-安全软件排查)
- [连接器特定指南](#连接器特定指南)
  - [GitCode 连接器](#gitcode-连接器)
  - [Figma 连接器](#figma-连接器)
  - [Email Inbox 连接器](#email-inbox-连接器)
  - [Playwright 连接器](#playwright-连接器)
  - [Chrome MCP 连接器](#chrome-mcp-连接器)
  - [Computer Use 连接器](#computer-use-连接器)

---

## 通用指南

### 应用内连接器操作指南

当需要引导用户在 CodeArtsWork 应用内操作连接器时，按以下步骤描述：

**打开连接器页面：**
1. 在 CodeArtsWork 应用左侧导航栏，点击"连接器"图标
2. 你应该看到：连接器市场列表，每个连接器显示为一个卡片，包含图标、名称和描述

**查找特定连接器：**
1. 在连接器页面顶部的搜索框中，输入连接器名称（如"GitCode"）
2. 你应该看到：列表筛选为匹配的连接器卡片
3. 如果没找到，点击搜索框旁边的分类筛选，切换到"开发工具"等分类查看

**安装连接器：**
1. 找到目标连接器卡片，点击卡片任意位置
2. 你应该看到：弹出连接器详情对话框，显示连接器信息和配置表单
3. 在配置区域填写所需的字段（如 Token、API Key 等）
4. 点击对话框右下角的"安装"按钮
5. 你应该看到：弹出"安装成功"提示，卡片上出现状态指示灯

**更新已安装连接器的配置：**
1. 找到已安装的连接器卡片，点击卡片
2. 在弹出的详情对话框中，修改配置输入框中的值
3. 点击"更新"按钮
4. 你应该看到：弹出"更新成功"提示

**重新启用连接器：**
1. 在已安装连接器卡片上，找到右上角的开关
2. 如果开关是关闭的（灰色），点击开关打开它
3. 等待 5-10 秒，观察状态指示灯：
   - 🟢 绿色 = 连接成功
   - 🔴 红色 = 连接失败
   - 🟡 黄色/闪烁 = 正在连接中，请稍等

**卸载并重新安装连接器（兜底方案）：**
1. 找到已安装的连接器卡片，点击卡片打开详情
2. 在详情对话框右下角，点击"卸载"按钮
3. 你应该看到：卡片恢复到未安装状态
4. 再次点击该卡片，重新填写配置，点击"安装"

---

### 通过自定义连接器弹框修改配置

**适用场景：**
- 连接器详情弹框中的配置项不全（模板只定义了部分占位符字段，但连接器实际需要更多 environment 变量）
- 需要添加自定义 environment 变量（如代理地址、自定义 API 路径等）
- 需要修改 `mcp_settings.json` 中的完整配置，但不想用记事本手动编辑（应用内编辑有 JSON 校验，更安全）

**与连接器详情弹框的区别：**

| 对比项 | 连接器详情弹框 | 自定义连接器弹框 |
|--------|--------------|----------------|
| 显示哪些配置项 | 仅模板中定义的占位符字段 | 完整 JSON（所有 server 的全部配置） |
| 能否添加新字段 | 不能 | 能（自由编辑 JSON） |
| JSON 校验 | 不涉及 | 保存前自动校验，格式错误会提示 |
| 编辑器 | 表单输入框 | Monaco 代码编辑器（带语法高亮） |
| 适用场景 | 填写 Token、API Key 等标准配置 | 添加自定义变量、批量修改、高级配置 |

**如何打开自定义连接器弹框：**
1. 在 CodeArtsWork 应用左侧导航栏，点击"连接器"
2. 你应该看到：连接器市场列表页面
3. 在页面顶部（搜索框附近），找到"自定义配置"按钮
4. 点击"自定义配置"按钮
5. 你应该看到：弹出一个大对话框，内含代码编辑器，显示 JSON 格式的配置内容

**编辑配置：**
1. 在代码编辑器中，找到需要修改的连接器配置段（按连接器名称查找，如 `gitcode`、`figma` 等）
2. 在该连接器的 `environment` 部分，修改或添加键值对
   - 修改现有值：将旧值替换为新值（如将 `"GITCODE_TOKEN": ""` 改为 `"GITCODE_TOKEN": "你的实际Token"`）
   - 添加新变量：在 `environment` 对象中添加新行，格式为 `"变量名": "值"`，注意逗号分隔
3. 你应该看到：编辑器中 JSON 内容已更新，修改的部分有高亮标记

**保存配置：**
1. 点击对话框底部的"保存"按钮
2. 如果 JSON 格式有误，你应该看到：弹出错误提示"JSON 格式无效"，请检查是否有遗漏逗号、引号不匹配等问题
3. 如果 JSON 格式正确，你应该看到：对话框关闭，连接器列表状态自动刷新（各连接器重新尝试连接）

**示例：通过自定义连接器弹框为 GitCode 添加代理配置：**

1. 打开自定义连接器弹框
2. 找到 `gitcode` 配置段：
   ```json
   "gitcode": {
     "command": ["node", "..."],
     "environment": {
       "GITCODE_TOKEN": "你的Token",
       "GITCODE_API_BASE_URL": "https://api.gitcode.com/api/v5"
     },
     "enabled": true
   }
   ```
3. 在 `environment` 中添加代理变量（在最后一行后面加逗号，再加新行）：
   ```json
   "environment": {
     "GITCODE_TOKEN": "你的Token",
     "GITCODE_API_BASE_URL": "https://api.gitcode.com/api/v5",
     "HTTPS_PROXY": "http://127.0.0.1:8080"
   }
   ```
4. ⚠️ 注意逗号：最后一行（`HTTPS_PROXY` 那行）后面不要加逗号，但前面的行（`GITCODE_API_BASE_URL` 那行）末尾要加逗号
5. 点击"保存"
6. 你应该看到：对话框关闭，GitCode 连接器状态更新

**空配置模板：**

如果 `mcp_settings.json` 为空或不存在，编辑器会显示一个示例模板：
```json
{
  "my-custom-mcp": {
    "type": "local",
    "command": ["npx", "-y", "@modelcontextprotocol/server-memory"],
    "environment": {},
    "timeout": 5000,
    "enabled": true
  }
}
```
可基于此模板创建自定义 MCP 连接器配置。

---

### 运行时自动安装矩阵

**本矩阵供 AI 在 SKILL.md Step 4.3 安装运行时（Node.js / Python / uv）时使用。** 依据诊断上下文"运行环境检测"段的**操作系统 / 架构 / 终端**选择对应命令。执行前先 `command --version` 二次确认缺失，执行后必须 `command --version` 验证输出版本号。

#### 下载地址优先级与内网镜像兜底

安装命令执行失败或公共源（nodejs.org / github.com / astral.sh）不可达时，**按以下三级顺序取下载地址**：

1. **product.json 动态配置（最优先）**：读取应用安装目录（打包后为 `resources` 目录，开发态为项目根目录）下的 `product.json` 的 `updateMcpEnvService` 字段，其中 `win32X64NodeUrl`、`darwinArm64UxUrl` 等字段为对应平台×架构的最新内网地址（命名规则：`{platform}{Arch}{Node|Ux}Url`）
2. **内网镜像静态表（本文件兜底）**：见下方地址表，用于下载官方安装包/压缩包——全局安装（winget/apt/brew）失败时，供用户手动安装（命令行方案或图形化方案，见「兜底手动指导」）
3. **公共源**：`https://nodejs.org` / `https://github.com` / `https://astral.sh`，仅当前两级均不可用时尝试

> 内网环境公共源几乎必然失败（代理/防火墙拦截，如 `ERR_TUNNEL_CONNECTION_FAILED`）。AI 应在报错或无响应 **3-5 秒内快速切换下一级**，不反复重试同一来源。

##### Node.js 内网镜像地址（华为镜像站，已验证）

| 平台 | 架构 | 下载地址 | 格式 |
|------|------|---------|------|
| Windows | x64 | `https://mirrors.tools.huawei.com/nodejs/v20.18.1/node-v20.18.1-win-x64.zip` | zip |
| Windows | arm64 | `https://mirrors.tools.huawei.com/nodejs/v20.18.1/node-v20.18.1-win-arm64.zip` | zip |
| Linux | x64 | `https://mirrors.tools.huawei.com/nodejs/v20.18.1/node-v20.18.1-linux-x64.tar.gz` | tar.gz |
| Linux | arm64 | `https://mirrors.tools.huawei.com/nodejs/v20.18.1/node-v20.18.1-linux-arm64.tar.gz` | tar.gz |
| macOS | x64 | `https://mirrors.tools.huawei.com/nodejs/v20.18.1/node-v20.18.1-darwin-x64.tar.gz` | tar.gz |
| macOS | arm64 | `https://mirrors.tools.huawei.com/nodejs/v20.18.1/node-v20.18.1-darwin-arm64.tar.gz` | tar.gz |

> Node.js v20.18.1 为 LTS；华为镜像站是 nodejs.org 的完整镜像，可替换目录为其他版本号。

##### uv 内网镜像地址（华为 Artifactory，Windows/Linux 已验证，macOS 待运维确认）

| 平台 | 架构 | 下载地址 |
|------|------|---------|
| Windows | x64 | `https://cmc-lfg-artifactory.cmc.tools.huawei.com/artifactory/generic-codemate-plugin/hw-codemate-plugin/uv-x86_64-pc-windows-msvc.zip` |
| Windows | arm64 | `https://cmc-lfg-artifactory.cmc.tools.huawei.com/artifactory/generic-codemate-plugin/hw-codemate-plugin/uv-aarch64-pc-windows-msvc.zip` |
| Linux | x64 | `https://cmc-lfg-artifactory.cmc.tools.huawei.com/artifactory/generic-codemate-plugin/hw-codemate-plugin/uv-x86_64-unknown-linux-gnu.tar.gz` |
| Linux | arm64 | `https://cmc-lfg-artifactory.cmc.tools.huawei.com/artifactory/generic-codemate-plugin/hw-codemate-plugin/uv-aarch64-unknown-linux-gnu.tar.gz` |
| macOS | x64 | `https://cmc-lfg-artifactory.cmc.tools.huawei.com/artifactory/generic-codemate-plugin/hw-codemate-plugin/uv-x86_64-apple-darwin.tar.gz`（⚠️ 推导值未验证） |
| macOS | arm64 | `https://cmc-lfg-artifactory.cmc.tools.huawei.com/artifactory/generic-codemate-plugin/hw-codemate-plugin/uv-aarch64-apple-darwin.tar.gz`（⚠️ 推导值未验证） |

##### Python 内网镜像说明

- 已验证的内网镜像方案暂未覆盖 Python 完整安装包
- `uv python install 3.x` 从 GitHub 下载，内网同样不可达（`allow-insecure-host` 仅放开 HTTP 访问，不解决网络隔离）
- 内网场景优先使用系统包管理器安装 Python（Windows 用 `winget install Python.Python.3.12`，Linux 用 `sudo apt install python3`，macOS 用 `brew install python@3.12`），均失败再转下方「兜底手动指导」的下载安装包方案

#### 命令矩阵

| 运行时 | Windows | macOS | Linux |
|--------|---------|-------|-------|
| Node.js | `winget install OpenJS.NodeJS.LTS` | `brew install node` | `sudo apt install -y nodejs` 或 nvm（用户级）：`curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh \| bash`，新开终端后 `nvm install --lts` |
| Python | `winget install Python.Python.3.12` | `brew install python@3.12` | `sudo apt install -y python3` 或 pyenv：`curl https://pyenv.run \| bash`，新开终端后 `pyenv install 3.12 && pyenv global 3.12` |
| uv | `powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 \| iex"` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |

#### 使用规则

1. **二次确认**：执行前先跑 `node --version` / `python --version` / `uv --version`，确认确实缺失（检测结果可能滞后）
2. **执行确认**：列出将执行的命令，等待用户同意（遵循 SKILL.md Step 3 询问机制）
3. **验证**：执行后必须 `command --version` 确认输出版本号，并检查可执行文件存在（`where node` / `which node`）；校验失败视为安装失败
4. **PATH 生效**：新装运行时需重启 CodeArtsWork 或新开终端才生效，务必提醒用户；若用户级 PATH 不生效，须注册到**系统变量（Machine）**（需管理员权限）
5. **版本选择原则**：
   - Node.js：选 LTS（长期支持版），不要装 Current 尝鲜版
   - Python：选 3.10-3.12 稳定版（连接器兼容性最好）
   - uv：装最新稳定版即可
6. **winget 依赖**：需要 Windows 10 1809+ 且商店自带 winget；若 `winget` 命令不存在，直接转下方兜底手动指导
7. **下载源切换**：内网环境公共源失败时，按上方「下载地址优先级与内网镜像兜底」切换到华为镜像地址，不反复重试公共源

#### 常见失败与应对

| 失败现象 | 原因 | 应对 |
|---------|------|------|
| `要求提升权限` / UAC / 访问被拒绝 | winget 安装需管理员确认 | 允许以管理员权限执行（如 PowerShell 以管理员运行），仍失败转兜底手动指导 |
| 网络超时 / `ERR_TUNNEL_CONNECTION_FAILED` | 公司网络访问 GitHub/官方源受限 | **切换到华为内网镜像地址**（见上方地址表）；仍失败则转兜底手动指导 |
| `brew: command not found` | macOS 未安装 Homebrew | 安装 Homebrew（`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`）或转兜底：官网下载 .pkg 安装包 |
| winget 安装成功但 `--version` 无输出 | PATH 未刷新 | 提示新开终端 / 重启 CodeArtsWork |
| `sudo` 需要密码 | Linux 系统级安装 | 允许执行 `sudo`；若无法交互输入密码，提示用户协助提供密码，或改用 nvm/pyenv 用户级安装 |

#### 兜底手动指导（命令行安装失败 / AI 无法执行命令时）

命令行安装失败，或 AI 当前环境无法执行命令（如权限被拒绝）时，**不要反复重试**，输出手动安装步骤。**手动方案同时提供两种方式，用户任选其一**：

- **方式一：命令行方案**：用户可在终端粘贴执行的完整命令（已验证可执行通过）
- **方式二：图形化方案**：打开浏览器下载安装包 → 双击安装 → 跟随向导 → 验证（面向电脑小白）

**Node.js：**

方式一（命令行，请逐条粘贴执行）：
> ⚠️ 每条命令单独复制到终端，粘贴后按回车，看到上一条执行完成后再粘贴下一条。

1. 按 `Win + R`，输入 `powershell`，回车
2. 粘贴执行第 1 条（安装）：`winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements`
3. 粘贴执行第 2 条（验证）：`node --version`，应显示 `v20.x` 及以上
4. ⚠️ 若新开终端仍找不到 `node`，说明用户级 PATH 未生效：按下方"方式二"的步骤，在"系统变量"的 `Path` 中新增 Node.js 安装目录（需要管理员权限）

方式二（图形化）：
- 按下方 [Node.js 安装指南](#nodejs-安装指南) 输出（Windows `.msi` / macOS `.pkg`，官网 `https://nodejs.org` 选 LTS，安装向导自动配置 PATH）
- 内网用户无法访问官网时，用华为镜像 `https://mirrors.tools.huawei.com/nodejs/v20.18.1/` 下载对应平台安装包

**Python：**

方式一（命令行，请逐条粘贴执行）：
> ⚠️ 每条命令单独复制到终端，粘贴后按回车，看到上一条执行完成后再粘贴下一条。

1. 按 `Win + R`，输入 `powershell`，回车
2. 粘贴执行第 1 条（安装）：`winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements`
3. 粘贴执行第 2 条（验证）：`python --version`，应显示 `Python 3.12.x`
4. ⚠️ 若新开终端仍找不到 `python`，说明用户级 PATH 未生效：按"方式二（Windows）"在图形界面中确认/补充 Python 安装目录到"系统变量"的 `Path`（需要管理员权限）

方式二（图形化，Windows）：
1. 打开浏览器，访问 `https://www.python.org/downloads/`
2. 你应该看到：页面上一个黄色按钮"Download Python 3.x.x"
3. 点击黄色按钮下载 `.exe` 安装包（约 25MB，保存在"下载"文件夹）
4. 双击下载的安装包，弹出安装向导
5. ⚠️ **第一页最下方必须勾选"Add python.exe to PATH"**（添加 Python 到 PATH），否则系统找不到 python
6. 点击"Install Now"
7. 你应该看到：进度条走完后显示"Setup was successful"
8. 验证：按 `Win + R`，输入 `cmd`，回车，输入 `python --version` 回车，应显示 `Python 3.x.x`
9. 重启 CodeArtsWork 后重新启用连接器

方式二（图形化，macOS / Linux）：
- macOS：访问 `https://www.python.org/downloads/macos/` 下载 `.pkg` 双击安装，安装向导自动完成，验证 `python3 --version`
- Linux：使用系统"软件中心"搜索安装 Python3，或联系管理员协助安装

**uv：**

方式一（命令行，已验证可执行通过，请逐条粘贴执行）：
> ⚠️ 每条命令单独复制到终端，粘贴后按回车，看到上一条执行完成后再粘贴下一条。不要一次粘贴多行。

1. 按 `Win + R`，输入 `powershell`，回车
2. 粘贴执行第 1 条（安装 uv）：`powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - 此命令从 Astral 官方源下载安装脚本，安装到 `%USERPROFILE%\.local\bin\`（用户目录，无需管理员权限），自动配置用户级 PATH
3. 粘贴执行第 2 条（重载环境变量）：`$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")`
   - （或直接关闭并重新打开 PowerShell 终端，推荐）
4. 粘贴执行第 3 条（验证）：`uv --version`，再粘贴执行 `uvx --version`，都应输出版本号（如 `uv 0.x.x`）
5. ⚠️ 若新开终端仍找不到 `uv`，说明用户级 PATH 未生效：需将 `%USERPROFILE%\.local\bin` 注册到**系统变量（Machine）**——按下方"方式二"第 5 步操作，在"系统变量"的 `Path` 中新增该目录（需要管理员权限）
6. macOS/Linux 用户在终端逐条执行：先 `curl -LsSf https://astral.sh/uv/install.sh | sh`，再新开终端执行 `uv --version` 验证

方式二（图形化，Windows）：
1. 打开浏览器，访问华为 Artifactory 下载地址（见上方 uv 内网镜像地址表，选 Windows 对应平台），下载 `.zip` 文件
2. 右键点击下载的 `.zip` 文件 → 选择"全部解压缩" → 点击"提取"
3. 你应该看到：解压出一个文件夹，里面有 `uv.exe`
4. 在 `C:\Users\你的用户名` 下新建一个文件夹，命名为 `uv`，把 `uv.exe` 复制进去
5. 配置系统路径（让系统能找到 uv.exe，注册到**系统变量**）：
   - 按 `Win + R`，输入 `sysdm.cpl`，回车
   - 你应该看到："系统属性"窗口，点击"高级"选项卡，点击右下角"环境变量"按钮
   - 在"系统变量"（上半区）中找到 `Path`，选中它，点击"编辑"
   - 点击"新建"，输入 `C:\Users\你的用户名\uv`，点击"确定"关闭所有窗口
   - ⚠️ 修改系统变量需要管理员权限，若弹出"用户账户控制"窗口，点击"是"
6. 验证：按 `Win + R`，输入 `cmd`，回车，输入 `uv --version` 回车，应显示 `uv 0.x.y`
7. macOS/Linux 用户：联系管理员协助安装 uv

#### 验证命令汇总

| 运行时 | 验证命令 | 期望输出 |
|--------|---------|---------|
| Node.js | `node --version` | `v20.x` 及以上 |
| Python | `python --version` / `python3 --version` | `Python 3.10+` |
| uv | `uv --version` | `uv 0.x.y` |

---

### Node.js 安装指南

**适用场景：** 诊断上下文中错误类别为 `environment_missing`，且 `command` 首词为 `node` 或 `npx`。几乎所有连接器都依赖 Node.js 运行时。

**面向用户的手动修复步骤：**

1. 打开浏览器（Chrome、Edge 或 Firefox 均可）
2. 在地址栏输入 `https://nodejs.org` 并按回车
3. 你应该看到：Node.js 官网，页面上有两个绿色下载按钮
4. 点击标有"LTS"（长期支持版）的按钮下载安装包
   - ⚠️ 不要点击"Current"版本，LTS 版本更稳定
   - 下载的文件名类似 `node-v20.18.0-x64.msi`，通常保存在"下载"文件夹中
5. 打开"下载"文件夹（可在浏览器中点击下载记录，点击"在文件夹中显示"）
6. 双击下载的 `.msi` 安装包
7. 如果弹出"是否允许此应用对你的设备进行更改？"对话框，点击"是"
8. 你应该看到：Node.js 安装向导弹出
9. 勾选"I accept the terms in the License Agreement"（我接受许可协议），点击"Next"
10. 继续点击"Next"（下一步）保持默认设置，直到出现"Install"按钮
    - ⚠️ 不要取消勾选"Add to PATH"选项，这个选项让系统能找到 Node.js
11. 点击"Install"按钮，可能会再次弹出管理员权限确认，点击"是"
12. 等待安装进度条走完，点击"Finish"完成安装
13. 验证安装是否成功：
    - 按键盘 `Win + R` 键，打开"运行"对话框
    - 输入 `cmd`，按回车，打开命令提示符（黑色窗口）
    - 输入 `node --version`，按回车
    - 你应该看到：显示版本号（如 `v20.18.0`），说明安装成功
    - 如果显示"'node' 不是内部或外部命令"，说明 PATH 未生效，请重启电脑后再试
14. 完全关闭 CodeArtsWork 应用（点击窗口右上角 X，或在系统托盘图标上右键→退出），然后重新打开
15. 回到连接器页面，重新启用该连接器

---

### mcp_settings.json 手动编辑

**适用场景：** 配置文件格式错误、JSON 解析失败、连接器配置需要手动修改且应用内 UI 无法操作时。

> **优先使用应用内"自定义连接器"弹框**：如果 CodeArtsWork 应用正在运行，建议优先使用"自定义连接器弹框"编辑配置（见上方[通过自定义连接器弹框修改配置](#通过自定义连接器弹框修改配置)章节），它有 JSON 格式校验，比记事本编辑更安全。仅在应用无法启动、弹框无法打开等极端情况下，才使用以下记事本手动编辑方式。

**文件位置：** `C:\Users\你的用户名\.codeartswork\mcp\mcp_settings.json`

**如何打开：**
1. 按键盘 `Win + R` 键，打开"运行"对话框
2. 输入 `%USERPROFILE%\.codeartswork\mcp`，按回车
3. 你应该看到：打开一个文件夹，里面有 `mcp_settings.json` 和 `plugin.json` 文件
4. 右键点击 `mcp_settings.json`，选择"打开方式"→"记事本"
5. 你应该看到：一个 JSON 格式的文本文件，内容类似：
   ```json
   {
     "mcp": {
       "gitcode": {
         "command": ["node", "..."],
         "environment": {
           "GITCODE_TOKEN": "你的Token值",
           "GITCODE_API_BASE_URL": "https://api.gitcode.com/api/v5"
         },
         "enabled": true,
         "timeout": 5000,
         "type": "local"
       }
     }
   }
   ```

**编辑注意事项：**
- ⚠️ 修改前先备份：复制一份文件重命名为 `mcp_settings_backup.json`
- ⚠️ JSON 格式要求严格：每个键值对之间有逗号，最后一个键值对后面不能有逗号
- ⚠️ 所有字符串（键名和值）必须用英文双引号 `"` 包裹，不能用单引号
- 修改完成后保存（Ctrl+S），关闭记事本
- 回到 CodeArtsWork 应用，重新启用连接器

---

### 网络问题排查

**适用场景：** 诊断上下文中错误类别为 `network_timeout`，或错误信息包含 `ECONNREFUSED`、`ETIMEDOUT`、`ECONNRESET`、`ENOTFOUND`。

**面向用户的手动排查步骤：**

1. 检查 VPN/代理是否已连接：
   - 如果你使用公司 VPN，检查 VPN 客户端是否显示"已连接"
   - 如果 VPN 未连接，先连接 VPN 再回到连接器页面重试
   - ⚠️ 部分公司内网服务（如 GitCode）必须连接 VPN 才能访问

2. 检查网络是否正常：
   - 打开浏览器，访问 `https://www.baidu.com`
   - 如果能正常打开页面，说明网络基本正常
   - 如果打不开，检查网线/WiFi 连接，或重启路由器

3. 检查防火墙是否拦截：
   - 如果刚安装了杀毒软件，检查是否拦截了 CodeArtsWork 或 Node.js
   - 参考 [Windows 安全软件排查](#windows-安全软件排查)

4. 检查 DNS 解析：
   - 按 `Win + R`，输入 `cmd`，按回车
   - 输入 `nslookup api.gitcode.com`（将域名替换为实际连接器需要访问的地址），按回车
   - 你应该看到：显示 IP 地址，说明 DNS 正常
   - 如果显示"找不到名称"，说明 DNS 有问题，尝试切换到 8.8.8.8 或 114.114.114.114

5. 完成排查后，回到连接器页面重新启用连接器

---

### Windows 安全软件排查

**适用场景：** 连接器突然无法启动，错误信息包含 `EACCES`、`permission`、`denied`、`spawn` 等。

**Windows Defender 检查：**
1. 按 `Win + I` 打开"设置"
2. 点击"更新和安全"→"Windows 安全中心"
3. 点击"病毒和威胁防护"
4. 在"保护历史记录"中，检查是否有 CodeArtsWork 或 Node.js 被隔离/拦截的记录
5. 如果有，点击"允许"恢复文件

**第三方杀毒软件检查：**
1. 如果你安装了 360 安全卫士、火绒、电脑管家等，打开它们
2. 在"隔离区"或"信任列表"中检查是否有 CodeArtsWork、Node.js、或 `mcp_settings.json` 被拦截
3. 将 CodeArtsWork 安装目录和 `C:\Users\你的用户名\.codeartswork` 添加到信任/白名单

**文件夹权限检查：**
1. 按 `Win + R`，输入 `%USERPROFILE%\.codeartswork`，按回车
2. 右键点击 `mcp` 文件夹，选择"属性"
3. 切换到"安全"选项卡
4. 确认当前用户有"完全控制"权限。如果没有，点击"编辑"添加权限

---

## 连接器特定指南

### GitCode 连接器

- **常见错误**：`GITCODE_TOKEN` 为空或过期
- **错误类别**：`auth_failure` / `config_error`
- **可自动修复**：是（填写 Token 到配置文件）
- **前提条件**：用户有 GitCode 账号
- **配置字段**：`GITCODE_TOKEN`、`GITCODE_API_BASE_URL`（默认 `https://api.gitcode.com/api/v5`）
- **配置指南 URL**：`https://gitcode.com/setting/token-classic`

**面向用户的手动修复步骤：**

#### 第一步：获取 GitCode Token

1. 打开浏览器，在地址栏输入 `https://gitcode.com` 并按回车
2. 你应该看到：GitCode 官网首页
3. 如果未登录，点击页面右上角的"登录"按钮，输入用户名和密码登录
   - 你应该看到：登录后页面右上角显示你的头像和用户名
4. 在地址栏输入 `https://gitcode.com/setting/token-classic` 并按回车
   - 或者：点击右上角头像 → 在下拉菜单中点击"设置" → 在左侧菜单中点击"个人访问令牌"
5. 你应该看到："个人访问令牌"页面，有一个"新建令牌"按钮
6. 点击"新建令牌"按钮
7. 在弹出的对话框中：
   - "令牌名称"输入框：填写一个容易记住的名字，如 `CodeArtsWork`
   - "过期时间"：根据需要选择，建议至少 30 天
   - 权限勾选：至少勾选 `repo`（仓库读写权限），如果需要读取 Issue/PR，也勾选对应权限
8. 点击"提交"或"创建"按钮
9. 你应该看到：页面显示一长串字符（就是 Token）
   - ⚠️ **Token 只显示这一次！关闭页面后无法再查看。请立即复制保存。**
   - 点击 Token 旁边的"复制"按钮，或手动选中全部文字按 Ctrl+C 复制

#### 第二步：在 CodeArtsWork 中填入 Token

1. 回到 CodeArtsWork 应用
2. 在左侧导航栏点击"连接器"
3. 在搜索框输入 `GitCode`，找到 GitCode 连接器卡片
4. 点击该卡片，打开详情对话框
5. 你应该看到：配置区域有两个输入框
   - `GITCODE_TOKEN`：将刚才复制的 Token 粘贴到这里（按 Ctrl+V）
   - `GITCODE_API_BASE_URL`：保持默认值 `https://api.gitcode.com/api/v5` 不用改
6. 点击"更新"按钮
7. 你应该看到：弹出"更新成功"提示

#### 修复后验证

1. 在连接器页面找到 GitCode 卡片
2. 如果开关是关闭的，点击开关打开
3. 等待 5-10 秒，观察状态指示灯：
   - 🟢 绿色 = 连接成功
   - 🔴 红色 = 仍然失败，点击"诊断"按钮，把新的错误信息发给我

---

### Figma 连接器

- **常见错误**：`FIGMA_API_KEY` 缺失或权限不足
- **错误类别**：`auth_failure` / `config_error`
- **可自动修复**：是（填写 API Key 到配置文件）
- **前提条件**：用户有 Figma 账号
- **配置字段**：`FIGMA_API_KEY`
- **配置指南 URL**：`https://www.figma.com/developers/api#access-tokens`

**面向用户的手动修复步骤：**

#### 第一步：获取 Figma API Key

1. 打开浏览器，在地址栏输入 `https://www.figma.com` 并按回车
2. 你应该看到：Figma 官网首页
3. 如果未登录，点击右上角"Log in"按钮，输入邮箱密码登录
   - 你应该看到：登录后页面右上角显示你的头像
4. 在地址栏输入 `https://www.figma.com/developers/api#access-tokens` 并按回车
   - 或者：点击右上角头像 → "Settings" → 在页面中找到"Personal access tokens"部分
5. 你应该看到：页面中有一个"Generate new token"或"Personal access tokens"区域
6. 在 Token 名称输入框中填写名称，如 `CodeArtsWork`
7. 点击"Generate token"按钮
8. 你应该看到：页面显示生成的 Token（一长串字符）
   - ⚠️ **Token 只显示一次，关闭页面后无法再查看。请立即复制保存。**
   - 选中 Token 文字，按 Ctrl+C 复制

#### 第二步：在 CodeArtsWork 中填入 API Key

1. 回到 CodeArtsWork 应用
2. 在左侧导航栏点击"连接器"
3. 在搜索框输入 `Figma`，找到 Figma 连接器卡片
4. 点击该卡片，打开详情对话框
5. 你应该看到：配置区域有一个 `FIGMA_API_KEY` 输入框
6. 将刚才复制的 Token 粘贴到 `FIGMA_API_KEY` 输入框中（按 Ctrl+V）
7. 点击"更新"按钮
8. 你应该看到：弹出"更新成功"提示

#### 修复后验证

1. 在连接器页面找到 Figma 卡片
2. 如果开关是关闭的，点击开关打开
3. 等待 5-10 秒，观察状态指示灯：
   - 🟢 绿色 = 连接成功
   - 🔴 红色 = 仍然失败，点击"诊断"按钮，把新的错误信息发给我

---

### Email Inbox 连接器

- **常见错误**：IMAP 参数配置错误、邮箱授权码未生成
- **错误类别**：`auth_failure` / `config_error`
- **可自动修复**：是（修正 IMAP 参数）
- **配置字段**：`IMAP_HOST`、`IMAP_PORT`、`IMAP_SECURE`、`EMAIL_USER`、`EMAIL_PASSWORD`

**面向用户的手动修复步骤：**

#### 第一步：开启邮箱 IMAP 服务并获取授权码

**QQ 邮箱：**
1. 打开浏览器，访问 `https://mail.qq.com`，登录 QQ 邮箱
2. 点击页面上方的"设置" → "账户"
3. 向下滚动找到"IMAP/SMTP 服务"部分
4. 点击"开启"按钮
5. 按提示用手机发送短信验证
6. 你应该看到：页面显示一串16位字符的授权码
   - ⚠️ **授权码只显示一次，请立即复制保存。** 授权码不是 QQ 密码！
7. IMAP 参数填写：
   - `IMAP_HOST`：`imap.qq.com`
   - `IMAP_PORT`：`993`
   - `IMAP_SECURE`：`true`
   - `EMAIL_USER`：你的完整 QQ 邮箱地址（如 `123456@qq.com`）
   - `EMAIL_PASSWORD`：刚才复制的授权码（不是 QQ 密码）

**163 邮箱：**
1. 打开浏览器，访问 `https://mail.163.com`，登录 163 邮箱
2. 点击页面上方的"设置" → "POP3/SMTP/IMAP"
3. 找到"IMAP/SMTP 服务"，点击"开启"
4. 按提示验证身份
5. 你应该看到：页面显示一串授权码
   - ⚠️ **授权码只显示一次，请立即复制保存。** 授权码不是邮箱密码！
6. IMAP 参数填写：
   - `IMAP_HOST`：`imap.163.com`
   - `IMAP_PORT`：`993`
   - `IMAP_SECURE`：`true`
   - `EMAIL_USER`：你的完整 163 邮箱地址（如 `yourname@163.com`）
   - `EMAIL_PASSWORD`：刚才复制的授权码

**Gmail：**
1. 打开浏览器，访问 `https://mail.google.com`，登录 Google 账号
2. 开启两步验证：访问 `https://myaccount.google.com/security`，确保"两步验证"已开启
3. 生成应用密码：访问 `https://myaccount.google.com/apppasswordons`
4. 在"应用名称"输入框中填写 `CodeArtsWork`，点击"创建"
5. 你应该看到：页面显示一串16位字符的应用密码
   - ⚠️ **应用密码只显示一次，请立即复制保存。**
6. IMAP 参数填写：
   - `IMAP_HOST`：`imap.gmail.com`
   - `IMAP_PORT`：`993`
   - `IMAP_SECURE`：`true`
   - `EMAIL_USER`：你的 Gmail 地址（如 `yourname@gmail.com`）
   - `EMAIL_PASSWORD`：刚才复制的应用密码

**Outlook / Office365：**
1. IMAP 参数填写：
   - `IMAP_HOST`：`outlook.office365.com`
   - `IMAP_PORT`：`993`
   - `IMAP_SECURE`：`true`
   - `EMAIL_USER`：你的 Outlook 邮箱地址
   - `EMAIL_PASSWORD`：你的邮箱密码（Outlook 使用普通密码即可，无需授权码）

#### 第二步：在 CodeArtsWork 中填入配置

1. 回到 CodeArtsWork 应用
2. 在左侧导航栏点击"连接器"
3. 在搜索框输入 `Email`，找到 Email Inbox 连接器卡片
4. 点击该卡片，打开详情对话框
5. 你应该看到：配置区域有 5 个输入框
6. 按照上面对应邮箱类型的参数，逐一填入：
   - `IMAP_HOST`：填入 IMAP 服务器地址
   - `IMAP_PORT`：填入 `993`
   - `IMAP_SECURE`：填入 `true`
   - `EMAIL_USER`：填入你的完整邮箱地址
   - `EMAIL_PASSWORD`：填入授权码或应用密码（不是邮箱登录密码）
7. 点击"更新"按钮
8. 你应该看到：弹出"更新成功"提示

#### 修复后验证

1. 在连接器页面找到 Email Inbox 卡片
2. 如果开关是关闭的，点击开关打开
3. 等待 5-10 秒，观察状态指示灯：
   - 🟢 绿色 = 连接成功
   - 🔴 红色 = 仍然失败，点击"诊断"按钮，把新的错误信息发给我

---

### Playwright 连接器

- **常见错误**：Node.js 未安装、Playwright 浏览器未安装
- **错误类别**：`environment_missing` / `process_crash`
- **可自动修复**：部分（可自动安装浏览器，不可自动安装 Node.js）
- **配置字段**：无（Playwright 无需配置项）
- **依赖**：Node.js ≥ 18

**面向用户的手动修复步骤：**

#### 第一步：安装 Node.js

如果错误信息中包含 `node`、`npx`、`ENOENT`、`command not found` 等关键词，说明 Node.js 未安装或未正确配置。

1. 按 [Node.js 安装指南](#nodejs-安装指南) 完整操作
2. 安装完成后重启 CodeArtsWork 应用

#### 第二步：安装 Playwright 浏览器（AI 可自动执行）

如果 Node.js 已安装但错误信息包含 `browser`、`executable`、`playwright install` 等关键词，说明浏览器未安装。

> 此步骤可以由 AI 自动执行，也可由用户手动操作：

**手动安装步骤：**
1. 按 `Win + R` 键，输入 `cmd`，按回车打开命令提示符
2. 输入以下命令并按回车：
   ```
   npx playwright install chromium
   ```
3. 你应该看到：开始下载浏览器，显示进度条
4. 等待下载完成（约 100-200MB，视网速可能需要几分钟）
5. 你应该看到：命令行显示"Chromium XXX installed"或类似成功信息
6. 关闭命令提示符

#### 修复后验证

1. 回到 CodeArtsWork 应用，在连接器页面找到 Playwright 卡片
2. 如果开关是关闭的，点击开关打开
3. 等待 10-15 秒（Playwright 首次启动较慢）
4. 观察状态指示灯：
   - 🟢 绿色 = 连接成功
   - 🔴 红色 = 仍然失败，点击"诊断"按钮，把新的错误信息发给我

---

### Chrome MCP 连接器

- **常见错误**：Chrome 扩展未安装或未启用
- **错误类别**：`environment_missing` / `process_crash`
- **可自动修复**：否（需用户在浏览器中手动安装扩展）
- **配置字段**：无（Chrome MCP 无需配置项）
- **配置指南 URL**：`https://chromewebstore.google.com/`

**面向用户的手动修复步骤：**

#### 第一步：安装 Chrome MCP 扩展

1. 打开 Chrome 浏览器
2. 在地址栏输入以下网址并按回车（Chrome MCP 扩展的 Chrome Web Store 页面）：
   - 先访问 `https://chromewebstore.google.com/`
   - 在搜索框中输入 `Chrome MCP` 搜索
   - 找到 Chrome MCP 扩展，点击进入详情页
3. 你应该看到：扩展详情页面，右上角有"添加到 Chrome"按钮
4. 点击"添加到 Chrome"按钮
5. 你应该看到：弹出确认对话框，点击"添加扩展程序"
6. 等待安装完成
7. 你应该看到：浏览器右上角扩展栏出现 Chrome MCP 图标

#### 第二步：确认扩展已启用

1. 点击 Chrome 右上角的"扩展程序"图标（拼图形状的图标）
2. 在列表中找到 Chrome MCP
3. 如果旁边有图钉图标，点击它将扩展固定到工具栏
4. 确认扩展开关是打开的（如果按钮是灰色的，点击它启用）

#### 修复后验证

1. 回到 CodeArtsWork 应用，在连接器页面找到 Chrome MCP 卡片
2. 如果开关是关闭的，点击开关打开
3. 等待 5-10 秒，观察状态指示灯：
   - 🟢 绿色 = 连接成功
   - 🔴 红色 = 仍然失败，确保 Chrome 浏览器已打开（不是 Edge 或 Firefox），再点击"诊断"按钮

---

### Computer Use 连接器

- **常见错误**：通常无需配置，故障率极低
- **错误类别**：通常为 `environment_missing`（Node.js 未安装）
- **可自动修复**：否（如果 Node.js 未安装，需用户手动安装）
- **配置字段**：无
- **依赖**：Node.js

**面向用户的手动修复步骤：**

如果 Computer Use 连接器显示失败，通常是 Node.js 环境问题：

1. 按 [Node.js 安装指南](#nodejs-安装指南) 检查并安装 Node.js
2. 安装后重启 CodeArtsWork 应用
3. 回到连接器页面，重新启用 Computer Use 连接器

如果安装 Node.js 后仍然失败：

1. 卸载 Computer Use 连接器（点击卡片 → 点击"卸载"）
2. 重新安装（点击卡片 → 点击"安装"）
3. 观察状态指示灯是否变绿

---

## 补充说明

### 如何判断用户使用的是哪种邮箱

在诊断 Email Inbox 连接器时，如果用户不确定邮箱类型，可以根据 `EMAIL_USER` 字段的域名判断：

| 邮箱域名 | 邮箱类型 | IMAP 主机 |
|---------|---------|-----------|
| `@qq.com` | QQ 邮箱 | `imap.qq.com` |
| `@163.com` | 163 邮箱 | `imap.163.com` |
| `@gmail.com` | Gmail | `imap.gmail.com` |
| `@outlook.com` / `@hotmail.com` / `@office365.com` | Outlook | `outlook.office365.com` |
| 其他 | 请用户提供邮箱服务商名称 | 根据服务商查询 IMAP 设置 |

### Token/授权码与密码的区别

在引导用户填写 Token 或授权码时，务必说明：

- **登录密码**：你登录邮箱/网站时输入的密码
- **授权码 / 应用密码**：邮箱服务商专门给第三方应用生成的密码，不是你的登录密码
- **Token / API Key**：在网站的开发者设置中生成的访问凭证

三者不能混用。CodeArtsWork 中需要填入的是授权码/应用密码/Token，不是登录密码。
