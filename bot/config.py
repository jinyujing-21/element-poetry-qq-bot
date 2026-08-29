"""配置管理 — 官方QQ机器人"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent.parent

# 数据库路径
DB_PATH = BASE_DIR / "data" / "bot.db"

# 图片输出目录
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# QQ开放平台配置
QQ_APPID = os.getenv("QQ_APPID", "")
QQ_SECRET = os.getenv("QQ_SECRET", "")
QQ_TOKEN = os.getenv("QQ_TOKEN", "")

# Webhook服务器配置
SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8080"))

# 管理员 QQ 列表（用于反馈审核等）
ADMIN_QQS = [int(x) for x in os.getenv("ADMIN_QQS", "").split(",") if x.strip()]
