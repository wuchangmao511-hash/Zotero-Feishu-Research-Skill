# Research Paper Agent

Research Paper Agent 是一个面向研究生的本地论文阅读与知识管理工具。用户提供 Zotero 中的论文标题后，Agent 可通过 Zotero Local API 只读获取论文元数据和本地 PDF，阅读全文并生成结构化中文笔记，随后将笔记同步至飞书知识库，并通过 Zotero Key 在飞书 Paper Library 中创建或更新索引。

本项目坚持以下原则：

- Zotero 是论文元数据和附件的唯一主数据源。
- Zotero 全程只读，不读取或修改 `zotero.sqlite`。
- PDF 优先在本机处理，不上传到本仓库。
- 本地 Markdown 创建成功后，才允许写入飞书。
- Paper Library 使用 Zotero Key 去重。

## 工作流程

```text
论文标题
  → Zotero Local API 查询
  → 获取 metadata 和 PDF attachment
  → Zotero full-text / PyMuPDF fallback
  → 生成本地 Markdown 笔记
  → 创建飞书知识库文档
  → 创建或更新 Paper Library 记录
```

## 项目结构

```text
.
├── AGENTS.md                     # Agent 工作流、约束与笔记规范
├── README.md                     # 安装和使用说明
├── requirements.txt             # Python 依赖
├── research.config.example.json # 可公开的配置模板
├── scripts/
│   ├── zotero_local.py          # Zotero Local API 只读客户端
│   └── paper_extract.py         # PyMuPDF PDF 全文提取 fallback
├── notes/                        # 正式论文笔记
└── cache/                        # PDF 提取结果和临时文件
```

## 部署方式概览

本项目提供两种部署方法：

| 方法 | 适合用户 | 特点 |
|---|---|---|
| **方式一：Agent 辅助部署（推荐）** | 使用 Codex、Claude Code 等编码 Agent 的用户 | Agent 自动检查环境、安装依赖和执行 dry run；用户只需完成飞书授权并填写资源 URL |
| **方式二：PowerShell 手动部署** | 希望理解每个步骤，或需要独立排查环境问题的用户 | 按命令逐项安装、配置和验证 |

无论采用哪种方法，都必须满足以下安全边界：Zotero 只读；不读取 `zotero.sqlite`；不创建飞书测试垃圾数据；不向 GitHub 提交真实配置、论文 PDF、全文缓存或私人笔记。

## 部署方式一：Agent 辅助部署（推荐）

Agent 可以自动完成大部分初始化工作，包括环境检查、虚拟环境创建、Python 依赖安装、飞书 CLI 检查、本地目录创建、配置文件初始化以及只读 dry run。

仍需用户完成两项操作：

1. 在浏览器中完成飞书用户授权。
2. 提供自己的飞书 Wiki 父节点 URL 和 Paper Library URL。

### 步骤 1：下载项目

```powershell
git clone https://github.com/wuchangmao511-hash/Zotero-Feishu-Research-Skill.git
```

也可以在 GitHub 页面选择 **Code → Download ZIP** 并解压。

### 步骤 2：使用 Agent 打开项目

在 Codex 或其他编码 Agent 中打开：

```text
Zotero-Feishu-Research-Skill
```

确保 Agent 的当前工作目录中能够看到 `AGENTS.md`、`README.md`、`requirements.txt` 和 `scripts/`。

### 步骤 3：发送部署提示词

将下面的完整提示词发送给 Agent：

```text
请初始化并部署当前 Research Paper Agent 项目。

开始前完整阅读并严格遵循：
- AGENTS.md
- README.md
- research.config.example.json

请完成以下工作：

1. 检查 Git、Python、Node.js 和 npm 是否可用。
2. 创建项目虚拟环境 .venv，并在该环境中安装 requirements.txt。
3. 检查 PyMuPDF 是否能够通过 import fitz 正常导入。
4. 检查飞书官方 lark-cli；如果没有安装，则通过 npm 安装 @larksuite/cli。
5. 确保 notes/ 和 cache/ 存在。
6. 如果 research.config.json 不存在，则从 research.config.example.json 复制创建。
7. 检查 Zotero Local API：http://localhost:23119/api/。
8. 检查 lark-cli 当前登录状态。
9. 如果需要飞书用户授权，请暂停并提示我在浏览器中完成授权。
10. 如果配置中缺少 Wiki 父节点 URL 或 Paper Library URL，请明确告诉我需要填写的字段，不要自行猜测。
11. 配置完成后，只读检查飞书 Wiki、Paper Library、Papers 表及其字段。
12. 执行一次只读 dry run：Zotero 查询 → metadata → PDF attachment → full-text → 本地 PDF 路径。

限制：
- 不得修改 Zotero。
- 不得读取 zotero.sqlite。
- 不得创建飞书测试文档或测试记录。
- 不得把真实配置、PDF、缓存或私人笔记提交到 Git。

最后按以下格式报告：

Git: PASS / FAIL
Python: PASS / FAIL
PyMuPDF: PASS / FAIL
Zotero Local API: PASS / FAIL
lark-cli: PASS / FAIL
Feishu Login: PASS / FAIL
Feishu Wiki: PASS / FAIL
Paper Library: PASS / FAIL
Configuration: PASS / FAIL

对于 FAIL 项，说明具体原因和解决办法。
```

