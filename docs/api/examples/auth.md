# API：登入與身分驗證（`/api/auth`）

登入與身分驗證相關 API。

> 撰寫格式（區塊順序、Request/Response Model）見 [API_REFERENCE_TEMPLATE.md](../API_REFERENCE_TEMPLATE.md)；回應型態分類見 [RESPONSE_CONVENTIONS.md](../RESPONSE_CONVENTIONS.md)。

---

## POST /api/auth/login

驗證使用者帳號密碼，成功時回傳 `token`、使用者名稱與角色。

### Description

以帳號與密碼登入。此端點**公開，無需認證**。成功回傳 `token`，後續請求可用 `Authorization: Bearer <token>` 帶入。後端會對 `username` 去除前後空白。

### Operation ID

`auth.login`

### Tag

`auth`

### Request

**Method**: `POST`

**Headers**:

```
Content-Type: application/json
```

**Request Model（JSON body）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `username` | string | Yes | 登入帳號（後端會 `trim` 前後空白） |
| `password` | string | Yes | 登入密碼 |

```json
{ "username": "alice", "password": "example-password" }
```

### Response

**Success (200 OK)** — 登入成功，回固定小物件（非資源），`LoginResult`。

**Response Model（`LoginResult`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `token` | string | Yes | 登入憑證，後續請求以 `Authorization: Bearer <token>` 帶入 |
| `username` | string | Yes | 登入帳號 |
| `role` | string | Yes | 使用者角色 |

```json
{ "token": "eyJ1c2VybmFtZSI6ImFsaWNlIn0.Zx...", "username": "alice", "role": "member" }
```

**Error (401 Unauthorized)** — 帳號不存在或密碼錯誤。缺少 / 為空的 `username` / `password` 同樣回 `401`（不區分「未填寫」與「錯誤」，避免洩漏帳號是否存在）。

**Response Model（`Error`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "帳號或密碼錯誤" }
```

### Usage Example

```http
POST /api/auth/login HTTP/1.1
Host: localhost:5001
Content-Type: application/json

{ "username": "alice", "password": "example-password" }
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{ "token": "eyJ1c2VybmFtZSI6...", "username": "alice", "role": "member" }
```
