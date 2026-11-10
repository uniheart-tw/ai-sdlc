"""Flask app factory。import 本模組不得有副作用。"""
import os

from flask import Flask

import config


def create_app():
    """建立 Flask app：驗證設定、註冊 Blueprint。"""
    # 本機開發才載入 .env；不存在或未安裝 python-dotenv 時略過
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    except ImportError:
        pass
    _reload_config()
    config.validate()

    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_BYTES

    from routes import api_bp
    app.register_blueprint(api_bp)
    return app


def _reload_config():
    """載入 .env 後，環境變數有設定的項目才覆蓋 config（未設定者保留現值，方便測試 patch）。"""
    for name in (*config.REQUIRED_VARS, "SES_REGION", "SES_SENDER"):
        if os.environ.get(name):
            setattr(config, name, os.environ[name])
    if os.environ.get("MAX_UPLOAD_BYTES"):
        config.MAX_UPLOAD_BYTES = int(os.environ["MAX_UPLOAD_BYTES"])


if __name__ == "__main__":
    create_app().run(port=5001)
