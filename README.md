# 📬 公众号信息助手

一个面向个人的微信公众号信息聚合与机会提醒工具。

## 产品定位

从大量关注的公众号中，找出不能错过的招聘、比赛、活动、报名信息，并通过飞书推送提醒。

核心解决两个问题：
1. 低频但重要的机会信息容易被淹没——错过一条招聘可能要等一年
2. 公众号分散在不同地方，需要逐个点开检查——集中到电脑端统一浏览

## 功能规划

| 阶段 | 功能 | 状态 |
|------|------|------|
| **P0** | 机会提醒：AI 识别招聘/实习/比赛/夏校/志愿招募，提取截止日期，飞书推送 | 🚧 开发中 |
| **P1** | 校园信息聚合：学校/学院/社团的活动、讲座、通知集中看板 | 📋 计划中 |
| **P2** | 阅读看板：新闻标题浏览 + 兴趣文章必读清单（已读/收藏） | 📋 计划中 |

## 公众号分类

| 类型 | AI 处理 | 展示方式 |
|------|---------|---------|
| **机会类** | ✅ DeepSeek 识别 + 提取截止日期 | 飞书推送 + 看板 |
| **校园类** | ✅ AI 分类活动类型 | 校园信息看板 |
| **新闻类** | ❌ | 标题列表，点击跳原文 |
| **兴趣类** | ❌ | 标题列表 + 已读/未读标记 |

## 技术架构

```
┌─────────────────────────────────────────────────┐
│            Docker Desktop (本地运行)              │
│                                                  │
│  ┌──────────────────┐  ┌──────────────────────┐ │
│  │  WeRSS (8001)    │  │  mp-assistant (8000) │ │
│  │  公众号抓取       │  │  FastAPI 后端        │ │
│  │  RSS / REST API   │──│  AI 分类 · 通知      │ │
│  │  SQLite           │  │  SQLite              │ │
│  └──────────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────┘
         │                        │
         ▼                        ▼
    微信公众号平台          飞书 Webhook
                         Claude / AI 工具
```

- **文章抓取**：[WeRSS (we-mp-rss)](https://github.com/rachelos/we-mp-rss) — 开源微信公众号 RSS 订阅工具
- **后端**：Python 3.13 + FastAPI + SQLAlchemy + SQLite
- **AI 文字分类**：DeepSeek API
- **AI 图片 OCR**：通义千问 qwen3.5-ocr（处理公众号长图文章）
- **通知推送**：飞书群机器人 Webhook
- **定时任务**：APScheduler（可配置频率，按公众号类型差异化）
- **部署**：Docker Compose 本地运行

## 项目结构

```
mp-assistant/
├── CLAUDE.md                    # 项目规范
├── README.md                    # 本文件
├── docker-compose.yml           # 容器编排
├── .env.example                 # 环境变量模板
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI 入口
│       ├── config.py            # 环境变量配置
│       ├── database.py          # SQLAlchemy 引擎
│       ├── models.py            # 数据模型（6 张表）
│       ├── schemas.py           # Pydantic 请求/响应模型
│       ├── routers/             # API 路由
│       │   ├── sync.py          # 同步 + AI 处理流水线
│       │   ├── accounts.py      # 公众号 CRUD
│       │   ├── articles.py      # 文章列表 + 详情
│       │   ├── opportunities.py # 机会识别结果
│       │   ├── campus.py        # 校园信息
│       │   ├── reading.py       # 阅读状态管理
│       │   └── alerts.py        # 健康检查 + 通知测试
│       └── services/            # 业务逻辑
│           ├── werss.py         # WeRSS API 客户端
│           ├── ai.py            # DeepSeek + qwen3.5-ocr
│           ├── prompts.py       # AI Prompt 模板
│           ├── notifier.py      # 飞书消息卡片
│           └── scheduler.py     # APScheduler 定时任务
│
├── docs/
│   └── API文档.md               # 前端对接接口文档
│
└── frontend/                    # 前端项目（独立开发）
```

## 数据库设计

6 张表：

| 表名 | 说明 |
|------|------|
| `monitored_account` | 监控的公众号（类型、标签） |
| `article` | 从 WeRSS 同步的文章 |
| `opportunity` | AI 提取的机会信息（招聘/比赛/实习等） |
| `campus_info` | AI 提取的校园活动信息 |
| `reading_state` | 已读/未读/收藏状态 |
| `alert_log` | 飞书通知发送记录 |

## 快速开始

### 前提

- Windows 10/11 + Docker Desktop
- DeepSeek API Key
- 阿里云百炼 API Key（用于图片文章 OCR）
- 一个微信公众号（用于 WeRSS 授权）

### 安装运行

```bash
# 1. 克隆仓库
git clone https://github.com/<your-username>/mp-assistant.git
cd mp-assistant

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 API Key

# 3. 启动
docker compose up -d

# 4. 访问
# 后端 API: http://localhost:8000
# API 文档: http://localhost:8000/docs
# WeRSS 管理: http://localhost:8001
```

### 配置 WeRSS

1. 打开 `http://localhost:8001`，账号 `admin` / 密码 `admin@123`
2. 用微信公众号管理员微信扫码授权
3. 搜索并订阅想要监控的公众号

### 添加监控

调用 API 注册公众号：

```bash
curl -X POST http://localhost:8000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "werss_mp_id": "公众号在WeRSS中的ID",
    "mp_name": "公众号名称",
    "account_type": "opportunity"
  }'
```

或使用前端页面操作。

### 手动触发同步

```bash
curl -X POST http://localhost:8000/api/sync
```

### 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `WERSS_BASE_URL` | WeRSS 地址 | `http://werss:8001` |
| `DEEPSEEK_API_KEY` | DeepSeek API Key | — |
| `DASHSCOPE_API_KEY` | 阿里云百炼 API Key | — |
| `FEISHU_WEBHOOK_URL` | 飞书机器人 Webhook URL | — |
| `SYNC_INTERVAL_MINUTES` | 默认同步间隔（分钟） | 360 |

## AI 成本

| 模型 | 用途 | 月成本估算 |
|------|------|-----------|
| DeepSeek-V3 | 文字文章分类 | ~¥0.11 |
| qwen3.5-ocr | 图片文章 OCR | ~¥0.90 |
| **合计** | | **~¥1/月** |

## 相关项目

- [WeRSS (we-mp-rss)](https://github.com/rachelos/we-mp-rss) — 微信公众号 RSS 订阅工具
