# FinQuery - 金融数据智能查询助手

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Flask-2.3+-green.svg" alt="Flask">
  <img src="https://img.shields.io/badge/AKShare-1.12+-orange.svg" alt="AKShare">
  <img src="https://img.shields.io/badge/DeepSeek-AI-purple.svg" alt="DeepSeek">
</div>

<br>

一个基于自然语言的金融数据查询助手，支持股票、指数等金融数据的智能查询和分析。

## ✨ 功能特点

- 🗣️ **自然语言查询** - 用日常语言查询金融数据，无需记忆复杂的 API
- 🤖 **智能问答** - 询问金融概念，获得专业解答
- 📊 **丰富数据源** - 基于 AKShare，支持 A 股、指数、基金等多种数据
- 💾 **数据导出** - 一键保存查询结果为 CSV 文件
- 🎨 **现代化界面** - 精美的 Web 界面，深色主题，响应式设计

## 🚀 快速开始

### 1. 环境要求

- Python 3.8+
- pip 包管理器

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

编辑 `src/.env` 文件，设置 DeepSeek API Key：

```
DEEPSEEK_API_KEY=your_api_key_here
```

### 4. 启动服务

**Linux / macOS:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

**手动启动:**
```bash
cd src
python ../backend/app.py
```

### 5. 访问 Web 界面

打开浏览器访问：http://localhost:5000

## 📖 使用示例

### 数据查询

```
获取上证指数最近10天的数据
查询贵州茅台最近7天股价
查询比亚迪的股票信息
获取国内成品油价格调整信息
```

### 知识问答

```
什么是市盈率？
如何分析一只股票？
K线图怎么看？
```

## 📁 项目结构

```
DBFP/
├── backend/           # 后端 API 服务
│   └── app.py         # Flask 应用主文件
├── frontend/          # 前端 Web 界面
│   └── index.html     # 主页面
├── src/               # 原始代码
│   ├── .env           # 环境变量配置
│   └── original version.py  # 命令行版本
├── data/              # 数据存储目录
├── rag/               # RAG 向量索引
├── requirements.txt   # Python 依赖
├── start.sh           # Linux/Mac 启动脚本
├── start.bat          # Windows 启动脚本
└── README.md          # 项目说明
```

## 🔧 API 接口

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/query` | POST | 执行自然语言查询 |
| `/api/save` | POST | 保存查询结果 |
| `/api/history` | GET | 获取历史记录 |
| `/api/download/<filename>` | GET | 下载历史文件 |

## 🤝 技术栈

- **后端**: Flask, Python
- **数据源**: AKShare
- **AI**: DeepSeek API
- **前端**: HTML5, CSS3, JavaScript
- **UI 设计**: 自定义深色主题

## 📝 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

- [AKShare](https://github.com/akfamily/akshare) - 开源金融数据接口
- [DeepSeek](https://www.deepseek.com/) - AI 语言模型
