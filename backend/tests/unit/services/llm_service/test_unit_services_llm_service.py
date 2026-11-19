"""單元測試：services.llm_service。"""
import json
from datetime import date

import pytest

import config
from services import llm_service as target

# conftest 會把 invoke_model patch 成 None stub；在匯入時保留真實函式以測試其本身
REAL_INVOKE_MODEL = target.invoke_model


class TestBuildPrompt:
    """對應原始碼函式 build_prompt。"""

    @pytest.mark.equivalence
    def test_build_prompt_replaces_placeholders(self):
        """等價類劃分: 日期與轉寫內容被帶入提示詞"""
        # Arrange
        transcript = "今天討論專案進度"
        # Act
        result = target.build_prompt(transcript, date(2024, 3, 5))
        # Assert
        assert "2024/03/05" in result
        assert transcript in result
        assert "{meeting_date}" not in result

    @pytest.mark.error_guessing
    def test_build_prompt_transcript_with_braces(self):
        """錯誤猜測: 轉寫內容含特殊字元仍原樣保留"""
        # Arrange
        transcript = "{x} %s <script>"
        # Act
        result = target.build_prompt(transcript, date(2024, 1, 1))
        # Assert
        assert transcript in result


class TestInvokeModel:
    """對應原始碼函式 invoke_model。"""

    @staticmethod
    def _fake_boto3(monkeypatch, response):
        calls = {}

        class FakeClient:
            def converse(self, **kwargs):
                calls["kwargs"] = kwargs
                return response

        class FakeSession:
            def __init__(self, **kwargs):
                calls["session"] = kwargs

            def client(self, name):
                calls["service"] = name
                return FakeClient()

        class FakeBoto3:
            Session = FakeSession

        monkeypatch.setattr(target, "boto3", FakeBoto3)
        return calls

    @pytest.mark.state_transition
    def test_invoke_model_joins_text_parts(self, monkeypatch):
        """狀態轉換: 設定齊全後呼叫 converse 並串接文字片段"""
        # Arrange
        monkeypatch.setattr(config, "require_llm_config", lambda: {
            "profile": "p", "region": "r", "model_id": "m"})
        response = {"output": {"message": {"content": [
            {"text": "ab"}, {"other": 1}, {"text": "cd"}]}}}
        calls = self._fake_boto3(monkeypatch, response)
        # Act
        result = REAL_INVOKE_MODEL("hello")
        # Assert
        assert result == "abcd"
        assert calls["service"] == "bedrock-runtime"
        assert calls["session"] == {"profile_name": "p", "region_name": "r"}
        assert calls["kwargs"]["modelId"] == "m"

    @pytest.mark.error_guessing
    def test_invoke_model_missing_config_raises(self, monkeypatch):
        """錯誤猜測: 缺少 LLM 設定時拋出例外"""
        # Arrange
        def boom():
            raise RuntimeError("missing")
        monkeypatch.setattr(config, "require_llm_config", boom)
        # Act / Assert
        with pytest.raises(RuntimeError):
            REAL_INVOKE_MODEL("hello")


class TestExtractJson:
    """對應原始碼函式 _extract_json。"""

    @pytest.mark.decision_table
    @pytest.mark.parametrize("text", [
        '{"a": 1}',
        '```json\n{"a": 1}\n```',
        '```\n{"a": 1}\n```',
        '前言 {"a": 1} 後記',
    ])
    def test_extract_json_formats(self, text):
        """決策表: 純 JSON、圍欄、無語言圍欄、前後文字皆可解析"""
        # Arrange / Act
        result = target._extract_json(text)
        # Assert
        assert result == {"a": 1}

    @pytest.mark.error_guessing
    @pytest.mark.parametrize("text, message", [
        ("沒有大括號", "不是 JSON"),
        ("} {", "不是 JSON"),
        ("{bad json}", "無法解析"),
        ("[1, 2]", "不是 JSON 物件"),
    ])
    def test_extract_json_invalid(self, text, message):
        """錯誤猜測: 無效輸出拋出 LLMError"""
        # Arrange / Act / Assert
        with pytest.raises(target.LLMError, match=message):
            target._extract_json(text)


