# Flask 單元測試報告

**測試類型**: unit  
**測試日期**: 2026-11-18  
**測試結果**: ✅ 28 passed, ❌ 0 failed, ⚠️ 0 error, ⏭️ 0 skipped（共 28 個測試案例，含 parametrize 展開；13 個測試函數）  
**執行指令**: `/Users/yehchitsai/2023_uniheart_startups/uniheart-works/ai-sdlc/.venv/bin/python ai-dev-tools/scripts/flask/generate_test_report.py services.llm_service --kind unit --with-report --fail-on-error --config /Users/yehchitsai/2023_uniheart_startups/uniheart-works/ai-sdlc/backend/flask-he-config.yaml`
**本次對象**: `services.llm_service`（13 個測試函數）

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

> 單元測試對象（模組）: 1 個 | 測試函數: 13 個

| # | 模組 | 測試檔 | 測試函數數 | 結果 |
|---|------|--------|-----------|------|
| 1 | `services.llm_service` | `tests/unit/services/llm_service/test_unit_services_llm_service.py` | 13 | ✅ |

### `services.llm_service`

#### 原始碼函數清單（6 個）

| # | 名稱 | 類型 | 行號 | 說明 |
|---|------|------|------|------|
| 1 | `LLMError` | class | L20 | LLM 呼叫失敗或輸出無法解析。 |
| 2 | `build_prompt` | function | L24 | 讀取提示詞範本並帶入會議日期與轉寫內容。 |
| 3 | `invoke_model` | function | L32 | 以 Bedrock converse 呼叫模型，回傳文字輸出。外部服務唯一出口。 |
| 4 | `_extract_json` | function | L46 | 從模型輸出取出 JSON 物件（容忍程式碼圍欄與前後文字）。 |
| 5 | `parse_result` | function | L67 | 驗證並正規化 LLM 輸出為 {summary, attendees}。 |
| 6 | `generate_meeting_minute` | function | L91 | 彙整會議記錄；任何失敗一律拋出 LLMError。 |

#### 函數與測試函數列表

**build_prompt**

| # | 測試函數 | 技術 | 說明 | 結果 |
|---|----------|------|------|------|
| 1 | `test_build_prompt_replaces_placeholders` | 等價類劃分 | 日期與轉寫內容被帶入提示詞 | ✅ PASSED |
| 2 | `test_build_prompt_transcript_with_braces` | 錯誤猜測 | 轉寫內容含特殊字元仍原樣保留 | ✅ PASSED |

**invoke_model**

| # | 測試函數 | 技術 | 說明 | 結果 |
|---|----------|------|------|------|
| 1 | `test_invoke_model_joins_text_parts` | 狀態轉換 | 設定齊全後呼叫 converse 並串接文字片段 | ✅ PASSED |
| 2 | `test_invoke_model_missing_config_raises` | 錯誤猜測 | 缺少 LLM 設定時拋出例外 | ✅ PASSED |

**_extract_json**

| # | 測試函數 | 技術 | 說明 | 結果 |
|---|----------|------|------|------|
| 1 | `test_extract_json_formats` | 決策表 | 純 JSON、圍欄、無語言圍欄、前後文字皆可解析 | ✅ PASSED |
| 2 | `test_extract_json_invalid` | 錯誤猜測 | 無效輸出拋出 LLMError | ✅ PASSED |

**parse_result**

| # | 測試函數 | 技術 | 說明 | 結果 |
|---|----------|------|------|------|
| 1 | `test_parse_result_valid` | 等價類劃分 | 有效輸出被正規化 | ✅ PASSED |
| 2 | `test_parse_result_empty_attendees` | 邊界值分析 | attendees 為空清單時回傳空清單 | ✅ PASSED |
| 3 | `test_parse_result_invalid_raises` | 錯誤猜測 | 非字串或欄位格式錯誤拋出 LLMError | ✅ PASSED |

**generate_meeting_minute**

| # | 測試函數 | 技術 | 說明 | 結果 |
|---|----------|------|------|------|
| 1 | `test_generate_meeting_minute_success` | 狀態轉換 | 模型回傳有效 JSON 時得到正規化結果 | ✅ PASSED |
| 2 | `test_generate_meeting_minute_llm_error_passthrough` | 錯誤猜測 | invoke_model 拋 LLMError 時原樣拋出 | ✅ PASSED |
| 3 | `test_generate_meeting_minute_wraps_unexpected_exception` | 錯誤猜測 | 其他例外被包成 LLMError 並保留原因 | ✅ PASSED |
| 4 | `test_generate_meeting_minute_parse_failure` | 錯誤猜測 | 模型輸出無法解析時拋出 LLMError | ✅ PASSED |

### 測試品質技術統計

