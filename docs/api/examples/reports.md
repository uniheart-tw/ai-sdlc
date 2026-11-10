# API：報表（`/api/reports`）

結果查詢與匯出相關 API。

> 撰寫格式見 [API_REFERENCE_TEMPLATE.md](../API_REFERENCE_TEMPLATE.md)；回應型態分類見 [RESPONSE_CONVENTIONS.md](../RESPONSE_CONVENTIONS.md)。

---

## GET /api/reports/results

列出結果清單。

### Description

取得結果清單，每筆包含 `subject_name`。此端點**需認證**（Bearer token）。

### Operation ID

`reports.list_results`

### Tag

`reports`

### Request

**Method**: `GET`

**Headers**:

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Model**: None（無 request body）

### Response

**Success (200 OK)** — 直接回結果陣列（無統一外層），每個元素為 `Result`。

**Response Model（`Result` 陣列）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `result_id` | integer | Yes | 結果主鍵（具名欄位，非 `id`） |
| `subject_id` | integer | No | 對象 ID |
| `subject_name` | string | No | 對象名稱 |
| `score` | number | No | 分數 |
| `started_at` | string | No | 開始時間 |
| `finished_at` | string | No | 完成時間 |
| `created_at` | string | No | 建立時間 |

```json
[
  {
    "result_id": 100,
    "subject_id": 3,
    "subject_name": "範例對象",
    "score": 80.0,
    "started_at": "2026-01-02 09:00:00",
    "finished_at": "2026-01-02 09:30:00",
    "created_at": "2026-01-02 09:30:00"
  }
]
```

**Error (401 Unauthorized)** — 缺少 token、格式錯誤、簽章無效或已過期。

**Response Model（`Error`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "未授權或憑證失效" }
```

### Usage Example

```http
GET /api/reports/results HTTP/1.1
Host: localhost:5001
Authorization: Bearer <token>
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "result_id": 100,
    "subject_id": 3,
    "subject_name": "範例對象",
    "score": 80.0,
    "started_at": "2026-01-02 09:00:00",
    "finished_at": "2026-01-02 09:30:00",
    "created_at": "2026-01-02 09:30:00"
  }
]
```

---

## GET /api/reports/export

匯出結果為 Excel。**特例：回應非 JSON，為 xlsx 位元組，無 JSON Response Model。**

### Description

匯出結果清單為 xlsx 檔。此端點**需認證**（Bearer token）。

### Operation ID

`reports.export_results`

### Tag

`reports`

### Request

**Method**: `GET`

**Headers**:

```
Authorization: Bearer {access_token}
```

**Request Model**: None（無 request body）

### Response

**Success (200 OK)** — 特例：非 JSON，回 xlsx 位元組。

- `Content-Type`：`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`。
- `Content-Disposition: attachment; filename=report.xlsx`。
- body 為 xlsx 二進位內容，無 JSON Response Model。

**Error (401 Unauthorized)** — 缺少 token、格式錯誤、簽章無效或已過期。

**Response Model（`Error`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "未授權或憑證失效" }
```

### Usage Example

```http
GET /api/reports/export HTTP/1.1
Host: localhost:5001
Authorization: Bearer <token>
```

```http
HTTP/1.1 200 OK
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename=report.xlsx

<xlsx 二進位內容>
```
