# Flask 整合測試報告

**測試類型**: integration（flask_function_wrapper.py 於行程內執行 requests/*.json）  
**測試日期**: 2026-11-18  
**測試結果**: ✅ 6 passed, ❌ 0 failed, ⚠️ 0 error（共 6 個請求；1 個資源）  
**執行指令**: `/Users/yehchitsai/2023_uniheart_startups/uniheart-works/ai-sdlc/.venv/bin/python ai-dev-tools/scripts/flask/generate_test_report.py meeting-minute --kind integration --with-report --fail-on-error --config /Users/yehchitsai/2023_uniheart_startups/uniheart-works/ai-sdlc/backend/flask-he-config.yaml`
**本次對象**: `meeting-minute`（6 個請求）

**測試環境**

| 項目 | 版本/設定 |
|------|----------|
| Python | 3.13.18 |
| flask | 3.0.3 |
| pytest | 8.3.3 |
| pytest-cov | 7.0.0 |
| coverage | 7.13.4 |
| 測試 DB | /tmp/flask-he/ai-sdlc/session/tests.db |

---

## 一、測試摘要

> 資源: 1 個 | 請求: 6 個

| # | 資源 | 端點數 | 請求檔數 | 通過 | 失敗 | 覆蓋率 | 結果 |
|---|------|--------|---------|------|------|--------|------|
| 1 | `meeting-minute` | 1 | 6 | 6 | 0 | 85% | ✅ |

### 測試品質技術統計

| 技術 | 請求數 |
|------|-----------|
| 邊界值分析 | 1 |
| 等價類劃分 | 1 |
| 決策表 | 1 |
| 錯誤猜測 | 2 |
| 狀態轉換 | 1 |
| **合計** | **6** |

---

## 二、測試品質技術應用詳細說明

### 2.1 邊界值分析 (Boundary Value Analysis)

**應用數量**: 1 個請求檔  

| # | 資源 | 請求檔 | 說明 | 結果 |
|---|------|----------|------|------|
| 1 | `meeting-minute` | `04_03_create_meeting_minute_invalid_utf8.json` | POST /api/meeting-minute — 非 UTF-8 檔案回 400 | ✅ PASSED |

### 2.2 等價類劃分 (Equivalence Partitioning)

**應用數量**: 1 個請求檔  

| # | 資源 | 請求檔 | 說明 | 結果 |
|---|------|----------|------|------|
| 1 | `meeting-minute` | `01_01_create_meeting_minute.json` | POST /api/meeting-minute — 合法轉寫檔且 LLM 回傳有效 JSON 回 200 | ✅ PASSED |

### 2.3 決策表 (Decision Table)

**應用數量**: 1 個請求檔  

| # | 資源 | 請求檔 | 說明 | 結果 |
|---|------|----------|------|------|
| 1 | `meeting-minute` | `04_02_create_meeting_minute_bad_extension.json` | POST /api/meeting-minute — 副檔名非 .txt/.md 回 400 | ✅ PASSED |

### 2.4 錯誤猜測 (Error Guessing)

**應用數量**: 2 個請求檔  

| # | 資源 | 請求檔 | 說明 | 結果 |
|---|------|----------|------|------|
| 1 | `meeting-minute` | `04_01_create_meeting_minute_missing_file.json` | POST /api/meeting-minute — 未帶 file 欄位回 400 | ✅ PASSED |
| 2 | `meeting-minute` | `04_05_create_meeting_minute_llm_none_502.json` | POST /api/meeting-minute — LLM 無輸出（None）回 502 | ✅ PASSED |

### 2.5 狀態轉換 (State Transition Testing)

**應用數量**: 1 個請求檔  

| # | 資源 | 請求檔 | 說明 | 結果 |
|---|------|----------|------|------|
| 1 | `meeting-minute` | `04_04_create_meeting_minute_llm_unparsable_502.json` | POST /api/meeting-minute — LLM 輸出無法解析回 502 | ✅ PASSED |

---

## 三、整合測試摘要

> 共 6 個請求（每個請求檔一列，依檔名順序執行）

| # | 資源 | 檔名 | 說明 | 技術 | 方法 | 路徑 | 預期 | 實際 | 結果 | 耗時 |
|---|------|------|------|------|------|------|------|------|------|------|
| 1 | `meeting-minute` | `01_01_create_meeting_minute.json` | POST /api/meeting-minute — 合法轉寫檔且 LLM 回傳有效 JSON 回 200 | 等價類劃分 | POST | `/api/meeting-minute` | 200 | 200 | ✅ PASSED | 8ms |
| 2 | `meeting-minute` | `04_01_create_meeting_minute_missing_file.json` | POST /api/meeting-minute — 未帶 file 欄位回 400 | 錯誤猜測 | POST | `/api/meeting-minute` | 400 | 400 | ✅ PASSED | 0ms |
| 3 | `meeting-minute` | `04_02_create_meeting_minute_bad_extension.json` | POST /api/meeting-minute — 副檔名非 .txt/.md 回 400 | 決策表 | POST | `/api/meeting-minute` | 400 | 400 | ✅ PASSED | 1ms |
| 4 | `meeting-minute` | `04_03_create_meeting_minute_invalid_utf8.json` | POST /api/meeting-minute — 非 UTF-8 檔案回 400 | 邊界值分析 | POST | `/api/meeting-minute` | 400 | 400 | ✅ PASSED | 1ms |
| 5 | `meeting-minute` | `04_04_create_meeting_minute_llm_unparsable_502.json` | POST /api/meeting-minute — LLM 輸出無法解析回 502 | 狀態轉換 | POST | `/api/meeting-minute` | 502 | 502 | ✅ PASSED | 1ms |
| 6 | `meeting-minute` | `04_05_create_meeting_minute_llm_none_502.json` | POST /api/meeting-minute — LLM 無輸出（None）回 502 | 錯誤猜測 | POST | `/api/meeting-minute` | 502 | 502 | ✅ PASSED | 1ms |

---

## 四、測試覆蓋率

### `meeting-minute` 端點 view function 覆蓋率

| Operation ID | View function | 檔案 | 行範圍 | 語句數 | 未覆蓋 | 覆蓋率 | 未覆蓋行號 |
|--------------|---------------|------|--------|--------|--------|--------|-----------|
| `meeting_minute.create_meeting_minute` | `create_meeting_minute` | `routes/meeting_minute.py` | L35-L74 | 26 | 4 | 85% | 48, 50, 57, 61 |
| **合計** | | | | **26** | **4** | **85%** | |

**目前覆蓋率 84.6% → 目標 65%**（已達目標）

> 💡 請開發者在 `/Users/yehchitsai/2023_uniheart_startups/uniheart-works/ai-sdlc/backend/tests/integration/meeting-minute/requests` 自行新增案例（參考上表未覆蓋行號），用 `/Users/yehchitsai/2023_uniheart_startups/uniheart-works/ai-sdlc/.venv/bin/python ai-dev-tools/scripts/flask/flask_function_wrapper.py meeting-minute --all --coverage` 重跑確認，把覆蓋率提高到 60–70%。

---

## 五、執行時間分析

| 測試類型 | 請求數 | 總時間（主請求） | 平均時間 | 最慢請求 |
|---------|--------|--------|---------|---------|
| 整合測試 | 6 | 0.01s | 2ms | meeting-minute/01_01_create_meeting_minute.json (8ms) |

---
