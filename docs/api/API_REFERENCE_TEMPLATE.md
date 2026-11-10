# API 端點文件範本（Python Flask）

本檔是**單一 API 端點**的撰寫範本，示範如何為一個 Flask 端點寫出一致、可自動轉換為 OpenAPI 的 Markdown 參考文件。
在 `docs/api/endpoint/<resource>.md` 新增端點時，複製下方對應區塊（GET / POST / PUT / DELETE），替換路徑、欄位與範例即可。
範例以通用的 `items` 資源示意，請依實際資源改寫，勿照抄範例的假資料。
完整的檔案範例見 [`examples/`](./examples/)（`auth.md`：公開端點；`reports.md`：需認證、含非 JSON 的檔案下載）。範例**不要**放進 `endpoint/`，否則會被當成本專案的端點，合併進 `openapi.yaml` 並成為測試對象。

## 檔案分工

| 檔案 | 內容 | 誰維護 |
|------|------|--------|
| `docs/api/endpoint/<resource>.md` | 各資源的端點文件（本範本的格式） | 手寫 |
| `docs/api/endpoint/metadata.yaml` | **整個 repo 共用**的 API 名稱、版本、伺服器位址、認證方式定義 | 手寫 |
| `docs/api/API_REFERENCE.md`、`docs/api/openapi.yaml` | 生成物 | 工具生成，勿手動編輯 |

## 專案層級 metadata（`docs/api/endpoint/metadata.yaml`）

API 名稱、版本、伺服器位址與認證方式屬於整個 repo，不寫在單一端點檔。
`build-reference.py` 合併時會讀這個檔，寫成 `API_REFERENCE.md` 檔首的 YAML front matter；`md-to-openapi.py` 再從 `API_REFERENCE.md` 取用。鍵名與 OpenAPI 相同，原樣寫入 `openapi.yaml`：

```yaml
info:
  title: Example API
  version: 1.0.0
  description: 範例 API。

servers:
  - url: http://localhost:5001
    description: 本機 Flask 開發伺服器

securitySchemes:
  BearerAuth:
    type: http
    scheme: bearer
    description: "登入取得 token，以 `Authorization: Bearer <token>` 帶入。"
```

- 沒有這個檔時 `API_REFERENCE.md` 不輸出 front matter，`openapi.yaml` 使用預設值且不產生 security。
- `md-to-openapi.py` 的 `--title` / `--version` / `--description` / `--server-url` 優先於 front matter。
- 修改 `metadata.yaml` 後，要重新執行合併（`build-reference.py`）才會生效。

## 檔案結構

一個資源一個檔（`docs/api/endpoint/<resource>.md`），檔首先寫資源說明，再依序列出各端點：

```markdown
# API：<資源名稱>（`/api/<resource>`）

<一句話說明這組 API 的用途。>

- 後端實作：<實作位置、Blueprint 名稱與路徑前綴>
- 資料來源：<資料來源說明（選填）>

> 撰寫格式見 API_REFERENCE_TEMPLATE.md；回應型態分類見 RESPONSE_CONVENTIONS.md。

---

## <METHOD> /api/<path>

（端點區塊，見下方範本）

---

## <METHOD> /api/<path>
...
```

端點之間以 `---` 分隔。檔案中**只放端點區塊**：每個 `## <METHOD> /api/<path>` 之後到下一個端點標題之前的內容，都會被視為該端點的內容，所以不要在端點之後另加與端點無關的章節。

## 撰寫規則

> **事實來源**：端點行為以後端實際實作為準。撰寫時以程式實際行為填寫，文件描述現況。

> **端點標題**：`## <METHOD> /api/<path>`。路徑參數寫成 `{item_id}`（OpenAPI 風格）。

> **Operation ID**：每個端點的 `### Operation ID` 值需全專案唯一，採 Flask 的「Blueprint 名.view 函式名」（例如 `items.list_items`）。
> 此值會由 md→openapi 工具輸出為 OpenAPI 的 `operationId`。