| 技術 | 測試函數數 |
|------|-----------|
| 邊界值分析 | 1 |
| 等價類劃分 | 2 |
| 決策表 | 1 |
| 錯誤猜測 | 7 |
| 狀態轉換 | 2 |
| **合計** | **13** |

---

## 二、測試品質技術應用詳細說明

### 2.1 邊界值分析 (Boundary Value Analysis)

**應用數量**: 1 個測試函數  

| # | 對象 | 測試函數 | 說明 | 結果 |
|---|------|----------|------|------|
| 1 | `services.llm_service` | `test_parse_result_empty_attendees` | attendees 為空清單時回傳空清單 | ✅ PASSED |

### 2.2 等價類劃分 (Equivalence Partitioning)

**應用數量**: 2 個測試函數  

| # | 對象 | 測試函數 | 說明 | 結果 |
|---|------|----------|------|------|
| 1 | `services.llm_service` | `test_build_prompt_replaces_placeholders` | 日期與轉寫內容被帶入提示詞 | ✅ PASSED |
| 2 | `services.llm_service` | `test_parse_result_valid` | 有效輸出被正規化 | ✅ PASSED |

### 2.3 決策表 (Decision Table)

**應用數量**: 1 個測試函數  

| # | 對象 | 測試函數 | 說明 | 結果 |
|---|------|----------|------|------|
| 1 | `services.llm_service` | `test_extract_json_formats` | 純 JSON、圍欄、無語言圍欄、前後文字皆可解析 | ✅ PASSED |

### 2.4 錯誤猜測 (Error Guessing)

**應用數量**: 7 個測試函數  

| # | 對象 | 測試函數 | 說明 | 結果 |
|---|------|----------|------|------|
| 1 | `services.llm_service` | `test_build_prompt_transcript_with_braces` | 轉寫內容含特殊字元仍原樣保留 | ✅ PASSED |
| 2 | `services.llm_service` | `test_invoke_model_missing_config_raises` | 缺少 LLM 設定時拋出例外 | ✅ PASSED |
| 3 | `services.llm_service` | `test_extract_json_invalid` | 無效輸出拋出 LLMError | ✅ PASSED |
| 4 | `services.llm_service` | `test_parse_result_invalid_raises` | 非字串或欄位格式錯誤拋出 LLMError | ✅ PASSED |
| 5 | `services.llm_service` | `test_generate_meeting_minute_llm_error_passthrough` | invoke_model 拋 LLMError 時原樣拋出 | ✅ PASSED |
| 6 | `services.llm_service` | `test_generate_meeting_minute_wraps_unexpected_exception` | 其他例外被包成 LLMError 並保留原因 | ✅ PASSED |
| 7 | `services.llm_service` | `test_generate_meeting_minute_parse_failure` | 模型輸出無法解析時拋出 LLMError | ✅ PASSED |

### 2.5 狀態轉換 (State Transition Testing)

**應用數量**: 2 個測試函數  

| # | 對象 | 測試函數 | 說明 | 結果 |
|---|------|----------|------|------|
| 1 | `services.llm_service` | `test_invoke_model_joins_text_parts` | 設定齊全後呼叫 converse 並串接文字片段 | ✅ PASSED |
| 2 | `services.llm_service` | `test_generate_meeting_minute_success` | 模型回傳有效 JSON 時得到正規化結果 | ✅ PASSED |

---

## 三、整合測試摘要

本報告為單元測試報告；整合測試見 `tests/integration-test-case-report.md`。

---

## 四、測試覆蓋率

### 模組覆蓋率

| 模組 | 語句數 | 未覆蓋 | 行覆蓋率 | 未覆蓋行號 |
|------|--------|--------|---------|-----------|
| `services.llm_service` | 73 | 0 | 100% | - |
| **TOTAL（測試對象）** | **73** | **0** | **100%** | |
| **coverage.unit_source 合計** | **73** | **0** | **100%** | |

### 函數覆蓋率

| 模組 | 函數名稱 | 行範圍 | 語句數 | 覆蓋率 | 狀態 |
|------|----------|--------|--------|--------|------|
| `services.llm_service` | `LLMError` | L20-L21 | 1 | 100% | ✅ |
| `services.llm_service` | `build_prompt` | L24-L29 | 3 | 100% | ✅ |
| `services.llm_service` | `invoke_model` | L32-L43 | 7 | 100% | ✅ |
| `services.llm_service` | `_extract_json` | L46-L64 | 18 | 100% | ✅ |
| `services.llm_service` | `parse_result` | L67-L88 | 21 | 100% | ✅ |
| `services.llm_service` | `generate_meeting_minute` | L91-L105 | 14 | 100% | ✅ |

---

## 五、執行時間分析

| 測試類型 | 測試數 | 總時間（call） | 平均時間 | 最慢測試 |
|---------|--------|--------|---------|---------|
| 單元測試 | 28 | 0.05s | 2ms | test_build_prompt_replaces_placeholders (50ms) |

---
