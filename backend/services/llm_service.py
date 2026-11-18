"""LLM（Bedrock）服務：本專案唯一呼叫 Bedrock 的模組。

負責提示詞組裝、呼叫 converse 與解析 JSON 輸出。log 不記錄轉寫內容與個資。
"""
import json
import logging
import re
from datetime import date
from pathlib import Path

import boto3

import config

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "meeting_minute.md"


class LLMError(RuntimeError):
    """LLM 呼叫失敗或輸出無法解析。"""


def build_prompt(transcript: str, meeting_date: date) -> str:
    """讀取提示詞範本並帶入會議日期與轉寫內容。"""
    template = PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace(
        "{meeting_date}", meeting_date.strftime("%Y/%m/%d")
    ).replace("{transcript}", transcript)


def invoke_model(prompt: str) -> str:
    """以 Bedrock converse 呼叫模型，回傳文字輸出。外部服務唯一出口。"""
    cfg = config.require_llm_config()
    session = boto3.Session(profile_name=cfg["profile"], region_name=cfg["region"])
    client = session.client("bedrock-runtime")
    response = client.converse(
        modelId=cfg["model_id"],
        messages=[{"role": "user", "content": [{"text": prompt}]}],
        inferenceConfig={"maxTokens": 4096, "temperature": 0.2},
    )
    parts = response["output"]["message"]["content"]
    return "".join(p.get("text", "") for p in parts)


def _extract_json(text: str) -> dict:
    """從模型輸出取出 JSON 物件（容忍程式碼圍欄與前後文字）。"""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        data = json.loads(text)
    except ValueError:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise LLMError("LLM 輸出不是 JSON")
        try:
            data = json.loads(text[start : end + 1])
        except ValueError as exc:
            raise LLMError("LLM 輸出無法解析為 JSON") from exc
    if not isinstance(data, dict):
        raise LLMError("LLM 輸出不是 JSON 物件")
    return data


def parse_result(raw) -> dict:
    """驗證並正規化 LLM 輸出為 {summary, attendees}。"""
    if not isinstance(raw, str):
        raise LLMError("LLM 無輸出")
    data = _extract_json(raw)
    summary = data.get("summary")
    attendees = data.get("attendees")
    if not isinstance(summary, str) or not summary.strip():
        raise LLMError("summary 缺少或格式錯誤")
    if not isinstance(attendees, list):
        raise LLMError("attendees 缺少或格式錯誤")
    result = []
    for item in attendees:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            raise LLMError("attendees 項目格式錯誤")
        name = item["name"].strip()
        email = item.get("email") or ""
        if not isinstance(email, str):
            raise LLMError("attendees email 格式錯誤")
        if name:
            result.append({"name": name, "email": email.strip()})
    return {"summary": summary, "attendees": result}


def generate_meeting_minute(transcript: str, meeting_date: date) -> dict:
    """彙整會議記錄；任何失敗一律拋出 LLMError。"""
    prompt = build_prompt(transcript, meeting_date)
    try:
        raw = invoke_model(prompt)
    except LLMError:
        raise
    except Exception as exc:  # boto3 / 設定錯誤；不記錄內容，只記錄型別
        logger.error("LLM 呼叫失敗：%s", type(exc).__name__)
        raise LLMError("LLM 呼叫失敗") from exc
    try:
        return parse_result(raw)
    except LLMError:
        logger.error("LLM 輸出解析失敗")
        raise
