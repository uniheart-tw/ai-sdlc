"""設定集中處：只從環境變數讀取。

import 本模組不得有副作用（不讀檔、不驗證）；必要變數的驗證在 create_app() 時呼叫 validate()。
"""
import os

# 必要環境變數，缺少時 validate() 會列出名稱
REQUIRED_VARS = ("BEDROCK_REGION", "BEDROCK_MODEL_ID")

BEDROCK_REGION = os.environ.get("BEDROCK_REGION", "")
BEDROCK_MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "")
SES_REGION = os.environ.get("SES_REGION", "ap-southeast-1")
SES_SENDER = os.environ.get("SES_SENDER", "yehchitsai@uniheart.com.tw")
MAX_UPLOAD_BYTES = int(os.environ.get("MAX_UPLOAD_BYTES", str(1024 * 1024)))


class ConfigError(RuntimeError):
    """必要環境變數缺少時拋出。"""


def validate():
    """檢查必要環境變數（以模組目前的屬性值為準，方便測試覆寫）。"""
    missing = [name for name in REQUIRED_VARS if not globals().get(name)]
    if missing:
        raise ConfigError("缺少必要環境變數：" + ", ".join(missing))
