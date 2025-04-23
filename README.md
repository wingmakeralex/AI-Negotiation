# AI 谈判实验平台

这是一个基于 Flask 和 OpenAI API 的 Web 应用，用于进行 AI 谈判实验。用户可以输入他们的 Prolific ID，然后与 AI 进行对话。所有的对话记录都会被保存到数据库和日志文件中。

## 功能特点

- 用户认证：需要输入 Prolific ID 才能开始对话
- 对话记录：所有对话都会被保存到 SQLite 数据库
- 日志记录：对话内容同时保存到按日期分类的日志文件中
- 历史记录：可以查看之前的对话历史
- 响应式设计：适配不同设备的界面

## 技术栈

- 后端：Python Flask
- 数据库：SQLite
- 前端：HTML, CSS, JavaScript
- AI 接口：OpenAI API

## 安装步骤

1. 克隆项目：
```bash
git clone [你的仓库地址]
cd [项目目录]
```

2. 创建虚拟环境（推荐）：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

4. 配置环境变量：
创建 `.env` 文件并添加你的 OpenAI API 密钥：
```
OPENAI_API_KEY=你的API密钥
```

## 运行项目

1. 启动服务器：
```bash
python app.py
```

2. 在浏览器中访问：
```
http://localhost:5000
```

## 项目结构

```
.
├── app.py              # 主应用文件
├── database.py         # 数据库操作
├── requirements.txt    # 项目依赖
├── .env               # 环境变量
├── static/            # 静态文件
│   ├── css/          # 样式文件
│   └── js/           # JavaScript 文件
├── templates/         # HTML 模板
└── logs/             # 日志文件目录
```

## 数据存储

- 数据库文件：每次启动服务器会创建一个新的数据库文件，格式为 `chat_history_YYYYMMDD_HHMMSS.db`
- 日志文件：对话内容会按日期保存到 `logs/chat_log_YYYYMMDD.txt` 文件中

## 如何查看数据

1. 查看数据库：
   - 使用 DB Browser for SQLite 打开 `.db` 文件
   - 或使用 sqlite3 命令行工具

2. 查看日志：
   - 直接打开 `logs` 目录下的 `.txt` 文件
   - 日志格式：`[时间戳] Prolific ID: ID号 | 角色: 消息内容`

## 注意事项

- 确保有有效的 OpenAI API 密钥
- 每次启动服务器都会创建新的数据库文件
- 日志文件按日期自动分类
- 建议定期备份数据库和日志文件

## 许可证

MIT License 