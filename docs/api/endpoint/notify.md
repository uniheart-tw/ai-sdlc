# API：會議記錄通知（`/api/notify`）

將會議摘要以 AWS SES 寄給與會者。

- 後端實作：`backend/routes/` 的 `notify` Blueprint，路徑前綴 `/api/notify`；SES 呼叫只透過 `services/` 內單一模組。
- 寄送方式：每位收件人各寄一封，收件人之間看不到彼此的 EMAIL。

> 撰寫格式見 API_REFERENCE_TEMPLATE.md；回應型態分類見 RESPONSE_CONVENTIONS.md。

---

## POST /api/notify

寄送會議摘要給與會者。

### Description

接收會議摘要與與會者名單，以 SES 從設定的寄件人（`SES_SENDER`，範例為 `sender@example.com`）寄出。此端點**公開，無需認證**。成功回 `204 No Content`，無 body。後端不在 log 記錄 EMAIL 與內文。

### Operation ID

`notify.send_notification`

### Tag

`notify`

### Validation Rules

- `summary` 缺少或去空白後為空，回 `400 {"error":"摘要不可為空"}`。
- `attendees` 缺少或為空陣列，回 `400 {"error":"至少需要一位與會者"}`。
- `attendees` 超過人數上限（預設 50），回 `400 {"error":"與會者人數超過上限"}`。
- 任一 `email` 格式錯誤，回 `400`，訊息指出是第幾筆，例如 `{"error":"第 2 位與會者的 EMAIL 格式錯誤"}`。
- SES 寄送失敗，回 `502`。

### Request

**Method**: `POST`

**Headers**:

```
Content-Type: application/json
```

**Request Model（JSON body）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `summary` | string | Yes | 會議摘要（Markdown），去空白後不可為空 |
| `attendees` | array of `Attendee` | Yes | 收件人名單，1 至 50 人 |

`Attendee`:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `name` | string | Yes | 與會者姓名 |
| `email` | string | Yes | 收件 EMAIL，需為合法格式 |

```json
{
  "summary": "## 基本資訊\n- 日期：2026/11/18\n\n## 決議事項\n- 下週開始 Sprint 2",
  "attendees": [
    { "name": "王小明", "email": "xiaoming@example.com" },
    { "name": "李小華", "email": "xiaohua@example.com" }
  ]
}
```

### Response

**Success (204 No Content)** — 寄送成功，無 response body，無 JSON Response Model。

**Error (400 Bad Request)** — 摘要為空、無收件人、人數超過上限或 EMAIL 格式錯誤。

**Response Model（`Error`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "第 2 位與會者的 EMAIL 格式錯誤" }
```

**Error (502 Bad Gateway)** — SES 寄送失敗。

**Response Model（`Error`）**（同上 schema）:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "郵件寄送失敗，請稍後再試" }
```

### Usage Example

```http
POST /api/notify HTTP/1.1
Host: localhost:5001
Content-Type: application/json

{
  "summary": "## 基本資訊\n- 日期：2026/11/18",
  "attendees": [
    { "name": "王小明", "email": "xiaoming@example.com" }
  ]
}
```

```http
HTTP/1.1 204 No Content
```
