"""别名解析引擎 — 所有模块的底层能力"""
from core.database import query_one, query_all


def resolve_alias(raw_input: str, module: str = None) -> dict | None:
    """
    将用户输入解析为标准名称。

    返回: {"standard_name": "xxx", "module": "boss", "target_id": 1}
    未找到返回 None
    """
    text = raw_input.strip()

    # 构建查询条件
    if module:
        sql = """
            SELECT standard_name, module, target_id
            FROM aliases
            WHERE alias = ? AND module = ?
            ORDER BY priority DESC
            LIMIT 1
        """
        result = query_one(sql, (text, module))
    else:
        sql = """
            SELECT standard_name, module, target_id
            FROM aliases
            WHERE alias = ?
            ORDER BY priority DESC
            LIMIT 1
        """
        result = query_one(sql, (text,))

    return result


def add_alias(alias: str, standard_name: str, module: str,
              target_id: int = None, priority: int = 0):
    """添加别名"""
    from core.database import execute
    execute("""
        INSERT OR REPLACE INTO aliases (alias, standard_name, module, target_id, priority)
        VALUES (?, ?, ?, ?, ?)
    """, (alias, standard_name, module, target_id, priority))


def search_fuzzy(keyword: str, module: str = None) -> list[dict]:
    """模糊搜索（用于关键词索引模块）"""
    if module:
        sql = """
            SELECT standard_name, module, target_id
            FROM aliases
            WHERE standard_name LIKE ? AND module = ?
            LIMIT 10
        """
        return query_all(sql, (f"%{keyword}%", module))
    else:
        sql = """
            SELECT standard_name, module, target_id
            FROM aliases
            WHERE standard_name LIKE ? OR alias LIKE ?
            LIMIT 10
        """
        return query_all(sql, (f"%{keyword}%", f"%{keyword}%"))
