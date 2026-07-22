# 公众号信息助手 — API 文档

## 基本信息

- **后端地址**：`http://localhost:8000`
- **数据格式**：JSON（请求和响应都是 JSON）
- **跨域**：已开放 CORS，任何本地前端都可以调用
- **无需登录**：本地使用，没有鉴权

## 通用响应格式

```json
{
  "code": 0,
  "message": "ok",
  "data": { ... }
}
```

`code=0` 表示成功。

---

## API 列表

### 1. 健康检查

```
GET /api/health
```

返回示例：
```json
{
  "status": "ok",
  "werss": "ok",
  "deepseek": "auth_error",
  "dashscope": "ok",
  "feishu": "configured"
}
```

---

### 2. 公众号管理

#### 获取所有公众号

```
GET /api/accounts
```

可选参数：`?account_type=opportunity&is_active=true`

返回示例：
```json
[
  {
    "id": 1,
    "werss_mp_id": "mp_abc123",
    "mp_name": "浙江大学就业指导中心",
    "cover_url": "https://...",
    "account_type": "opportunity",
    "tags": "[\"浙大\",\"就业\"]",
    "is_active": true,
    "created_at": "2026-07-22T10:00:00"
  }
]
```

`account_type` 可选值：`opportunity`（机会类）、`campus`（校园类）、`news`（新闻类）、`interest`（兴趣类）

#### 添加公众号

```
POST /api/accounts
Content-Type: application/json

{
  "werss_mp_id": "mp_abc123",
  "mp_name": "浙江大学就业指导中心",
  "cover_url": "https://...",
  "account_type": "opportunity",
  "tags": "[\"浙大\",\"就业\"]"
}
```

#### 更新公众号

```
PUT /api/accounts/{id}
Content-Type: application/json

{
  "account_type": "campus",
  "tags": "[\"浙大\",\"活动\"]"
}
```

只传需要修改的字段即可。

#### 停用公众号

```
DELETE /api/accounts/{id}
```

---

### 3. 文章

#### 获取文章列表

```
GET /api/articles?account_type=opportunity&limit=50&offset=0
```

参数：
- `account_type`：按公众号类型筛选（可选）
- `werss_mp_id`：按具体公众号筛选（可选）
- `limit`：每页数量，默认 50
- `offset`：偏移量，默认 0

返回示例：
```json
[
  {
    "id": 1,
    "werss_article_id": "art_xyz",
    "werss_mp_id": "mp_abc123",
    "title": "腾讯2026校园招聘正式启动",
    "author": "腾讯招聘",
    "summary": "腾讯2026届校园招聘全面启动...",
    "cover_url": "https://...",
    "original_url": "https://mp.weixin.qq.com/s/...",
    "published_at": "2026-07-21T10:30:00",
    "fetched_at": "2026-07-22T08:00:00",
    "ai_processed": true
  }
]
```

#### 获取文章详情

```
GET /api/articles/{id}
```

返回比列表多一个 `raw_content` 字段（HTML 正文）。

#### 更新阅读状态

```
PUT /api/articles/{id}/reading-state
Content-Type: application/json

{
  "is_read": true,
  "is_favorite": false,
  "notes": ""
}
```

三个字段都是可选的，只传需要修改的。

---

### 4. 机会信息（P0 核心）

#### 获取机会列表

```
GET /api/opportunities?opp_type=internship&min_confidence=0.7&upcoming_only=false&limit=50&offset=0
```

参数：
- `opp_type`：机会类型筛选（可选）
  - `job` — 招聘
  - `internship` — 实习
  - `competition` — 比赛
  - `camp` — 训练营/夏校
  - `volunteer` — 志愿活动
  - `registration` — 报名/招募
  - `other` — 其他
- `min_confidence`：最低置信度，默认 0.7
- `upcoming_only`：只显示截止日期未过期的，默认 false

