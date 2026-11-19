"""單元測試共用設定（flask-he 依範本產生）。

範本：ai-dev-tools/harness-engineering/flask-he/templates/unit_conftest.py.template
複製到【主】backend/tests/unit/conftest.py 後，並在同目錄建立空的 __init__.py（讓 pytest 以 unit.conftest 匯入，
不覆蓋根 conftest 的模組名 conftest；否則既有測試的 `from conftest import ...` 會失敗），
把下方常數**照 context.json 原樣填入**（範本刻意留空，不含任何專案的值；不要自行增刪鍵）：
- CONFIG_PATCHES   ← context.json 的 config_patches（設定檔 app.config_patches）
- CONFIG_OVERRIDES ← context.json 的 config_overrides（設定檔 app.config_overrides）
- EXTERNAL_STUBS   ← context.json 的 external_stubs.patch（設定檔 external_stubs.patch）
- TECHNIQUES       ← context.json 的 techniques（設定檔 techniques；下方為工具預設值，不一致時以 context.json 為準）

作用：
1. 註冊品質技術 marker（避免 PytestUnknownMarkWarning）。
2. 每個測試自動（autouse）把 CONFIG_PATCHES 列出的 config 屬性指到 tmp_path、套用 config_overrides，
   直接執行 `cd backend && pytest -q` 時也碰不到開發資料。
3. 每個測試自動把 EXTERNAL_STUBS 列出的外部服務入口 patch 成回傳 None，不會真的呼叫外部服務。

import config 需要 backend/ 在 sys.path 上：經 flask-he 工具執行時 test_env plugin 已加入；
直接執行 pytest 時由根 conftest 或專案的 pytest 設定負責。
CONFIG_PATCHES 與 CONFIG_OVERRIDES 都是空的時候不 import，專案可以沒有 config 模組。
"""
import os

import pytest

# ── 設定值（來源：專案的 flask-he 設定檔；照 context.json 填入）──────────────

# app.config_patches：{"屬性名": "tmp_file" | "tmp_dir"}
#   tmp_file → tmp_path 下的檔案；tmp_dir → tmp_path 下的目錄
CONFIG_PATCHES = {
    "UPLOAD_DIR": "tmp_dir",
}

# app.config_overrides：{"屬性名": 測試時固定的值}
CONFIG_OVERRIDES = {
    "SMTP_HOST": "localhost",
    "SMTP_PORT": 1025,
    "SMTP_USER": "",
    "SMTP_PASSWORD": "",
    "MAIL_FROM": "meeting-bot@example.com",
}

# external_stubs.patch：["模組.函式", ...]，測試時一律 patch 成回傳 None
EXTERNAL_STUBS = [
    "services.mail_service.send_mail",
    "services.llm_service.invoke_model",
    "services.ses_service.send_email",
]

# techniques：marker 與 docstring 前綴
TECHNIQUES = {
    "boundary": "邊界值分析",
    "equivalence": "等價類劃分",
    "decision_table": "決策表",
    "error_guessing": "錯誤猜測",
    "state_transition": "狀態轉換",
}


# ── marker 註冊 ─────────────────────────────────────────────────────

def pytest_configure(config):
    """註冊品質技術 marker。"""
    for marker, label in TECHNIQUES.items():
        config.addinivalue_line("markers", f"{marker}: {label}")


# ── 隔離 fixture ────────────────────────────────────────────────────

def _stub_none(*args, **kwargs):
    """外部服務 stub：一律回傳 None。"""
    return None


@pytest.fixture(autouse=True)
def flask_he_isolation(tmp_path, monkeypatch):
    """每個測試：config 指到 tmp_path、套用 config_overrides、patch 外部服務。"""
    if CONFIG_PATCHES or CONFIG_OVERRIDES:
        import config  # 只有要改寫屬性時才需要專案的 config 模組（名稱見 context.json 的 app.config_module）
    for name, kind in CONFIG_PATCHES.items():
        target = tmp_path / name.lower()
        if kind == "tmp_dir":
            target.mkdir(parents=True, exist_ok=True)
        else:  # tmp_file
            target = tmp_path / f"{name.lower()}.db"
        monkeypatch.setattr(config, name, os.fspath(target))
    for name, value in CONFIG_OVERRIDES.items():
        monkeypatch.setattr(config, name, value, raising=False)
    for dotted in EXTERNAL_STUBS:
        try:
            monkeypatch.setattr(dotted, _stub_none)
        except (ImportError, AttributeError):
            # 設定檔列出但專案尚未存在的入口（例：services.mail_service）：略過
            pass
    yield tmp_path
