"""會議記錄彙整 Blueprint：只做 HTTP 解析與輸入驗證，業務邏輯在 services/。"""
import logging
import re
from datetime import datetime
from pathlib import PurePath

from flask import Blueprint, jsonify, request

import config
from services import llm_service

logger = logging.getLogger(__name__)

meeting_minute_bp = Blueprint("meeting_minute", __name__, url_prefix="/api/meeting-minute")

ALLOWED_EXTENSIONS = {".txt", ".md"}
_DATE_RE = re.compile(r"^(\d{8})$")


def _error(message: str, status: int):
    return jsonify({"error": message}), status


def _parse_date(stem: str):
    """檔名主檔名須為合法 YYYYMMDD，否則回傳 None。"""
    if not _DATE_RE.match(stem):
        return None
    try:
        return datetime.strptime(stem, "%Y%m%d").date()
    except ValueError:
        return None


@meeting_minute_bp.route("", methods=["POST"])
def create_meeting_minute():
    """上傳轉寫檔並回傳會議摘要與與會者。"""
    upload = request.files.get("file")
    if upload is None or not upload.filename:
        return _error("缺少檔案", 400)

    path = PurePath(upload.filename)
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return _error("僅接受 .txt 或 .md 檔案", 400)

    # 多讀 1 byte 以判斷是否超過上限，避免整個大檔進記憶體
    data = upload.stream.read(config.MAX_UPLOAD_BYTES + 1)
    if not data:
        return _error("檔案內容為空", 400)
    if len(data) > config.MAX_UPLOAD_BYTES:
        return _error("檔案超過大小上限", 400)

    try:
        transcript = data.decode("utf-8")
    except UnicodeDecodeError:
        return _error("檔案必須為 UTF-8 編碼", 400)
    if not transcript.strip():
        return _error("檔案內容為空", 400)

    meeting_date = _parse_date(path.stem)
    if meeting_date is None:
        return _error("檔名必須為 YYYYMMDD 格式", 400)

    try:
        result = llm_service.generate_meeting_minute(transcript, meeting_date)
    except llm_service.LLMError:
        return _error("會議記錄產生失敗，請稍後再試", 502)

    return jsonify(
        {
            "meeting_date": meeting_date.isoformat(),
            "summary": result["summary"],
            "attendees": result["attendees"],
        }
    ), 200
