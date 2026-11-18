# API：會議記錄彙整（`/api/meeting-minute`）

上傳會議轉寫檔，由大語言模型彙整成會議摘要，並回傳與會者名單。

- 後端實作：`backend/routes/` 的 `meeting_minute` Blueprint，路徑前綴 `/api/meeting-minute`；LLM 呼叫只透過 `services/` 內單一模組。
- 資料來源：上傳檔僅在記憶體處理，不落地儲存。

> 撰寫格式見 API_REFERENCE_TEMPLATE.md；回應型態分類見 RESPONSE_CONVENTIONS.md。

---

## POST /api/meeting-minute

上傳轉寫檔並回傳會議摘要與與會者。

### Description

接收 `multipart/form-data` 的轉寫檔（`.txt` 或 `.md`），由 LLM 產生會議記錄，回傳會議日期、Markdown 摘要與與會者名單。此端點**公開，無需認證**。會議日期取自檔名的 `YYYYMMDD`。轉寫中未出現的 EMAIL 以空字串回傳，不會捏造。

### Operation ID

`meeting_minute.create_meeting_minute`

### Tag

`meeting-minute`

### Validation Rules

- 缺少 `file` 欄位，回 `400 {"error":"缺少檔案"}`。
- 副檔名非 `.txt` / `.md`，回 `400 {"error":"僅接受 .txt 或 .md 檔案"}`。
- 檔案為空，回 `400 {"error":"檔案內容為空"}`。
- 檔案超過大小上限（預設 1 MB，由環境變數 `MAX_UPLOAD_BYTES` 設定），回 `400 {"error":"檔案超過大小上限"}`。
- 檔案非 UTF-8，回 `400 {"error":"檔案必須為 UTF-8 編碼"}`。
- 檔名不含合法的 `YYYYMMDD` 日期，回 `400 {"error":"檔名必須為 YYYYMMDD 格式"}`。
- LLM 呼叫失敗或輸出無法解析，回 `502`。

### Request

**Method**: `POST`

**Headers**:

```
Content-Type: multipart/form-data
```

**Request Model（multipart/form-data）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `file` | file | Yes | 轉寫檔，副檔名 `.txt` 或 `.md`，檔名格式 `YYYYMMDD.txt` / `YYYYMMDD.md`，UTF-8 編碼 |

### Response

**Success (200 OK)** — 彙整結果，`MeetingMinute`。

**Response Model（`MeetingMinute`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `meeting_date` | string | Yes | 會議日期，格式 `YYYY-MM-DD`，取自檔名 |
| `summary` | string | Yes | 會議摘要（Markdown），含基本資訊、討論事項、決議事項、行動事項、下次會議 |
| `attendees` | array of `Attendee` | Yes | 與會者名單，可為空陣列 |

`Attendee`:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `name` | string | Yes | 與會者姓名 |
| `email` | string | Yes | 與會者 EMAIL；轉寫中未出現時為空字串 |

```json
{
  "meeting_date": "2026-11-18",
  "summary": "## 基本資訊\n- 日期：2026/11/18\n\n## 決議事項\n- 下週開始 Sprint 2",
  "attendees": [
    { "name": "王小明", "email": "xiaoming@example.com" },
    { "name": "李小華", "email": "" }
  ]
}
```

**Error (400 Bad Request)** — 缺檔、副檔名不符、檔案為空、超過大小上限、非 UTF-8 或檔名日期格式不符。

**Response Model（`Error`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "僅接受 .txt 或 .md 檔案" }
```

**Error (502 Bad Gateway)** — LLM 呼叫失敗，或 LLM 輸出無法解析為預期的 JSON。

**Response Model（`Error`）**（同上 schema）:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "會議記錄產生失敗，請稍後再試" }
```

### Usage Example

```http
POST /api/meeting-minute HTTP/1.1
Host: localhost:5001
Content-Type: multipart/form-data; boundary=----example

------example
Content-Disposition: form-data; name="file"; filename="20261118.txt"
Content-Type: text/plain

（轉寫內容）
------example--
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "meeting_date": "2026-11-18",
  "summary": "## 基本資訊\n- 日期：2026/11/18",
  "attendees": [
    { "name": "王小明", "email": "xiaoming@example.com" }
  ]
}
```
