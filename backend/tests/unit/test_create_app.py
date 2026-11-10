"""create_app() 啟動驗證測試。"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import pytest
import config
from app import create_app


def test_缺少必要環境變數時列出名稱(monkeypatch):
    for n in config.REQUIRED_VARS:
        monkeypatch.delenv(n, raising=False)
        monkeypatch.setattr(config, n, "")
    with pytest.raises(config.ConfigError) as e:
        create_app()
    assert "BEDROCK_REGION" in str(e.value) and "BEDROCK_MODEL_ID" in str(e.value)


def test_設定齊全時health回200(monkeypatch):
    monkeypatch.setattr(config, "BEDROCK_REGION", "ap-southeast-1")
    monkeypatch.setattr(config, "BEDROCK_MODEL_ID", "test-model")
    r = create_app().test_client().get("/api/health")
    assert r.status_code == 200