返回示例：
```json
[
  {
    "id": 1,
    "article_id": 5,
    "is_opportunity": true,
    "confidence": 0.95,
    "opp_type": "internship",
    "opp_name": "腾讯2026校园招聘",
    "deadline": "2026-09-15",
    "deadline_display": "2026年9月15日截止",
    "target_audience": "2026届本科及以上",
    "requirements": "招聘软件开发、产品经理等多个岗位",
    "notified": true,
    "processed_at": "2026-07-22T09:00:00",
    "title": "腾讯2026校园招聘正式启动",
    "mp_name": "腾讯招聘",
    "original_url": "https://mp.weixin.qq.com/s/...",
    "published_at": "2026-07-21T10:30:00"
  }
]
```

#### 获取即将截止的机会

```
GET /api/opportunities/upcoming?days=7
```

`days`：未来几天内截止，默认 7 天。

返回示例：
```json
[
  {
    "id": 1,
    "opp_name": "字节跳动前端实习",
    "opp_type": "internship",
    "deadline": "2026-07-25",
    "days_left": 3,
    "mp_name": "字节跳动招聘",
    "original_url": "https://..."
  }
]
```

#### 人工修正 AI 结果

```
PUT /api/opportunities/{id}
Content-Type: application/json

{
  "opp_name": "修改后的名称",
  "deadline": "2026-10-01",
  "opp_type": "job"
}
```

---

### 5. 校园信息（P1）

```
GET /api/campus?event_type=lecture&organizer=计算机&limit=50&offset=0
```

参数：
- `event_type`：活动类型（可选）
  - `event` — 活动
  - `lecture` — 讲座/论坛
  - `competition` — 比赛/征集
  - `volunteer` — 志愿活动
  - `internship` — 实习/招聘
  - `notice` — 通知公告
- `organizer`：主办方搜索（可选，模糊匹配）

返回示例：
```json
[
  {
    "id": 1,
    "article_id": 10,
    "event_type": "lecture",
    "event_date": "2026-08-01",
    "location": "紫金港校区蒙民伟楼",
    "organizer": "计算机学院",
    "deadline": "2026-07-30",
    "processed_at": "2026-07-22T09:00:00",
    "title": "AI前沿技术讲座",
    "mp_name": "浙大计算机",
    "original_url": "https://...",
    "published_at": "2026-07-21T15:00:00"
  }
]
```

---

### 6. 同步操作

#### 手动触发同步 + AI 处理

```
POST /api/sync
```

这是最核心的操作——从 WeRSS 拉取新文章 → AI 分类识别 → 发送飞书通知，全部一步完成。

返回示例：
```json
{
  "total_fetched": 25,
  "new_articles": 5,
  "ai_processed": 5,
  "alerts_sent": 2,
  "errors": []
}
```

字段说明：
- `total_fetched`：从 WeRSS 拉取的文章总数
- `new_articles`：新入库的文章数
- `ai_processed`：AI 处理成功的文章数
- `alerts_sent`：发送的飞书通知数
- `errors`：错误信息列表

---

### 7. 通知测试

```
POST /api/alerts/test
```

发送一条飞书测试消息。

---

## 前端页面建议

如果你想自己做几个页面来替换我那个简陋的看板，建议做这些页面：

| 页面 | 路由 | 用到的 API |
|------|------|-----------|
| 首页/机会看板 | `/` | `GET /api/opportunities` + `POST /api/sync` |
| 校园信息 | `/campus` | `GET /api/campus` |
| 新闻阅读 | `/reading/news` | `GET /api/articles?account_type=news` |
| 兴趣必读 | `/reading/interest` | `GET /api/articles?account_type=interest` + `PUT /api/articles/{id}/reading-state` |
| 设置/管理 | `/settings` | `GET/POST/PUT/DELETE /api/accounts` |

不需要 new 路由——你前端做好了，直接用这些 API 就行，后端不用改。

---

## 给 AI 工具的提示

把这个文档发给 Tree Code / Kimi / v0 / Claude 等任何前端工具，加上这句话：

> 帮我做一个公众号信息助手的 Web 前端，后端已经在 localhost:8000 运行，API 文档如上。
> 要求：
> - 纯前端项目（HTML/JS 或 React/Vue 都可以）
> - 本地运行在另一个端口
> - 美观现代的设计风格
> - 响应式布局，适合桌面端使用
> - 飞书风格的配色（蓝色系）
> - 包含以下页面：机会看板首页、校园信息页、新闻阅读页、兴趣必读页（含已读/收藏功能）、设置页（管理公众号）
