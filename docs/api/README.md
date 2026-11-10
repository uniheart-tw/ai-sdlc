# API 定義

本目錄集中維護 ai-sdlc 的 **API 定義**，作為前後端共用規格的單一事實來源（SSOT）。
採 **API-First**：手寫端點文件 → 合併 → 產生 OpenAPI 規範 → 驗證 → 契約測試。事實來源為 `backend/routes/*.py` 的實際行為。

## 目錄內容

| 檔案 / 目錄 | 性質 | 說明 |
|------------|------|------|
| [`README.md`](./README.md) | 手寫 | 本檔。全域資訊：目錄導覽、分檔規則、共通約定、撰寫規範。（本檔不再是合併來源；合併只收 `endpoint/*.md`。） |
| [`endpoint/`](./endpoint/) | 手寫 | 各路徑群組的端點文件（一群組一檔），為合併與 OpenAPI 的**唯一手寫來源**。見下方「分檔規則」。 |
| [`endpoint/metadata.yaml`](./endpoint/metadata.yaml) | 手寫 | 整個 repo 共用的 API 名稱、版本、伺服器位址、認證方式（`securitySchemes`），由 `build-reference.py` 讀入並寫成 `API_REFERENCE.md` 的檔首 front matter；不是端點文件，端點內容不會被合併。 |
| [`API_REFERENCE_TEMPLATE.md`](./API_REFERENCE_TEMPLATE.md) | 手寫 | 單一端點撰寫範本（GET/POST/PUT/DELETE 與檔案 / 串流特例），示範區塊、順序與 Request/Response Model 格式。 |
| [`RESPONSE_CONVENTIONS.md`](./RESPONSE_CONVENTIONS.md) | 手寫 | 回應型態規範基準：成功回裸資源、錯誤 `{"error":...}` ＋狀態碼、刪除 `{"status":"deleted"}` 等慣例與狀態碼對照。 |
| [`API_FIRST_WORKFLOW.md`](./API_FIRST_WORKFLOW.md) | 手寫 | API-First 開發流程說明：工具鏈、三階段步驟、契約測試方式。 |
| `API_REFERENCE.md` | **生成物** | 由 `ai-dev-tools/scripts/apispec/build-reference.py` 合併 `endpoint/*.md` 而成的單一參考（檔首為自動產生的「端點總覽」彙整表），**勿手動編輯**（下次合併會覆蓋）。 |
| `openapi.yaml` | **生成物** | 由 `md-to-openapi.py` 從 `API_REFERENCE.md` 產生的 OpenAPI 3.0 規範，**勿手動編輯**。契約測試以此為輸入。 |

> 要修改 API 內容，一律改 `endpoint/*.md` 後重新執行工具鏈；兩個生成物不要直接編輯。
> 合併來源只收 `endpoint/*.md`（不含本 README 與範本 / 流程 / 回應慣例說明），故 `API_REFERENCE.md` 不會混入非 API 規格內容。

## 分檔規則

端點文件依**路徑群組**分檔，一個路徑群組一份文件，置於 [`endpoint/`](./endpoint/) 目錄，檔名對應 `/api/{group}` 的 `{group}`（例如 `/api/videos/*` → `endpoint/videos.md`）。

| 檔案 | 路徑群組 | 端點數 |
|------|----------|:----:|
| [`endpoint/auth.md`](./endpoint/auth.md) | `/api/auth/*` | 1 |
| [`endpoint/videos.md`](./endpoint/videos.md) | `/api/videos/*` | 12 |
| [`endpoint/assessments.md`](./endpoint/assessments.md) | `/api/assessments/*` | 15 |
| [`endpoint/courses.md`](./endpoint/courses.md) | `/api/courses/*` | 5 |
| [`endpoint/reports.md`](./endpoint/reports.md) | `/api/reports/*` | 2 |
| [`endpoint/taxonomies.md`](./endpoint/taxonomies.md) | `/api/taxonomies/*` | 4 |

> `GET /api/health` 定義於 `backend/app.py`（非 Blueprint），不屬於任何 Blueprint 路徑群組。

## 共通約定

- 所有 API 前綴為 `/api`，請求與回應皆為 JSON（檔案 / 串流端點除外）。
- 回應統一格式與狀態碼：見 [RESPONSE_CONVENTIONS.md](./RESPONSE_CONVENTIONS.md)。

## 撰寫規範

- 單一端點的撰寫格式（區塊、順序、Request/Response Model、Tag 標籤）：見 [API_REFERENCE_TEMPLATE.md](./API_REFERENCE_TEMPLATE.md)。
- **每個端點必須標註 `### Tag`**（資源群組名），用於分類與 OpenAPI 規範生成。
- 回應型態分類：見 [RESPONSE_CONVENTIONS.md](./RESPONSE_CONVENTIONS.md)。
- 整體開發流程（合併 → OpenAPI → 契約測試）：見 [API_FIRST_WORKFLOW.md](./API_FIRST_WORKFLOW.md)。

## 操作指令

工具鏈位於 `ai-dev-tools/scripts/apispec/`，於 repo 根目錄啟用 venv 後執行：

```bash
source .venv/bin/activate
T=ai-dev-tools/scripts/apispec

# 1. 合併 endpoint/*.md（含自動產生的端點總覽彙整表）→ docs/api/API_REFERENCE.md
python $T/build-reference.py

# 2. 產生 OpenAPI 規範 → docs/api/openapi.yaml
python $T/md-to-openapi.py

# 3. 依 openapi-validator-rules.yaml 驗證規範
python $T/validate-openapi.py
```

契約測試（打本機 Flask，驗證實作是否符合 `openapi.yaml`）：

```bash
# 1. 啟動本機 Flask（埠號依本機設定，預設 5001）
cd backend
PORT=5001 python app.py

# 2. 另開終端機，對本機 Flask 跑契約測試（URL 指向實際埠號）
schemathesis run docs/api/openapi.yaml --url http://localhost:5001 --include-method GET
```

> 新增 / 修改端點後，依序重跑步驟 1–3 重新產生規範，再跑契約測試。詳細流程與注意事項見 [API_FIRST_WORKFLOW.md](./API_FIRST_WORKFLOW.md)。