class TestParseResult:
    """對應原始碼函式 parse_result。"""

    @pytest.mark.equivalence
    def test_parse_result_valid(self):
        """等價類劃分: 有效輸出被正規化"""
        # Arrange
        raw = json.dumps({"summary": "摘要", "attendees": [
            {"name": " 小明 ", "email": " a@b.c "},
            {"name": "小華", "email": None},
            {"name": "   "},
        ]})
        # Act
        result = target.parse_result(raw)
        # Assert
        assert result == {"summary": "摘要", "attendees": [
            {"name": "小明", "email": "a@b.c"},
            {"name": "小華", "email": ""},
        ]}

    @pytest.mark.boundary
    def test_parse_result_empty_attendees(self):
        """邊界值分析: attendees 為空清單時回傳空清單"""
        # Arrange
        raw = '{"summary": "x", "attendees": []}'
        # Act
        result = target.parse_result(raw)
        # Assert
        assert result["attendees"] == []

    @pytest.mark.error_guessing
    @pytest.mark.parametrize("raw", [
        None,
        123,
        '{"summary": "", "attendees": []}',
        '{"summary": "  ", "attendees": []}',
        '{"summary": 1, "attendees": []}',
        '{"summary": "x"}',
        '{"summary": "x", "attendees": "no"}',
        '{"summary": "x", "attendees": ["str"]}',
        '{"summary": "x", "attendees": [{"name": 1}]}',
        '{"summary": "x", "attendees": [{"name": "a", "email": 5}]}',
    ])
    def test_parse_result_invalid_raises(self, raw):
        """錯誤猜測: 非字串或欄位格式錯誤拋出 LLMError"""
        # Arrange / Act / Assert
        with pytest.raises(target.LLMError):
            target.parse_result(raw)


class TestGenerateMeetingMinute:
    """對應原始碼函式 generate_meeting_minute。"""

    @pytest.mark.state_transition
    def test_generate_meeting_minute_success(self, monkeypatch):
        """狀態轉換: 模型回傳有效 JSON 時得到正規化結果"""
        # Arrange
        monkeypatch.setattr(target, "invoke_model",
                            lambda prompt: '{"summary": "s", "attendees": []}')
        # Act
        result = target.generate_meeting_minute("內容", date(2024, 1, 2))
        # Assert
        assert result == {"summary": "s", "attendees": []}

    @pytest.mark.error_guessing
    def test_generate_meeting_minute_llm_error_passthrough(self, monkeypatch):
        """錯誤猜測: invoke_model 拋 LLMError 時原樣拋出"""
        # Arrange
        def raise_llm(prompt):
            raise target.LLMError("direct")
        monkeypatch.setattr(target, "invoke_model", raise_llm)
        # Act / Assert
        with pytest.raises(target.LLMError, match="direct"):
            target.generate_meeting_minute("x", date(2024, 1, 2))

    @pytest.mark.error_guessing
    def test_generate_meeting_minute_wraps_unexpected_exception(self, monkeypatch):
        """錯誤猜測: 其他例外被包成 LLMError 並保留原因"""
        # Arrange
        def raise_other(prompt):
            raise ValueError("boom")
        monkeypatch.setattr(target, "invoke_model", raise_other)
        # Act / Assert
        with pytest.raises(target.LLMError, match="呼叫失敗") as info:
            target.generate_meeting_minute("x", date(2024, 1, 2))
        assert isinstance(info.value.__cause__, ValueError)

    @pytest.mark.error_guessing
    def test_generate_meeting_minute_parse_failure(self, monkeypatch):
        """錯誤猜測: 模型輸出無法解析時拋出 LLMError"""
        # Arrange
        monkeypatch.setattr(target, "invoke_model", lambda prompt: "not json")
        # Act / Assert
        with pytest.raises(target.LLMError):
            target.generate_meeting_minute("x", date(2024, 1, 2))
