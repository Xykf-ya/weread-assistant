"""AI 调用服务：DeepSeek（文本） + qwen3.5-ocr（图片）"""

import asyncio
import json
import time
import re
from typing import Any

import dashscope
from openai import AsyncOpenAI

from app.config import settings
from app.services.prompts import (
    OPPORTUNITY_SYSTEM_PROMPT,
    CAMPUS_SYSTEM_PROMPT,
)

# DashScope MaaS 端点配置
if settings.dashscope_base_url:
    dashscope.base_http_api_url = settings.dashscope_base_url


# === 客户端 ===

def _get_deepseek_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.deepseek_api_key,
        base_url=settings.deepseek_base_url,
    )


# === 文本分类（DeepSeek）===

async def classify_article_text(
    title: str,
    content: str,
    task: str = "opportunity",  # "opportunity" 或 "campus"
    model: str = "deepseek-chat",
) -> dict[str, Any]:
    """用 DeepSeek 对文字文章进行分类和提取

    Args:
        title: 文章标题
        content: 文章正文（纯文本，前 2000 字即可）
        task: "opportunity" 或 "campus"
        model: DeepSeek 模型名

    Returns:
        解析后的 JSON dict
    """
    system_prompt = OPPORTUNITY_SYSTEM_PROMPT if task == "opportunity" else CAMPUS_SYSTEM_PROMPT

    # 截断内容，控制 token 消耗
    content_truncated = content[:2500] if content else ""

    user_message = f"标题: {title}\n\n正文:\n{content_truncated}"

    client = _get_deepseek_client()
    start_time = time.time()

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.1,
            max_tokens=800,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        return {
            "error": str(e),
            "is_opportunity": False if task == "opportunity" else None,
            "confidence": 0,
        }

    duration_ms = int((time.time() - start_time) * 1000)

    content_text = response.choices[0].message.content or "{}"
    tokens_in = response.usage.prompt_tokens if response.usage else 0
    tokens_out = response.usage.completion_tokens if response.usage else 0

    # 解析 JSON
    result = _parse_json_response(content_text)
    result["_meta"] = {
        "model": model,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "duration_ms": duration_ms,
    }

    return result


# === 图片 OCR + 分类（qwen3.5-ocr → DeepSeek）===

async def classify_article_image(
    title: str,
    image_urls: list[str],
    task: str = "opportunity",
    ocr_model: str = "qwen3.5-ocr",
    text_model: str = "deepseek-chat",
) -> dict[str, Any]:
    """两步处理图片文章：OCR 提取文字 → DeepSeek 分类

    Args:
        title: 文章标题
        image_urls: 图片 URL 列表
        task: "opportunity" 或 "campus"
        ocr_model: OCR 模型名
        text_model: 文本分类模型名

    Returns:
        解析后的 JSON dict
    """
    start_time = time.time()

    # Step 1: 用 qwen3.5-ocr 提取图片中的文字
    ocr_text = await _ocr_images(image_urls, model=ocr_model)
    if not ocr_text:
        duration_ms = int((time.time() - start_time) * 1000)
        return {
            "error": "OCR 未能提取到文字",
            "is_opportunity": False if task == "opportunity" else None,
            "confidence": 0,
            "_meta": {"model": ocr_model, "tokens_in": 0, "tokens_out": 0, "duration_ms": duration_ms},
        }

    # Step 2: 用 DeepSeek 对提取的文字做分类
    result = await classify_article_text(title, ocr_text, task=task, model=text_model)

    # 补充元信息
    result["_meta"]["model"] = f"ocr:{ocr_model}+text:{text_model}"
    result["_meta"]["duration_ms"] = int((time.time() - start_time) * 1000)

    return result


async def _ocr_images(image_urls: list[str], model: str = "qwen3.5-ocr") -> str:
    """调用 qwen3.5-ocr 从图片中提取文字

    Args:
        image_urls: 图片 URL 列表
        model: OCR 模型名

    Returns:
        提取到的全部文字（拼接为一个字符串）
    """
    # 构建多模态消息（DashScope 原生格式）
    content_parts: list[dict] = []
    for url in image_urls[:3]:  # 最多 3 张图
        content_parts.append({"image": url})
    content_parts.append({"text": "请仅输出图像中的文本内容。"})

    messages = [{"role": "user", "content": content_parts}]

    try:
        # dashscope SDK 是同步的，用线程池避免阻塞事件循环
        response = await asyncio.to_thread(
            dashscope.MultiModalConversation.call,
            api_key=settings.dashscope_api_key,
            model=model,
            messages=messages,
        )
    except Exception as e:
        # OCR 调用本身失败
        return "" if "OCR" in str(e) else ""

    # 解析响应：提取所有 text 片段
    if (response.output
            and response.output.choices
            and response.output.choices[0].message
            and response.output.choices[0].message.content):
        text_parts = []
        for item in response.output.choices[0].message.content:
            if isinstance(item, dict) and "text" in item:
                text_parts.append(item["text"])
        return "\n".join(text_parts)

    return ""


# === 统一分类入口 ===

async def classify_article(
    title: str,
    raw_content: str,
    is_image: bool,
    image_urls: list[str] | None = None,
    task: str = "opportunity",
) -> dict[str, Any]:
    """统一的文章分类入口，自动选择模型

    Args:
        title: 文章标题
        raw_content: 原始 HTML 内容
        is_image: 是否为图片文章
        image_urls: 图片 URL 列表（图片文章时需要）
        task: "opportunity" 或 "campus"

    Returns:
        分类结果 dict + _meta 元信息
    """
    if is_image and image_urls:
        return await classify_article_image(title, image_urls, task=task)
    else:
        # 提取纯文本
        from app.services.werss import strip_html
        text = strip_html(raw_content) if raw_content else ""
        return await classify_article_text(title, text, task=task)


# === JSON 解析 ===

def _parse_json_response(text: str) -> dict[str, Any]:
    """从 AI 返回的文本中提取 JSON"""
    if not text:
        return {}

    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 尝试提取 ```json ... ``` 代码块
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 尝试提取 { ... } 部分
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return {"raw_response": text, "parse_error": True}


# === 健康检查 ===

async def check_deepseek_health() -> bool:
    """检查 DeepSeek API 是否可用"""
    try:
        client = _get_deepseek_client()
        await client.models.list()
        return True
    except Exception:
        return False


async def check_dashscope_health() -> bool:
    """检查阿里云百炼 / MaaS API 是否可用（通过 qwen3.5-ocr 轻量调用测试）"""
    try:
        messages = [{"role": "user", "content": [{"text": "hi"}]}]
        response = await asyncio.to_thread(
            dashscope.MultiModalConversation.call,
            api_key=settings.dashscope_api_key,
            model="qwen3.5-ocr",
            messages=messages,
        )
        return response.output is not None and response.output.choices is not None
    except Exception:
        return False
