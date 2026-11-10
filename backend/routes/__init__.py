"""Blueprint 集中註冊。"""
from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/health")
def health():
    """健康檢查。"""
    return jsonify({"status": "ok"})