> **Tag**：每個端點都要標 `### Tag`（資源群組，放在 Operation ID 之後），值用資源群組名（例如 `items`）。
> 此值會輸出為 OpenAPI 的 `tags`，**以此為準，不從路徑推斷**。

> **每個端點都要有 Request Model 與 Response Model**：Request body 與**每一個** Response（成功與各錯誤）
> 都要附結構化 Model 表（欄位、型別、必填、說明）＋ JSON 範例。回應型態分類一律遵循
> [RESPONSE_CONVENTIONS.md](./RESPONSE_CONVENTIONS.md)（成功回裸資源、錯誤 `{"error":...}`、刪除回 `{"status":"deleted"}` 等）。
> 無 request body 的端點（GET / DELETE）Request Model 標「None」。

## 認證

認證方式（例如 Bearer token）定義在 `metadata.yaml` 的 `securitySchemes`。
**每個端點是否需要認證，由該端點 `### Request` 的 `**Headers**` 區塊決定**，工具不猜測、不看說明文字：

| 端點類型 | `### Request` 怎麼寫 | 生成的 OpenAPI |
|----------|---------------------|----------------|
| 需認證（Bearer token） | Headers 列 `Authorization: Bearer {access_token}` | `security: [{BearerAuth: []}]` |
| 以自訂 header 認證（`apiKey`，in: header） | Headers 列該 scheme 的 `name`，例如 `X-Api-Key: {key}` | 套用對應的 scheme |
| 公開（無需認證） | Headers **不含**任何認證標頭，並在 `### Description` 註明「公開，無需認證」 | `security: []` |

- `metadata.yaml` 沒有定義 `securitySchemes` 時，整份 spec 不輸出 `security`。
- 需認證的端點，Response 一律列出 `Error (401 Unauthorized)`，讓規格中看得出哪些端點受保護。
- Headers 要寫成程式碼區塊，每行一個 `Name: value`（見下方範例）。

---

## GET /api/items

列出項目（讀取類範本，需認證）。

### Description

取得項目清單，可用 query 參數篩選。此端點**需認證**（Bearer token）。

### Operation ID

`items.list_items`

### Tag

`items`

### Request

**Method**: `GET`

**Headers**:

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Query Parameters**（Optional）:

| Parameter | Type | Required | Description |
|-----------|------|:----:|------|
| `status` | string | No | 篩選狀態，僅接受 `enabled` / `disabled`；其他值回 400 |

**Request Model**: None（無 request body）

### Response

**Success (200 OK)** — 直接回資源陣列（無統一外層），每個元素為 `Item`。

**Response Model（`Item` 陣列）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `item_id` | integer | Yes | 項目主鍵（具名欄位，非 `id`） |
| `name` | string | Yes | 項目名稱 |
| `description` | string | No | 說明 |
| `status` | string | Yes | `enabled` / `disabled` |
| `created_at` | string(date-time) | No | 建立時間（ISO 8601） |

```json
[
  {
    "item_id": 1,
    "name": "範例項目",
    "description": "這是一個範例",
    "status": "enabled",
    "created_at": "2026-02-28T10:30:00"
  }
]
```

**Error (400 Bad Request)** — 參數不合法。

**Response Model（`Error`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "status 必須為 enabled 或 disabled" }
```

**Error (401 Unauthorized)** — 缺少 token、格式錯誤、簽章無效或已過期。

**Response Model（`Error`）**（同上 schema）:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "未授權或憑證失效" }
```

### Usage Example

```http
GET /api/items?status=enabled HTTP/1.1
Host: localhost:5001
Authorization: Bearer <token>
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "item_id": 1,
    "name": "範例項目",
    "description": "這是一個範例",
    "status": "enabled",
    "created_at": "2026-02-28T10:30:00"
  }
]
```

---

## POST /api/items

新增項目（建立類範本，需認證）。

### Description

