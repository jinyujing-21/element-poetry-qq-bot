"""关键词索引模块"""
from core.alias import search_fuzzy
from core.database import query_all, execute


def search_keyword(keyword: str) -> dict:
    """全文搜索"""
    # 记录查询日志
    execute(
        "INSERT INTO query_logs (raw_input, module, hit) VALUES (?, ?, ?)",
        (keyword, "search", 0)
    )

    # 搜索别名表
    results = search_fuzzy(keyword)

    if not results:
        return {
            "type": "text",
            "content": f"未找到「{keyword}」的相关结果。\n发送「反馈 {keyword}数据缺失」可提交补充。"
        }

    # 更新命中状态
    execute(
        "UPDATE query_logs SET hit = 1 WHERE raw_input = ? ORDER BY id DESC LIMIT 1",
        (keyword,)
    )

    lines = [f"搜索「{keyword}」结果：", ""]
    module_names = {
        "boss": "Boss属性",
        "dungeon": "副本",
        "seal": "纹章",
        "forge": "锻造",
        "magic": "魔素",
    }

    for r in results:
        mod = module_names.get(r["module"], r["module"])
        lines.append(f"[{mod}] {r['standard_name']}")

    return {"type": "text", "content": "\n".join(lines)}
