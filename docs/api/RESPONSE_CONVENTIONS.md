# 回應型態規範（Response Shape Mapping）

本文件是 **所有 API spec 回應形狀的規範基準**：針對不同類型的端點，定義其回應該有的 JSON 形狀與 HTTP 狀態碼。
撰寫 `docs/api/endpoint/*.md` 的任何回應範例時，一律對照本文件分類。

事實來源為後端的**實際回傳行為**；文件描述現況，不是反過來。

> **本規範與資料庫 schema 無關**：這裡定義的是 API 對外回傳的形狀，與資料庫 schema 彼此獨立。
> 回應欄位名碰巧與 DB 欄位同名（如 `item_id`），是後端直接回傳查詢結果的實作結果，**不是以 DB schema 為事實來源**。
> 每個端點的 Request / Response Model 以 API 實際回傳形狀為準，各自定義於該端點的資源 spec 內。

## 核心慣例

本規範**沒有統一的成功外層**（不存在 `{code, message, data}` 這種包裹）。回應依端點語意分型：

- **成功**：直接回**裸資源** JSON（物件或陣列），依語意用 `200` 或 `201`；少數操作類端點回固定小物件（見下）。
- **錯誤**：統一 `{"error": "<人類可讀訊息>"}` ＋對應 HTTP 狀態碼。
- **刪除**：回 `{"status": "deleted"}`（**不是** `{"ok": true}`，也不是 `204`）。
- **主鍵欄位名**：資源主鍵用具名欄位（`item_id` / `order_id` …），**不是**通用的 `id`。
- **字元**：內容使用 UTF-8。

---

## 成功回應型態

### 1. 列表 → 回陣列

讀取清單類端點直接回 JSON 陣列（無外層）。

- 範例端點：`GET /api/items`、`GET /api/orders`。
- 狀態碼：`200`。

```json
[
  { "item_id": 1, "name": "項目 A", "status": "enabled" },
  { "item_id": 2, "name": "項目 B", "status": "enabled" }
]
```

### 2. 單筆 → 回物件

讀取單一資源直接回資源物件；主鍵用具名欄位（`item_id` 等）。某些 GET 會在物件上**附掛關聯**（例如項目詳情附 `children` 陣列）。

- 範例端點：`GET /api/items/{item_id}`。
- 狀態碼：`200`。

```json
{
  "item_id": 1,
  "name": "項目 A",
  "description": "…",
  "status": "enabled",
  "created_at": "2026-02-28T10:30:00",
  "children": []
}
```

### 3. 建立 → `201` ＋資源（含變體）

POST 建立類回 `201` ＋建立後的資源物件。
部分建立端點回的是固定小物件而非完整資源：

| 端點類型 | 回應 |
|------|------|
| 建立資源（`POST /api/items`） | `201` ＋建立後的資源物件 |
| 建立子資源，只需回主鍵 | `201` `{"<resource>_id": <int>}` |
| 批次匯入 | `201` `{"imported": <int>}` |

```json
{ "child_id": 42 }
```

### 4. 刪除 → `200` `{"status":"deleted"}`

所有資源的 DELETE 一律回此固定物件。

```json
{ "status": "deleted" }
```

### 5. 更新類變體

| 端點類型 | 回應 |
|----------|------|
| 資源 PUT | `200` ＋更新後的資源物件 / 詳情 |
| 子資源 PUT，不回資源 | `200` `{"status": "updated"}` |
| 批次覆寫 | `200` `{"status": "ok", "count": <int>}` |

```json
{ "status": "ok", "count": 3 }
```

### 6. 非同步任務

耗時操作採非同步：

- 提交端點（如 `POST /api/items/{item_id}/generate`）→ `202` `{"task_id": <int>, "status": "pending"}`。
- 輪詢端點（如 `GET /api/tasks/{task_id}`）→ `200` 任務物件
  （`status` 為 `pending` / `processing` / `done` / `failed`；`done` 附 `result`、`failed` 附 `error`）。

```json
{ "task_id": 5, "status": "pending" }
```

### 7. 輔助 / 動作類（非資源）

