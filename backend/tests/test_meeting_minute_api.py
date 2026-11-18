"""POST /api/meeting-minute 測試：LLM 以 stub 取代，不呼叫真實 Bedrock。"""
import io
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import create_app  # noqa: E402

DATA = Path(__file__).parent / "data"
STUB = "services.llm_service.invoke_model"
GOOD = (DATA / "llm_response.json").read_text(encoding="utf-8")


@pytest.fixture
def cli():
    return create_app().test_client()


def post(cli, content: bytes, name="20261118.txt"):
    return cli.post(
        "/api/meeting-minute",
        data={"file": (io.BytesIO(content), name)},
        content_type="multipart/form-data",
    )


def test_health(cli):
    assert cli.get("/api/health").status_code == 200


def test_200(cli):
    with patch(STUB, return_value=GOOD) as m:
        r = post(cli, (DATA / "20261118.txt").read_bytes())
    assert r.status_code == 200
    body = r.get_json()
    assert body["meeting_date"] == "2026-11-18"
    assert body["attendees"][1] == {"name": "李小華", "email": ""}
    assert "2026/11/18" in m.call_args[0][0]


def test_200_fenced_json_md(cli):
    with patch(STUB, return_value=f"```json\n{GOOD}\n```"):
        r = post(cli, "內容".encode(), "20261118.md")
    assert r.status_code == 200


def test_missing_file(cli):
    r = cli.post("/api/meeting-minute", data={}, content_type="multipart/form-data")
    assert (r.status_code, r.get_json()) == (400, {"error": "缺少檔案"})


@pytest.mark.parametrize(
    "content,name,msg",
    [
        (b"x", "20261118.pdf", "僅接受 .txt 或 .md 檔案"),
        (b"", "20261118.txt", "檔案內容為空"),
        (b"\xff\xfe\x00", "20261118.txt", "檔案必須為 UTF-8 編碼"),
        (b"x", "meeting.txt", "檔名必須為 YYYYMMDD 格式"),
        (b"x", "20261399.txt", "檔名必須為 YYYYMMDD 格式"),
    ],
)
def test_400(cli, content, name, msg):
    with patch(STUB) as m:
        r = post(cli, content, name)
    assert r.status_code == 400
    assert r.get_json() == {"error": msg}
    m.assert_not_called()


def test_too_large(cli):
    with patch("config.MAX_UPLOAD_BYTES", 10), patch(STUB) as m:
        r = post(cli, b"a" * 11)
    assert (r.status_code, r.get_json()) == (400, {"error": "檔案超過大小上限"})
    m.assert_not_called()


@pytest.mark.parametrize(
    "effect",
    [
        {"side_effect": RuntimeError("boom")},
        {"return_value": "不是 JSON"},
        {"return_value": '{"summary": "x"}'},
        {"return_value": '{"summary": "", "attendees": []}'},
    ],
)
def test_502(cli, effect):
    with patch(STUB, **effect):
        r = post(cli, b"x")
    assert r.status_code == 502
    assert r.get_json() == {"error": "會議記錄產生失敗，請稍後再試"}