建立一筆項目，成功回建立後的資源。此端點**需認證**（Bearer token）。

### Operation ID

`items.create_item`

### Tag

`items`

### Validation Rules

- `name` 必填，缺少或去空白後為空回 `400 {"error":"缺少項目名稱"}`。
- `status` 若有提供，僅接受 `enabled` / `disabled`，否則回 `400 {"error":"status 必須為 enabled 或 disabled"}`。

### Request

**Method**: `POST`

**Headers**:

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Model（JSON body）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `name` | string | Yes | 項目名稱（去空白後不可為空） |
| `description` | string | No | 說明 |
| `status` | string | No | `enabled` / `disabled`，預設 `enabled` |

```json
{ "name": "新項目", "description": "新項目的說明" }
```

### Response

**Success (201 Created)** — 建立後的資源，`Item`。

**Response Model（`Item`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `item_id` | integer | Yes | 項目主鍵 |
| `name` | string | Yes | 項目名稱 |
| `description` | string | No | 說明 |
| `status` | string | Yes | `enabled` / `disabled` |
| `created_at` | string(date-time) | No | 建立時間 |

```json
{
  "item_id": 7,
  "name": "新項目",
  "description": "新項目的說明",
  "status": "enabled",
  "created_at": "2026-02-28T10:35:00"
}
```

**Error (400 Bad Request)** — 缺必填 / 格式不符。

**Response Model（`Error`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "缺少項目名稱" }
```

**Error (401 Unauthorized)** — 缺少 token 或憑證失效。

**Response Model（`Error`）**（同上 schema）:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "未授權或憑證失效" }
```

### Usage Example

```http
POST /api/items HTTP/1.1
Host: localhost:5001
Authorization: Bearer <token>
Content-Type: application/json

{ "name": "新項目", "description": "新項目的說明" }
```

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "item_id": 7,
  "name": "新項目",
  "description": "新項目的說明",
  "status": "enabled",
  "created_at": "2026-02-28T10:35:00"
}
```

---

## PUT /api/items/{item_id}

更新項目（更新類範本，回更新後資源，需認證）。

### Description

更新指定項目的欄位，未提供的欄位保持不變。此端點**需認證**（Bearer token）。

### Operation ID

`items.update_item`

### Tag

`items`

### Request

**Method**: `PUT`

**Headers**:

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|:----:|------|
| `item_id` | integer | Yes | 項目主鍵 |

**Request Model（JSON body，皆選填，未提供保持不變）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `name` | string | No | 項目名稱 |
| `description` | string | No | 說明 |
| `status` | string | No | `enabled` / `disabled`；其他值回 400 |

```json
{ "name": "更新後的名稱", "description": "更新後的說明", "status": "enabled" }
```

### Response

**Success (200 OK)** — 更新後的資源，`Item`。

**Response Model（`Item`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `item_id` | integer | Yes | 項目主鍵 |
| `name` | string | Yes | 項目名稱 |
| `description` | string | No | 說明 |
| `status` | string | Yes | `enabled` / `disabled` |
| `created_at` | string(date-time) | No | 建立時間 |

```json
{
  "item_id": 7,
  "name": "更新後的名稱",
  "description": "更新後的說明",
  "status": "enabled",
  "created_at": "2026-02-28T10:35:00"
}
```

**Error (400 Bad Request)** — `status` 值不合法。

**Response Model（`Error`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "status 必須為 enabled 或 disabled" }
```

**Error (401 Unauthorized)** — 缺少 token 或憑證失效。

**Response Model（`Error`）**（同上 schema）:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "未授權或憑證失效" }
```

**Error (404 Not Found)** — 項目不存在。

**Response Model（`Error`）**（同上 schema）:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "找不到項目" }
```

### Usage Example

