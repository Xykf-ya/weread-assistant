"""应用配置，从环境变量加载"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # WeRSS 连接
    werss_base_url: str = "http://werss:8001"
    werss_username: str = "admin"
    werss_password: str = "admin@123"

    # AI — DeepSeek
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"

    # AI — 阿里云百炼 (qwen3.5-ocr)
    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/api/v1"

    # 同步频率（分钟）
    sync_interval_minutes: int = 360
    sync_interval_opportunity: int = 360
    sync_interval_campus: int = 360
    sync_interval_news: int = 720
    sync_interval_interest: int = 360

    # 飞书通知
    feishu_webhook_url: str = ""

    # 邮箱（可选）
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    notify_email: str = ""

    # 数据库
    database_url: str = "sqlite:////app/data/mp.db"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
