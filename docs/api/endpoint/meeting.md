# API：會議彙整（`/api/meeting-minute`）

上傳會議轉寫檔，由 LLM（Claude Sonnet 4.0，經 AWS Bedrock）彙整成會議記錄摘要與與會者名單。

- 後端實作：`backend/routes/meeting.py`（Blueprint `meeting`，路徑 `/api/meeting-minute`）；LLM 只經 `backend/services/` 單一模組呼叫。
- 資料來源：使用者上傳的 `.txt` / `.md` 轉寫檔，於記憶體處理，不落地儲存。

> 撰寫格式（區塊順序、Request/Response Model）見 [API_REFERENCE_TEMPLATE.md](../API_REFERENCE_TEMPLATE.md)；回應型態分類見 [RESPONSE_CONVENTIONS.md](../RESPONSE_CONVENTIONS.md)。

---

## POST /api/meeting-minute

上傳轉寫檔並取得會議記錄摘要與與會者名單。

### Description

以 `multipart/form-data` 上傳單一轉寫檔（欄位 `file`），後端驗證後交由 LLM 彙整，回傳 Markdown 摘要與與會者名單。此端點**公開，無需認證**。

- 檔名須為 `YYYYMMDD.txt` 或 `YYYYMMDD.md`，會議日期由檔名提取。
- 檔案編碼為 UTF-8，大小上限由環境變數 `MAX_UPLOAD_BYTES` 設定（預設 1 MB）。
- 轉寫檔通常不含 email，`attendees[].email` 可能為空字串，由前端讓使用者補填。
- LLM 呼叫可能耗時數十秒。

### Operation ID

`meeting.meeting_minute`

### Tag

`meeting`

### Validation Rules

- 未帶 `file` 欄位或檔名為空，回 `400 {"error":"缺少上傳檔案"}`。
- 副檔名不是 `.txt` / `.md`，回 `400 {"error":"僅支援 .txt 或 .md 檔案"}`。
- 檔名不符 `YYYYMMDD`（8 位數字且為合法日期），回 `400 {"error":"檔名須為 YYYYMMDD.txt 或 YYYYMMDD.md"}`。
- 檔案內容為空（去空白後無內容），回 `400 {"error":"檔案內容為空"}`。
- 檔案超過大小上限，回 `400 {"error":"檔案超過大小上限"}`。
- LLM 呼叫失敗，或輸出無法解析為「摘要＋與會者」，回 `502 {"error":"會議彙整失敗，請稍後再試"}`。

### Request

**Method**: `POST`

**Headers**:

```
Content-Type: multipart/form-data
```

**Request Model（multipart/form-data）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `file` | file | Yes | 會議轉寫檔，`.txt` / `.md`，檔名 `YYYYMMDD.<ext>`，UTF-8，不得為空 |

### Response

**Success (200 OK)** — 會議彙整結果，固定小物件（動作類，非資源），`MeetingMinuteResult`。

**Response Model（`MeetingMinuteResult`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `summary` | string | Yes | 會議記錄摘要（Markdown，繁體中文，含基本資訊、討論事項、決議事項、行動事項、下次會議） |
| `attendees` | array of `Attendee` | Yes | 與會者名單，可為空陣列 |

**`Attendee`**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `name` | string | Yes | 與會者姓名 |
| `email` | string | Yes | 與會者 email；轉寫檔未提供時為空字串 |

```json
{
  "summary": "# 會議記錄\n\n## 基本資訊\n- 日期：2026/11/10\n\n## 討論事項\n- 討論專案進度\n\n## 決議事項\n- 下週完成 API 規格\n\n## 行動事項\n- 王小明：整理 API 文件\n\n## 下次會議\n- 2026/11/17",
  "attendees": [
    { "name": "王小明", "email": "ming@example.com" },
    { "name": "李小華", "email": "" }
  ]
}
```

**Error (400 Bad Request)** — 缺檔、副檔名不符、檔名無 `YYYYMMDD`、空檔或超過大小上限。

**Response Model（`Error`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "僅支援 .txt 或 .md 檔案" }
```

**Error (502 Bad Gateway)** — LLM 呼叫失敗或輸出無法解析。

**Response Model（`Error`）**（同上 schema）:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "會議彙整失敗，請稍後再試" }
```

### Usage Example

```http
POST /api/meeting-minute HTTP/1.1
Host: localhost:5001
Content-Type: multipart/form-data; boundary=----example

------example
Content-Disposition: form-data; name="file"; filename="20261110.txt"
Content-Type: text/plain

王小明：今天討論專案進度……
------example--
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "summary": "# 會議記錄\n\n## 基本資訊\n- 日期：2026/11/10",
  "attendees": [
    { "name": "王小明", "email": "ming@example.com" },
    { "name": "李小華", "email": "" }
  ]
}
```

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{ "error": "檔名須為 YYYYMMDD.txt 或 YYYYMMDD.md" }
```

```http
HTTP/1.1 502 Bad Gateway
Content-Type: application/json

{ "error": "會議彙整失敗，請稍後再試" }
```
