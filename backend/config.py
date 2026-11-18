"""集中讀取環境變數。import 時只讀 os.environ，不建立任何連線或檔案。"""
import os
from pathlib import Path

from dotenv import load_dotenv

_BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(_BACKEND_DIR.parent / ".env")


def _int_env(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


# AWS / Bedrock（未設定時為 None，呼叫端須在使用時回明確錯誤）
AWS_PROFILE = os.environ.get("AWS_PROFILE") or None
BEDROCK_REGION = os.environ.get("BEDROCK_REGION") or None
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID") or None

# SES
SES_REGION = os.environ.get("SES_REGION") or "ap-southeast-1"
MAIL_FROM = os.environ.get("MAIL_FROM") or "sender@example.com"

# 上傳
MAX_UPLOAD_BYTES = _int_env("MAX_UPLOAD_BYTES", 1_048_576)
UPLOAD_DIR = str(_BACKEND_DIR / "uploads")