```http
PUT /api/items/7 HTTP/1.1
Host: localhost:5001
Authorization: Bearer <token>
Content-Type: application/json

{ "name": "更新後的名稱", "description": "更新後的說明", "status": "enabled" }
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "item_id": 7,
  "name": "更新後的名稱",
  "description": "更新後的說明",
  "status": "enabled",
  "created_at": "2026-02-28T10:35:00"
}
```

---

## DELETE /api/items/{item_id}

刪除項目（刪除類範本，需認證）。

### Description

刪除指定項目。此操作無法復原。此端點**需認證**（Bearer token）。

### Operation ID

`items.delete_item`

### Tag

`items`

### Request

**Method**: `DELETE`

**Headers**:

```
Authorization: Bearer {access_token}
```

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|:----:|------|
| `item_id` | integer | Yes | 項目主鍵 |

**Request Model**: None（無 request body）

### Response

**Success (200 OK)** — 刪除成功固定回此物件，`DeleteResult`。

**Response Model（`DeleteResult`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `status` | string | Yes | 固定為 `"deleted"` |

```json
{ "status": "deleted" }
```

**Error (401 Unauthorized)** — 缺少 token 或憑證失效。

**Response Model（`Error`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "未授權或憑證失效" }
```

**Error (404 Not Found)** — 項目不存在。

**Response Model（`Error`）**（同上 schema）:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `error` | string | Yes | 人類可讀錯誤訊息 |

```json
{ "error": "找不到項目" }
```

### Usage Example

```http
DELETE /api/items/7 HTTP/1.1
Host: localhost:5001
Authorization: Bearer <token>
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{ "status": "deleted" }
```

---

## GET /api/health

健康檢查（公開端點範本）。

### Description

回報服務狀態。此端點**公開，無需認證**。

### Operation ID

`health.health`

### Tag

`health`

### Request

**Method**: `GET`

**Request Model**: None（無 request body）

### Response

**Success (200 OK)** — 固定小物件，`HealthResult`。

**Response Model（`HealthResult`）**:

| 欄位 | 型別 | 必填 | 說明 |
|------|------|:----:|------|
| `status` | string | Yes | 固定為 `"ok"` |

```json
{ "status": "ok" }
```

### Usage Example

```http
GET /api/health HTTP/1.1
Host: localhost:5001
```

```http
HTTP/1.1 200 OK
Content-Type: application/json

{ "status": "ok" }
```

---

## 特例：檔案 / 串流端點（非 JSON）

部分端點回傳的不是 JSON（檔案下載、串流、純文字等）。這類端點沒有 JSON Response Model，`### Response` 改述回傳型態與 headers。

> **必須明確標記**：在該 `**Success (...)**` 區塊內寫一行 ``- `Content-Type`：`<media-type>` ``（media type 要用反引號包住，且不含 `json`）。
> 工具只認這一行來判定非 JSON，不會從說明文字猜測；沒有這行就視為 JSON。
> multipart 上傳的檔案欄位，在 Request Model 的「型別」欄寫 `file`。

```markdown
## GET /api/items/export

匯出為 Excel。**特例：回應非 JSON，為 xlsx 位元組，無 JSON Response Model。**

### Response

**Success (200 OK)** — 特例：非 JSON，回 xlsx 位元組。

- `Content-Type`：`application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`。
- `Content-Disposition: attachment; filename=export.xlsx`。
- body 為 xlsx 二進位內容，無 JSON Response Model。
```

常見的非 JSON 類型：

- **串流**：無 `Range` → `200` 整檔；帶 `Range` → `206 Partial Content`，headers 含 `Content-Range` / `Accept-Ranges: bytes` / `Content-Length`。錯誤才回 `{"error":"..."}`（`Error`）。
- **純文字 / 字幕**：`200`，指定對應 `Content-Type`（如 `text/vtt`），body 為檔案內容。
- **xlsx 下載**：`200`，spreadsheet MIME ＋ `Content-Disposition: attachment`。

> 各回應型態的完整分類與狀態碼對照見 [RESPONSE_CONVENTIONS.md](./RESPONSE_CONVENTIONS.md)。