這些端點回固定小物件，而非資源，欄位依該端點語意定義：

| 端點類型 | 回應 |
|------|------|
| 登入 | `200` `{"token": "<str>", "username": "<str>", "role": "<str>"}` |
| 分析 / 產生文字 | `200` `{"description": "<str>"}` |
| 提交作答 / 計算 | `200` `{"result_id": <int>, "score": <float>}` |

```json
{ "token": "<token>", "username": "admin", "role": "admin" }
```

---

## 錯誤回應型態

錯誤統一為 `{"error": "<訊息>"}` ＋ HTTP 狀態碼（無業務碼欄位、無統一成功外層）：

| HTTP | 情境 | 範例 `error` 訊息 |
|:----:|------|------------------|
| 400 | 參數不合法 / 缺必填 / 檔案格式 / 解析失敗 | `"status 必須為 enabled 或 disabled"`、`"缺少項目名稱"` |
| 401 | 未授權：帳密比對失敗，或 token 缺失 / 無效 / 過期 | `"帳號或密碼錯誤"`、`"未授權或憑證失效"` |
| 404 | 資源不存在 / 路徑型別不符 | `"找不到項目"` |
| 409 | 違反唯一約束 | `"此名稱已存在"` |

> 未捕捉例外走框架預設 500，非 `{"error":...}`。
> 因此 spec 的 500 應標為「未捕捉例外的理論回應」，非既有契約。

### 錯誤範例

```
HTTP/1.1 400 Bad Request

{ "error": "status 必須為 enabled 或 disabled" }
```

```
HTTP/1.1 401 Unauthorized

{ "error": "帳號或密碼錯誤" }
```

```
HTTP/1.1 404 Not Found

{ "error": "找不到項目" }
```

```
HTTP/1.1 409 Conflict

{ "error": "此名稱已存在" }
```

---

## 檔案 / 串流特例（非 JSON）

部分端點回傳的不是 JSON，spec 須標明回傳型態與 headers：

| 端點類型 | 回應型態 |
|----------|----------|
| 串流 | 無 `Range` → `200` 整檔；帶 `Range` → `206`，headers 含 `Content-Range` / `Accept-Ranges: bytes` / `Content-Length` |
| 純文字 / 字幕 | `200`，`Content-Type` 為對應 MIME（如 `text/vtt`），body 為檔案內容 |
| xlsx 下載 | `200`，spreadsheet MIME ＋ `Content-Disposition: attachment; filename=<name>.xlsx` |
| 檔名含中文的下載 | `200`，`Content-Disposition` 含 RFC 5987 `filename*` ＋ ASCII 後備 |

> 上傳類端點為 `multipart/form-data` 請求（屬請求格式，非回應特例）。

---

## 前端錯誤處理建議

前端可用 HTTP client 的回應攔截器，把後端 `{error}` 轉成 `Error(msg)` 拋出，呼叫端以 `try/catch` 統一處理：

```javascript
try {
  const item = await createItem(payload);
  // 成功：item 即後端回的裸資源
} catch (e) {
  showError(e.message);   // e.message 即後端的 error 訊息
}
```

---

## 新增端點時的規範檢查

為 `docs/api/endpoint/<resource>.md` 新增端點時，確認回應符合本文件：

1. 成功回**裸資源**（陣列或物件），不包任何統一外層。
2. 資源主鍵用具名欄位（`item_id` 等），不用通用 `id`。
3. 刪除回 `{"status": "deleted"}`。
4. 錯誤回 `{"error": "<訊息>"}` ＋正確狀態碼（400 / 401 / 404 / 409）。
5. 建立 / 更新 / 任務 / 檔案等變體依上述分類標註。

---

> 📋 對應 API 文件：[docs/api/API_REFERENCE.md](./API_REFERENCE.md)
> 📋 對應端點範本：[docs/api/API_REFERENCE_TEMPLATE.md](./API_REFERENCE_TEMPLATE.md)
> 📋 開發流程：[docs/api/API_FIRST_WORKFLOW.md](./API_FIRST_WORKFLOW.md)
