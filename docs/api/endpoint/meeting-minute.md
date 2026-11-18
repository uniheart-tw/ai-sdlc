# API：會議記錄彙整（`/api/meeting-minute`）

上傳會議記錄文字檔，由 AI（Bedrock）彙整出摘要與與會者清單。

- 後端實作：`meeting_minute` Blueprint，路徑前綴 `/api/meeting-minute`
- 外部服務：AWS Bedrock（模型由 `BEDROCK_MODEL_ID` 設定）

> 撰寫格式見 [API_REFERENCE_TEMPLATE.md](../API_REFERENCE_TEMPLATE.md)；回應型態分類見 [RESPONSE_CONVENTIONS.md](../RESPONSE_CONVENTIONS.md)。

---

## POST /api/meeting-minute

上傳會議記錄並彙整。

### Description

接收 multipart 上傳的會議記錄檔，呼叫 Bedrock 產生摘要並擷取與會者姓名與 email。此端點**公開，無需認證**。

### Operation ID

`meeting_minute.summarize_meeting_minute`

### Tag

`meeting-minute`

### Validation Rules

- 欄位 `file` 必填，缺少或檔名為空回 `400 {"error":"缺少檔案"}`。
- 檔案大小不可超過 `MAX_UPLOAD_BYTES`（預設 1048576 bytes），超過回 `400 {"error":"檔案過大"}`。
- 檔案內容須為 UTF-8 文字且非空，否則回 `400 {"error":"檔案內容無法解析"}`。
- Bedrock 呼叫失敗或回傳內容無法解析回 `502`；呼叫逾時回 `504`。

### Request

**Method**: `POST`

**Headers**:

```
Content-Type: multipart/form-data
```

**Request Model（multipart/form-data）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `file` | file | Yes | 會議記錄文字檔（UTF-8） |

### Response

**Success (200 OK)** — 彙整結果，`MeetingMinuteResult`。

**Response Model（`MeetingMinuteResult`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `summary` | string | Yes | 會議摘要 |
| `attendees` | array of `Attendee` | Yes | 與會者清單，可為空陣列 |

**`Attendee`**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `name` | string | Yes | 與會者姓名 |
| `email` | string | Yes | 與會者 email |

```json
{
  "summary": "討論 Q3 產品時程，決議於 9 月底前完成 Beta 版。",
  "attendees": [
    { "name": "王小明", "email": "ming@example.com" },
    { "name": "李小華", "email": "hua@example.com" }
  ]
}
```

**Error (400 Bad Request)** — 缺少檔案、檔案過大或內容無法解析。

**Response Model（`Error`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "缺少檔案" }
```

**Error (502 Bad Gateway)** — Bedrock 呼叫失敗或回傳內容無法解析。

**Response Model（`Error`）**（同上 schema）:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "AI 服務呼叫失敗" }
```

**Error (504 Gateway Timeout)** — Bedrock 呼叫逾時。

**Response Model（`Error`）**（同上 schema）:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "AI 服務逾時" }
```

### Usage Example

```http
POST /api/meeting-minute HTTP/1.1
Host: localhost:5001
Content-Type: multipart/form-data; boundary=----form

------form
Content-Disposition: form-data; name="file"; filename="minutes.txt"
Content-Type: text/plain

（會議記錄文字）
------form--
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "summary": "討論 Q3 產品時程，決議於 9 月底前完成 Beta 版。",
  "attendees": [
    { "name": "王小明", "email": "ming@example.com" }
  ]
}
```
