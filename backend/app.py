"""Flask app factory。import 時不得有副作用，只在 __main__ 建立 app。"""
from flask import Flask, jsonify

import config


def create_app() -> Flask:
    app = Flask(__name__)
    # 請求本體上限略大於檔案上限（multipart 開銷），由路由再精確檢查檔案大小
    app.config["MAX_CONTENT_LENGTH"] = config.MAX_UPLOAD_BYTES + 64 * 1024

    from routes.meeting_minute import meeting_minute_bp

    app.register_blueprint(meeting_minute_bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(413)
    def too_large(_exc):
        return jsonify({"error": "檔案超過大小上限"}), 400

    return app


if __name__ == "__main__":
    create_app().run(port=5001)
