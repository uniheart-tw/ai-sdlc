"""集中讀取環境變數。機密與帳號一律來自環境變數（本機 .env），程式碼不內嵌預設機密。"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR.parent / ".env")


class ConfigError(RuntimeError):
    """必要的環境變數未設定。"""


def _get(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    return value if value else default


def require(name: str) -> str:
    """取得必要的環境變數；未設定時拋出明確的 ConfigError。"""
    value = _get(name)
    if value is None:
        raise ConfigError(f"環境變數 {name} 未設定，請參考 .env.example 設定")
    return value


# 會議紀錄上傳目錄
UPLOAD_DIR = BASE_DIR / "uploads"

# 非機密、可有預設值
AWS_REGION = _get("AWS_REGION", "ap-southeast-1")
MAX_UPLOAD_BYTES = int(_get("MAX_UPLOAD_BYTES", str(1024 * 1024)))

# 無預設值；使用 LLM / SES 時才檢查（呼叫 require_llm_config / require_ses_config）
AWS_PROFILE = _get("AWS_PROFILE")
LLM_MODEL_ID = _get("LLM_MODEL_ID")
SES_SENDER = _get("SES_SENDER")


def require_llm_config() -> dict:
    """使用 Bedrock LLM 前呼叫；缺少設定時拋出 ConfigError。"""
    return {
        "profile": require("AWS_PROFILE"),
        "region": require("AWS_REGION"),
        "model_id": require("LLM_MODEL_ID"),
    }


def require_ses_config() -> dict:
    """使用 SES 寄信前呼叫；缺少設定時拋出 ConfigError。"""
    return {
        "profile": require("AWS_PROFILE"),
        "region": require("AWS_REGION"),
        "sender": require("SES_SENDER"),
    }
