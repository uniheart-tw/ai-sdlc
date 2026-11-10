# AI Agent 開發指引
> 供 AI agent 閱讀的精簡指引：只列**技術、結構與規則**，不描述功能。
> 功能需求、API 規格、外部服務清單都放在各自的目錄（見「功能與規格在哪裡」），以那裡為準，勿憑本檔臆測。

## 技術棧
| 層 | 技術 |
|----|------|
| 後端 | Python 3.13、Flask 3（app factory `create_app()` + Blueprint） |
| 前端 | React 18 + Vite 5 + Axios（純 JSX，函式元件 + Hooks） |
| API 契約 | API-First：手寫 Markdown 端點文件 → OpenAPI 3.0（生成物）；前後端共用 |
| 測試 | 後端 pytest（Flask 內建 `test_client`，測試由 flask-he 生成）；前端 Vitest + React Testing Library |
| 環境 | 後端：uv，venv 建在 repo 根目錄 `.venv`，相依列在根目錄 `requirements.txt`；前端：npm，相依列在 `frontend/package.json` |
| 開發伺服器 | 後端 Flask `:5001`；前端 Vite `:5173`，`/api` 由 Vite proxy 轉到後端 |
| 設定 | 環境變數（本機 `.env`，範本 `.env.example`），由 `backend/config.py` 集中讀取 |

## 目錄結構
```
.
├── agent.md                  ← 本檔
├── requirements.txt          ← 後端相依
├── .env.example              ← 環境變數範本（實際值放 .env，不進版控）
├── backend/
│   ├── app.py                ← create_app()；import 時不得有副作用
│   ├── config.py             ← 設定集中處（讀環境變數）
│   ├── routes/               ← Blueprint：HTTP 與輸入驗證
│   ├── services/             ← 業務邏輯、外部服務的包裝
│   ├── tests/                ← unit/、integration/、data/（測試資料）
│   └── flask-he-config.yaml  ← 測試生成設定（含外部服務 stub 清單）
├── frontend/
│   ├── package.json          ← 前端相依與 npm scripts
│   ├── vite.config.js        ← 開發伺服器、/api proxy、Vitest 設定
│   └── src/
│       ├── api/              ← 所有 HTTP 呼叫集中於此（Axios client）
│       ├── components/       ← 共用元件
│       ├── pages/            ← 頁面
│       └── test/             ← 測試共用設定
├── docs/api/                 ← API-First 文件（流程、回應慣例、端點範本、endpoint/）
├── .kiro/steering/           ← 專案規範（hook 會注入）
├── .github/                  ← Issue / PR 範本
├── temp/user_reps/           ← 原始需求（輸入）
└── ai-dev-tools/             ← 開發工具（獨立 repo，已 gitignore）
```

## 功能與規格在哪裡
| 要知道什麼 | 去哪裡看 |
|-----------|---------|
| 這個 repo 要做什麼（原始需求） | `temp/user_reps/*.md` |
| 整理後的需求規格 | `temp/user_reps_report/`（hook 產出） |
| 目前要實作的任務 | 對應的 GitHub Issue |
| API 端點規格（唯一事實來源） | `docs/api/endpoint/*.md` |
| API 撰寫格式與回應慣例 | `docs/api/API_REFERENCE_TEMPLATE.md`、`docs/api/RESPONSE_CONVENTIONS.md` |
| API-First 開發流程 | `docs/api/API_FIRST_WORKFLOW.md` |
| 有哪些外部服務、測試時要 stub 什麼 | `backend/flask-he-config.yaml` 的 `external_stubs` |
| 測試工具怎麼用 | `ai-dev-tools/harness-engineering/flask-he/README.md`、`ai-dev-tools/scripts/flask/README.md` |
| 需要哪些環境變數 | `.env.example` |
| 哪些檔案不進版控 | `.gitignore` |

## 前端分層
`pages/` → `components/` → `api/` → 後端 `/api/*`。
- 元件與頁面不得直接呼叫 Axios / `fetch`；HTTP 一律經 `src/api/`，請求與回應形狀以 `docs/api/endpoint/*.md` 為準。
- API 路徑一律寫相對路徑 `/api/...`，由 Vite proxy 轉送；不要寫死後端主機與埠號。

## 後端分層（依賴單向）
`routes/` → `services/` → 儲存層 / 外部服務。
- `routes/` 保持薄：只做 HTTP 解析、輸入驗證、呼叫 service、組回應。
- 業務邏輯放 `services/`。
- **每個外部服務（郵件、第三方 API、雲端服務等）只透過 `services/` 內單一模組呼叫**；routes 與其他 service 不得直接使用其底層函式庫。這樣測試才能整塊替換。
- 新增或修改端點時，先改 `docs/api/endpoint/*.md`，再改後端與前端（API-First）；前後端成對更新。

