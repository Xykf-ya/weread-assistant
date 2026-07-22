# mp-assistant 项目规范

## 项目概述

公众号信息助手。从 [WeRSS](https://github.com/rachelos/we-mp-rss) 获取公众号文章，使用 AI 识别招聘/比赛/活动机会，通过飞书推送提醒，并提供电脑端阅读看板。

## 技术栈

- 文章抓取：WeRSS (Docker, 端口 8001)
- 后端：Python 3.13 + FastAPI (端口 8000)
- 数据库：SQLite（文件位于 `backend/data/mp.db`）
- ORM：SQLAlchemy 2.0
- AI：DeepSeek API（文本） + 通义千问 VL（图片）
- 定时任务：APScheduler
- 通知：飞书群机器人 Webhook
- 前端：Jinja2 模板 + htmx

## 目录约定

```
mp-assistant/
├── CLAUDE.md              # 本文件
├── docker-compose.yml     # WeRSS + mp-assistant 容器编排
├── .env.example           # 环境变量模板
├── .gitignore
├── backend/               # 所有后端代码
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py        # FastAPI 入口
│   │   ├── config.py      # 环境变量配置
│   │   ├── database.py    # SQLAlchemy 引擎
│   │   ├── models.py      # 数据模型
│   │   ├── schemas.py     # Pydantic schemas
│   │   ├── routers/       # API 路由
│   │   ├── services/      # 业务逻辑
│   │   └── templates/     # Jinja2 模板
│   └── data/              # SQLite 数据库（卷挂载，不进 git）
├── scripts/               # 工具脚本
└── docs/                  # 文档
```

## 命名约定

- Python 文件：snake_case
- Python 类：PascalCase
- 数据库表名：snake_case
- API 路径：kebab-case（如 `/api/opportunities`）
- 变量名、函数名：英文
- 注释、文档、UI 文案：中文

## 编码规范

- FastAPI 路由使用 `APIRouter`，在 main.py 中统一注册
- 数据库操作通过 SQLAlchemy session，不在路由函数中直接执行 SQL
- 所有外部 API 调用（WeRSS、DeepSeek、Qwen-VL、飞书）放在 services/ 下
- 环境变量通过 pydantic-settings 的 `Settings` 类统一管理
- AI 调用需要日志记录（存 AiProcessLog 表）
- 错误处理：API 调用失败重试 3 次，指数退避

## 验证命令

```bash
# 启动服务
docker compose up -d

# 查看日志
docker compose logs -f assistant

# 手动触发同步
curl -X POST http://localhost:8000/api/sync

# 检查健康状态
curl http://localhost:8000/api/health

# 重启服务
docker compose restart assistant
```

## 安全

- `.env` 不进 git
- `backend/data/` 不进 git（含数据库文件）
- API Key 通过环境变量注入，不硬编码
