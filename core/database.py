"""SQLite 数据库操作封装"""
import sqlite3
from pathlib import Path
from bot.config import DB_PATH


def get_conn() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """初始化数据库（建表）"""
    sql_path = Path(__file__).parent.parent / "data" / "init.sql"
    if not sql_path.exists():
        print(f"[WARN] init.sql 不存在: {sql_path}")
        return

    conn = get_conn()
    try:
        sql = sql_path.read_text(encoding="utf-8")
        conn.executescript(sql)
        print("[OK] 数据库初始化完成")
    finally:
        conn.close()


def query_one(sql: str, params: tuple = ()) -> dict | None:
    """查询单条记录"""
    conn = get_conn()
    try:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def query_all(sql: str, params: tuple = ()) -> list[dict]:
    """查询多条记录"""
    conn = get_conn()
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def execute(sql: str, params: tuple = ()):
    """执行写操作"""
    conn = get_conn()
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()
