# API：寄送通知（`/api/notify`）

將會議摘要以 email 寄給與會者。

- 後端實作：`notify` Blueprint，路徑前綴 `/api/notify`
- 外部服務：AWS SES（寄件者由 `MAIL_FROM` 設定）

> 撰寫格式見 [API_REFERENCE_TEMPLATE.md](../API_REFERENCE_TEMPLATE.md)；回應型態分類見 [RESPONSE_CONVENTIONS.md](../RESPONSE_CONVENTIONS.md)。

---

## POST /api/notify

寄送會議摘要通知。

### Description

將摘要寄給 `attendees` 內的每位與會者，成功回 `204`，無 body。此端點**公開，無需認證**。

### Operation ID

`notify.send_notify`

### Tag

`notify`

### Validation Rules

- `summary` 必填，缺少或去空白後為空回 `400 {"error":"缺少摘要"}`。
- `attendees` 必須為非空陣列，否則回 `400 {"error":"缺少收件者"}`。
- 每個 `attendees` 元素需有 `name` 與格式合法的 `email`，否則回 `400 {"error":"收件者格式不正確"}`。
- SES 寄送失敗回 `502`。

### Request

**Method**: `POST`

**Headers**:

```
Content-Type: application/json
```

**Request Model（JSON body）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `summary` | string | Yes | 會議摘要（去空白後不可為空） |
| `attendees` | array of `Attendee` | Yes | 收件者清單，至少一筆 |

**`Attendee`**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `name` | string | Yes | 收件者姓名 |
| `email` | string | Yes | 收件者 email |

```json
{
  "summary": "討論 Q3 產品時程，決議於 9 月底前完成 Beta 版。",
  "attendees": [
    { "name": "王小明", "email": "ming@example.com" }
  ]
}
```

### Response

**Success (204 No Content)** — 特例：寄送成功，無 response body，無 JSON Response Model。

- `Content-Type`：`text/plain`（無 body，僅為工具標記非 JSON）。

**Error (400 Bad Request)** — 缺少摘要、缺少收件者或收件者格式不正確。

**Response Model（`Error`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "缺少摘要" }
```

**Error (502 Bad Gateway)** — SES 寄送失敗。

**Response Model（`Error`）**（同上 schema）:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "郵件寄送失敗" }
```

### Usage Example

```http
POST /api/notify HTTP/1.1
Host: localhost:5001
Content-Type: application/json

{
  "summary": "討論 Q3 產品時程，決議於 9 月底前完成 Beta 版。",
  "attendees": [
    { "name": "王小明", "email": "ming@example.com" }
  ]
}
```

```http
HTTP/1.1 204 No Content
```