## 絕對不能踩的雷
1. **機密不進程式碼 / 版控**：帳密、金鑰一律讀環境變數；新增變數時同步更新 `.env.example`（只放範例值）。
2. **測試不得呼叫真實外部服務**：外部服務一律 stub，清單維護在 `backend/flask-he-config.yaml` 的 `external_stubs`；新增外部服務時一併登記。
3. **個資不進 log、不進版控**：範例與測試資料用假資料（email 用 `@example.com`）。
4. **執行期產生的資料不進版控**：上傳檔、資料庫檔等放在 `.gitignore` 已排除的目錄。
5. **`ai-dev-tools/` 勿修改、勿把其內容寫進文件或 commit**：它是獨立的開發工具 repo，不屬於本專案。
6. **生成物勿手動編輯**：`docs/api/API_REFERENCE.md`、`docs/api/openapi.yaml` 由工具產生，要改就改 `docs/api/endpoint/*.md` 後重新產生。

## 開發慣例
- 文件 / 註解使用繁體中文。
- Commit 用 Conventional Commits（scope：`backend` / `frontend` / `docs`）。
- 動手前先讀相關既有檔，沿用既有風格與相依；勿擅自引入新框架。
- 新增套件：後端寫進 `requirements.txt` 並固定版本；前端用 `npm install`，`package-lock.json` 一併提交。

## 測試
**後端**：測試由 flask-he 生成、驗證、出報告；**使用 `ai-dev-tools/` 的測試工具前，先讀對應 README**，勿憑本檔臆測參數。

| 要查什麼 | 文件 |
|---------|------|
| 依情境的指令速查（生成／驗證／報告／清除）、流程、產出 | `ai-dev-tools/harness-engineering/flask-he/README.md` |
| 每支 script 的完整參數、讀寫檔案、exit code、15 項 check、stub 規則 | `ai-dev-tools/scripts/flask/README.md` |
| 本專案的測試設定（對象範圍、門檻、外部服務 stub、測試環境） | `backend/flask-he-config.yaml` |

| 類型 | 對象 | 測試檔位置 | 執行方式 |
|------|------|-----------|---------|
| 單元 | 模組（`unit.source_include` 範圍） | `backend/tests/unit/` | pytest（經工具執行，見下） |
| 整合 | 資源（`/api/<resource>/...`） | `backend/tests/integration/<resource>/requests/*.json` | `flask_function_wrapper.py`（**不是 pytest**） |

- 測試檔一律由 `run.sh` 生成，不要在 `backend/tests/` 下另外手寫。
- 所有指令在 repo 根目錄、`source .venv/bin/activate` 後執行；工具套件另裝 `ai-dev-tools/scripts/flask/requirements.txt`。
- 常用指令（`run.sh` = `bash ai-dev-tools/harness-engineering/flask-he/run.sh`，其餘為 `python ai-dev-tools/scripts/flask/<script>`）：

| 情境 | 指令 |
|------|------|
| 檢查設定 | `read_config.py` |
| 列出對象與狀態 | `run.sh --list --kind unit\|integration` |
| 生成測試 | `run.sh <module> --kind unit`、`run.sh <resource> --kind integration` |
| 驗證測試品質 | `validate_tests.py <target> --kind unit\|integration`（全部用 `--all`） |
| 執行測試並出報告 | `generate_test_report.py --kind unit\|integration --with-report --fail-on-error` |
| 只執行測試（CI） | `generate_test_report.py --kind unit\|integration --fail-on-error` |
| 單獨跑整合請求檔 | `flask_function_wrapper.py <resource> --all --stub` |

- **執行測試優先用 `generate_test_report.py`／`validate_tests.py`**：它們會載入 test_env plugin，把測試資料指到 repo 外。直接跑 `pytest` 不會載入這層隔離，也不會執行整合測試。
- **手動跑 wrapper 一律加 `--stub`**：沒加時 `external_stubs.patch` 不攔截，會實際呼叫外部服務。validate／report 內部已固定帶 `--stub`。
- 驗證與報告都要跑時，先 `validate_tests.py` 再 `generate_test_report.py`。

**前端**
- Vitest + React Testing Library（jsdom）；測試檔與被測檔放在一起，命名 `*.test.jsx` / `*.test.js`。
- 測試中 mock `src/api/`，不打真實後端。
- 執行：`cd frontend && npm run test:run`（`npm test` 是 watch 模式）
