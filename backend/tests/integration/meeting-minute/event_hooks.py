"""
event_hooks.py — meeting-minute 資源的請求前處理（由 flask-he 範本生成）

flask_function_wrapper.py 會在「test_env 套用、app import 之後、送出請求之前」呼叫 preprocess()，
根據請求檔（requests/*.json）中的 _hooks 欄位決定要執行哪些 hook。一次執行只載入本檔一次。

呼叫時機（每個請求檔）：
  1. wrapper 先把前面檔案 _capture 存下的變數代入整份請求（{{item_id}} 等）
  2. 呼叫 preprocess(request, env_data)，依 _hooks 順序執行 hook
  3. 套用 stub → 送出請求 → 比對 _expected → _capture → _poll

env_data 內容：
  app           Flask app（已套用 test_env，DB 指向測試位置）
  client        app.test_client()（可用來事前建立資料）
  vars          跨檔共用的變數 dict（_capture 存在這裡；hook 也可以寫入）
  resource      資源名（meeting-minute）
  backend_root  project.backend_root 絕對路徑

設計原則（同 lambda 版）：
  1. 每個 hook 是一個函數：(request, env_data) → request
  2. hook 透過 HOOK_REGISTRY 註冊，請求檔用名稱引用
  3. 請求檔中使用 placeholder（如 "{{item_name}}"）標示動態欄位

── 兩種 hook 的區別 ──
  - 指定值（fixed）：值固定、來自 event_hooks.json。改測試資料只需改該檔一處。
  - 動態值（各資源自行新增）：值需在執行期取得（如鑑權 token、事前建立的資料 ID）。
    鑑權方式因專案而異，flask-he 不內建；請依原始碼與 context.json 的 auth_reference 實作，
    範例見檔尾（auth_admin／auth_user、seed_item）。請求檔不得寫死 token。

使用方式：
  請求檔宣告 "_hooks": ["fixed"]（需要鑑權時再加 "auth_admin" 等），並在需要替換的欄位放 placeholder：
    "json": {"name": "{{item_name}}"}
  event_hooks.json 提供對應值：
    {"item_name": "範例項目"}
"""
import json
from pathlib import Path


# ─── Hook Registry ───

HOOK_REGISTRY: dict[str, callable] = {}


def hook(name: str):
    """裝飾器：將函數註冊為具名 hook"""
    def decorator(func):
        HOOK_REGISTRY[name] = func
        return func
    return decorator


# ─── 共用工具 ───

def _load_hook_config() -> dict:
    """讀取同目錄的 event_hooks.json（集中管理測試用的指定值）。

    檔案不存在或格式錯誤時回空 dict（安全降級，hook 不中斷）。
    """
    config_path = Path(__file__).parent / "event_hooks.json"
    try:
        with open(config_path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _deep_replace(obj, mapping: dict):
    """遞迴把任意巢狀結構（dict / list / str）中的 {{key}} placeholder 換成 mapping[key]。

    - 整串即 placeholder（如 "{{item_id}}"）→ 保留 mapping 值的原型別（int 仍是 int）
    - 字串內嵌（如 "/api/items/{{item_id}}"）→ 轉成字串內嵌
    mapping 無對應 key 的 placeholder 原樣保留。
    """
    if isinstance(obj, dict):
        return {k: _deep_replace(v, mapping) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_deep_replace(v, mapping) for v in obj]
    if isinstance(obj, str):
        stripped = obj.strip()
        if stripped.startswith("{{") and stripped.endswith("}}") and stripped.count("{{") == 1:
            key = stripped[2:-2]
            if key in mapping and mapping[key] is not None:
                return mapping[key]
        for key, val in mapping.items():
            if val is None:
                continue
            obj = obj.replace("{{" + key + "}}", str(val))
        return obj
    return obj


# ─── Hook 實作 ───

@hook("fixed")
def fixed(request: dict, env_data: dict) -> dict:
    """把請求中的 {{key}} placeholder 換成 event_hooks.json 對應的指定值。

    event_hooks.json 裡的「每一個 key」都是一個 placeholder 來源；要新增可替換欄位，
    只需在 event_hooks.json 加 key、並在請求檔放 {{key}}，不必改本檔。
    placeholder 可出現在 path、headers、query、json、form、_expected 等任何位置。
    """
    config = _load_hook_config()
    mapping = {k: v for k, v in config.items() if v is not None}
    if not mapping:
        print("  ⚠️  [fixed] event_hooks.json 無可用的指定值，略過")
        return request
    request = _deep_replace(request, mapping)
    print(f"  🔑 [fixed] 套用 event_hooks.json: {', '.join(mapping.keys())}")
    return request


# ─── 動態 hook 範例（依專案需求啟用或改寫，非必要可刪除本區塊）───
#
# 鑑權：依專案的鑑權實作（context.json 的 auth_reference）取得 token，填進 Authorization header。
# 下方 auth_service.issue_token(...) 是示意，請換成專案實際的簽發方式與角色。
# 401 情境的請求檔不要掛這兩個 hook。
#
# @hook("auth_admin")
# def auth_admin(request: dict, env_data: dict) -> dict:
#     from services import auth_service
#     username = _load_hook_config().get("admin_username", "test-admin")   # 於 event_hooks.json 設定
#     token = auth_service.issue_token(username, "admin")
#     request.setdefault("headers", {})["Authorization"] = f"Bearer {token}"
#     return request
#
#
# @hook("auth_user")
# def auth_user(request: dict, env_data: dict) -> dict:
#     from services import auth_service
#     username = _load_hook_config().get("user_username", "test-user")
#     token = auth_service.issue_token(username, "user")
#     request.setdefault("headers", {})["Authorization"] = f"Bearer {token}"
#     return request
#
#
# 事前建立資料：用 env_data["client"] 打 API 建立，ID 存進 env_data["vars"]，後續檔案用 {{seed_item_id}}。
#
# @hook("seed_item")
# def seed_item(request: dict, env_data: dict) -> dict:
#     if "seed_item_id" not in env_data["vars"]:
#         resp = env_data["client"].post("/api/items", json={"name": "seed"})   # 需要鑑權時加 headers
#         env_data["vars"]["seed_item_id"] = resp.get_json()["item_id"]
#     return _deep_replace(request, {"seed_item_id": env_data["vars"]["seed_item_id"]})


# ─── 公開 API（flask_function_wrapper.py 呼叫）───

def preprocess(request: dict, env_data: dict) -> dict:
    """依序執行 request._hooks 中指定的 hooks。"""
    hooks_to_run = request.get("_hooks", [])
    for hook_name in hooks_to_run:
        if hook_name in HOOK_REGISTRY:
            request = HOOK_REGISTRY[hook_name](request, env_data)
        else:
            print(f"  ⚠️  Unknown hook: {hook_name} (available: {list(HOOK_REGISTRY.keys())})")
    return request
