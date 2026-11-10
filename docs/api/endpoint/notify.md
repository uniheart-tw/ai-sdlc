# API：寄送通知（`/api/notify`）

將會議記錄摘要以 AWS SES 寄給每位與會者。

- 後端實作：`backend/routes/notify.py`（Blueprint `notify`，路徑 `/api/notify`）；寄信只經 `backend/services/` 單一模組呼叫。
- 資料來源：請求 body 傳入的摘要與與會者名單，不儲存。

> 撰寫格式（區塊順序、Request/Response Model）見 [API_REFERENCE_TEMPLATE.md](../API_REFERENCE_TEMPLATE.md)；回應型態分類見 [RESPONSE_CONVENTIONS.md](../RESPONSE_CONVENTIONS.md)。

---

## POST /api/notify

寄送會議記錄通知給與會者。

### Description

送出摘要與與會者名單，系統逐一寄信給每位與會者。此端點**公開，無需認證**。成功時回 `204 No Content`（無 body）。任一收件人寄送失敗即回 502。後端 log 不記錄 email 與摘要內容。

### Operation ID

`notify.send_notify`

### Tag

`notify`

### Validation Rules

- 請求 body 不是合法 JSON 物件，回 `400 {"error":"請求內容必須為 JSON"}`。
- `summary` 缺少或去空白後為空，回 `400 {"error":"缺少會議摘要"}`。
- `attendees` 缺少或為空陣列，回 `400 {"error":"缺少與會者名單"}`。
- 任一 `attendees[].email` 為空或格式不合法，回 `400 {"error":"與會者 email 格式錯誤"}`。
- SES 寄送失敗（任一收件人），回 `502 {"error":"寄送通知失敗，請稍後再試"}`。

### Request

**Method**: `POST`

**Headers**:

```
Content-Type: application/json
```

**Request Model（JSON body）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `summary` | string | Yes | 會議記錄摘要（Markdown 純文字，去空白後不可為空） |
| `attendees` | array of `Attendee` | Yes | 收件的與會者名單，至少一位 |

**`Attendee`**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `name` | string | Yes | 與會者姓名 |
| `email` | string | Yes | 收件 email，須為合法格式 |

```json
{
  "summary": "# 會議記錄\n\n## 基本資訊\n- 日期：2026/11/10",
  "attendees": [
    { "name": "王小明", "email": "ming@example.com" },
    { "name": "李小華", "email": "hua@example.com" }
  ]
}
```

### Response

**Success (204 No Content)** — 寄送成功，無回應 body，無 JSON Response Model。

**Response Model**: None（204 無 response body；下方 `null` 僅表示 body 為空）

```json
null
```

**Error (400 Bad Request)** — 摘要為空、名單為空或 email 格式錯誤。

**Response Model（`Error`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "與會者 email 格式錯誤" }
```

**Error (502 Bad Gateway)** — SES 寄送失敗。

**Response Model（`Error`）**（同上 schema）:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "寄送通知失敗，請稍後再試" }
```

### Usage Example

```http
POST /api/notify HTTP/1.1
Host: localhost:5001
Content-Type: application/json

{
  "summary": "# 會議記錄\n\n## 基本資訊\n- 日期：2026/11/10",
  "attendees": [
    { "name": "王小明", "email": "ming@example.com" }
  ]
}
```

```http
HTTP/1.1 204 No Content
```

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{ "error": "缺少與會者名單" }
```

```http
HTTP/1.1 502 Bad Gateway
Content-Type: application/json

{ "error": "寄送通知失敗，請稍後再試" }
```