### 步骤 4：完成两个用户操作

如果 Agent 提示飞书未登录，按照提示完成浏览器授权。通常使用：

```powershell
lark-cli auth login --domain docs,wiki,base
```

如果 Agent 提示配置 URL 缺失，编辑 `research.config.json` 中的：

```json
{
  "feishu": {
    "wiki_parent_url": "你的飞书知识库父节点 URL",
    "paper_library_url": "你的飞书 Paper Library URL",
    "paper_table_name": "Papers"
  }
}
```

不要在配置文件中填写飞书密码、access token 或 App Secret。

### 步骤 5：确认部署报告

理想结果为所有检查项均为 `PASS`。如果只有 Feishu Login、Feishu Wiki 或 Paper Library 失败，按照 Agent 报告完成授权或修正 URL 后，让 Agent 重新检查失败项即可，不需要从头部署。

## 部署方式二：PowerShell 手动部署

以下流程适合希望逐步安装、不能使用编码 Agent，或需要定位环境问题的用户。

### 1. 系统要求

当前流程以 Windows PowerShell 为主要运行环境。安装前请准备：

- Windows 10 或 Windows 11
- [Git](https://git-scm.com/)
- Python 3.11 或更高版本
- Node.js 16 或更高版本（用于安装飞书官方 CLI）
- Zotero Desktop
- Codex 或其他能够遵循 `AGENTS.md` 的 Agent
- 可访问的飞书账号、知识库节点和多维表格

检查基础环境：

```powershell
git --version
python --version
node --version
npm --version
```

如果 `python` 指向错误版本，可以使用 Windows Python Launcher，例如：

```powershell
py -3.11 --version
```

### 2. 下载项目

```powershell
git clone https://github.com/wuchangmao511-hash/Zotero-Feishu-Research-Skill.git
Set-Location Zotero-Feishu-Research-Skill
```

也可以在 GitHub 页面选择 **Code → Download ZIP**，解压后在 PowerShell 中进入项目目录。

### 3. 创建 Python 虚拟环境

推荐为项目创建独立环境，避免电脑中的多个 Python 版本互相影响：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

如果 PowerShell 阻止激活脚本，可以仅为当前窗口临时放行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

激活成功后，命令行前通常会出现 `(.venv)`。

### 4. 安装 Python 依赖

```powershell
python -m pip install -r requirements.txt
```

当前唯一的外部 Python 依赖是 PyMuPDF。它在 Zotero 没有全文索引、索引不完整，或需要保留准确页码边界时读取本地 PDF。

验证安装：

```powershell
python -c "import fitz; print('PyMuPDF:', fitz.VersionBind)"
```

看到版本号即表示安装成功。PyMuPDF 的安装包名称是 `PyMuPDF`，但 Python 导入名称是 `fitz`。

### 5. 配置 Zotero Desktop

1. 安装并启动 Zotero Desktop。
2. 确保目标论文已保存为 Zotero 的 top-level bibliographic item。
3. 确保论文条目下存在 PDF attachment。
4. 保持 Zotero 在运行状态。
5. 如果 Zotero 设置中提供“允许本机其他应用与 Zotero 通信”选项，请确保它已启用；不同版本的选项名称可能略有差异。

本项目使用以下地址：

```text
http://localhost:23119/api/
```

检查 Local API：

```powershell
python scripts/zotero_local.py health
```

成功输出应包含：

```json
{
  "ok": true,
  "base_url": "http://localhost:23119/api/"
}
```

如果连接失败：

- 确认 Zotero Desktop 已启动。
- 退出并重新启动 Zotero。
- 确认 `localhost:23119` 没有被防火墙或其他程序拦截。
- 确认配置中的 URL 没有写成远程 Zotero Web API 地址。

### 6. 安装飞书官方 CLI

飞书 CLI 通过 npm 安装：

```powershell
npm install --global @larksuite/cli
```

验证安装：

```powershell
lark-cli --version
```

如果系统提示找不到 `lark-cli`：

1. 关闭并重新打开 PowerShell。
2. 执行 `npm config get prefix` 查看 npm 全局安装目录。
3. 确认该目录已加入用户的 `PATH` 环境变量。

### 7. 登录飞书

仅申请当前工作流需要的文档、知识库和多维表格权限：

```powershell
lark-cli auth login --domain docs,wiki,base
```

根据终端提示在浏览器中完成授权，然后检查登录状态：

```powershell
lark-cli auth status
```

正常情况下应看到 user identity 可用。Token 到期时，CLI 通常会在下一次用户 API 调用时自动刷新；刷新失败则重新执行登录命令。

### 8. 准备飞书资源

在飞书中准备以下资源：

1. 一个用于存放论文笔记的知识库父节点。
2. 一个多维表格 Base。
3. Base 中名为 `Papers` 的数据表。

Paper Library 推荐包含以下字段：

| 字段 | 推荐类型 | 用途 |
|---|---|---|
| 论文标题 | 文本 | Zotero 标题 |
| 作者 | 文本 | 作者列表 |
| 年份 | 数字 | 发表年份 |
| 期刊/会议 | 文本 | 正式来源 |
| 期刊分区 | 文本 | JCR Quartile；无法核实时填“未查询” |
| 中科院分区 | 文本 | 无法核实时填“未查询” |
| 分区年份 | 文本 | 分区对应年份 |
| 研究主题 | 多选 | 高层级研究方向 |
| 机器人类型 | 文本 | 机器人分类 |
| 建模方法 | 文本 | 主要建模方法 |
| 控制方法 | 文本 | 主要控制方法 |
| 应用场景 | 文本 | 主要应用 |
| Zotero标签 | 文本 | Zotero Tags |
| 阅读状态 | 单选 | 待读、在读、已读 |
| 一句话总结 | 文本 | 50–100 字核心总结 |
| 论文链接 | URL | DOI 或论文页面 |
| 飞书笔记 | URL | 详细阅读笔记 |
| 阅读日期 | 日期 | 完成阅读日期 |
| Zotero Key | 文本 | 唯一去重键 |

如果现有 Base 字段与上述规范不同，只报告差异，不要自动删除或重命名已有字段。

### 9. 创建本地配置

复制公开模板：

```powershell
Copy-Item research.config.example.json research.config.json
```

编辑 `research.config.json`：

```json
{
  "zotero": {
    "base_url": "http://localhost:23119/api",
    "user_id": 0
  },
  "feishu": {
    "wiki_parent_url": "YOUR_FEISHU_WIKI_OR_DOC_URL",
    "paper_library_url": "YOUR_FEISHU_BASE_URL",
    "paper_table_name": "Papers"
  },
  "local": {
    "notes_dir": "notes",
    "cache_dir": "cache"
  }
}
```

说明：

- `wiki_parent_url`：论文笔记父节点的飞书 URL。
- `paper_library_url`：Paper Library 的完整 URL，建议保留其中的 `table` 参数。
- `research.config.json` 包含私人资源地址，已通过 `.gitignore` 排除。
- 不要把飞书 token、App Secret 或登录缓存写进配置文件。

Wiki URL 中的 token 不一定是底层文档或 Base token。实际操作时应使用 `lark-cli wiki` 或 URL 解析能力取得真实对象，不能直接假设 URL token 就是目标对象 token。

### 10. 创建本地目录

```powershell
New-Item -ItemType Directory -Force notes, cache | Out-Null
```

- `notes/` 保存正式 Markdown 论文笔记。
- `cache/` 保存临时查询、PDF 提取和页面渲染结果。
- 私人笔记、PDF 和缓存默认不提交 Git。

### 11. 验证 Zotero 读取流程

搜索论文：

```powershell
python scripts/zotero_local.py search "论文标题、作者、DOI 或关键词"
```

得到 Zotero item key 后继续：

```powershell
python scripts/zotero_local.py item ITEM_KEY
python scripts/zotero_local.py children ITEM_KEY --pdf-only
```

得到 PDF attachment key 后：

```powershell
python scripts/zotero_local.py fulltext ATTACHMENT_KEY
python scripts/zotero_local.py file ATTACHMENT_KEY
```

检查 Collection：

```powershell
python scripts/zotero_local.py collections
```

上述命令全部只发出 HTTP GET 请求，不修改 Zotero。

### 12. 测试 PDF fallback

当 Zotero `fulltext` 不可用或内容不完整时，先用 `file` 命令取得真实 PDF 路径，再运行：

```powershell
python scripts/paper_extract.py "C:\path\to\paper.pdf" `
  --format markdown `
  --output "cache\paper-fulltext.md"
```

提取指定页码范围：

```powershell
python scripts/paper_extract.py "C:\path\to\paper.pdf" `
  --pages 3-8 `
  --format markdown `
  --output "cache\paper-pages-3-8.md"
```

输出文件使用 UTF-8，并以 `## Page N` 保留页码边界。扫描版 PDF 如果没有文字层，需要额外 OCR；PyMuPDF 本身不会自动完成 OCR。

### 13. 验证飞书访问

先检查身份和命令是否可用：

```powershell
lark-cli auth status
lark-cli wiki --help
lark-cli docs --help
lark-cli base --help
```

之后根据 `research.config.json` 中的 URL 做只读检查。不要为了验证连接而创建测试文档或垃圾记录。

### 14. 使用 Agent 阅读第一篇论文

在 Codex 中打开项目目录，并提交类似下面的任务：

```text
请严格按照当前项目的 AGENTS.md，阅读 Zotero 中的论文：

《论文标题》

使用 Zotero Local API 查询和读取 PDF，不修改 Zotero。
先在 notes/ 保存完整中文 Markdown 笔记；成功后在配置的飞书知识库父节点创建笔记，最后按 Zotero Key 创建或更新 Paper Library。
```

正确执行顺序必须是：

```text
Zotero 查询
→ PDF 全文读取
→ 本地 Markdown
→ 飞书知识库文档
→ Paper Library
```

任一步失败都应停止后续写入。例如飞书文档创建失败时，Paper Library 不应被标记为“已读”。

### 15. 安装完成检查表

完成以下检查即表示环境可以使用：

- [ ] `python --version` 可以运行。
- [ ] 虚拟环境已经激活。
- [ ] `import fitz` 成功并显示 PyMuPDF 版本。
- [ ] Zotero Desktop 正在运行。
- [ ] `zotero_local.py health` 返回成功。
- [ ] 能通过标题找到 top-level bibliographic item。
- [ ] 能找到 `application/pdf` attachment。
- [ ] 能取得 Zotero full-text 或通过 PyMuPDF 提取全文。
- [ ] `lark-cli --version` 可以运行。
- [ ] `lark-cli auth status` 显示 user identity 可用。
- [ ] Wiki 父节点具有读取和创建文档权限。
- [ ] Paper Library 具有读取、创建和更新记录权限。
- [ ] `research.config.json` 已配置且不会提交 Git。

## 常见错误

### 无法连接 Zotero Local API

启动或重启 Zotero，确认本地通信已启用，并检查 23119 端口。

### Zotero full-text 返回 404

PDF 可能尚未建立全文索引。使用 `file` 获取本地路径，然后通过 `paper_extract.py` 提取。

### 找不到 PDF attachment

确认 PDF 是目标 bibliographic item 的 child attachment，并检查 `contentType` 是否为 `application/pdf`。

### 找不到 PyMuPDF

```powershell
python -m pip install -r requirements.txt
python -c "import fitz; print(fitz.VersionBind)"
```

确保安装依赖和运行脚本时使用的是同一个 Python 或同一个虚拟环境。

### PowerShell 无法运行 lark-cli

如果提示脚本执行被禁用，可先在当前窗口执行：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
lark-cli --version
```

### 飞书登录状态失效

```powershell
lark-cli auth login --domain docs,wiki,base
lark-cli auth status
```

### Wiki 或 Base 无法访问

确认配置 URL 正确、当前飞书身份拥有权限，并先解析 Wiki/Base URL 对应的真实对象。不要凭 URL 中的 token 猜测底层对象类型。

## 隐私与安全

公开仓库中不得提交：

- `research.config.json`
- 飞书 token、App ID、App Secret 或登录缓存
- 私有 Wiki/Base URL
- Zotero 数据库文件
- 论文 PDF
- 论文全文缓存
- 私人阅读笔记
- 包含用户名的本地绝对路径

发布前建议运行：

```powershell
git status
git diff --cached
git grep -n -i -E "secret|token|authorization|app_secret"
```

如果敏感文件曾被 Git 跟踪，仅把它加入 `.gitignore` 不会从历史中删除；在公开仓库前应先清理 Git 历史并更换已泄露的凭证。

## License

建议代码使用 MIT License。论文 PDF、出版商图片和论文原文不属于本项目代码许可证的授权范围，因此不得随仓库分发。
