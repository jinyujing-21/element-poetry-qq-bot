"""纹章模块 — 图片优先"""
from pathlib import Path
from core.database import query_one, query_all
from core.alias import resolve_alias

# 纹章总表图片路径
SEAL_LIST_IMAGE = Path(__file__).parent.parent / "templates" / "seal_list.png"


def query_seal(name: str) -> dict:
    """查询单个纹章"""
    alias_result = resolve_alias(name, "seal")
    if alias_result:
        name = alias_result["standard_name"]

    seal = query_one("SELECT * FROM seal WHERE name = ?", (name,))
    if not seal:
        candidates = query_all(
            "SELECT name FROM seal WHERE name LIKE ? LIMIT 10",
            (f"%{name}%",)
        )
        if not candidates:
            return {"type": "text", "content": f"未找到「{name}」的纹章数据。"}
        if len(candidates) == 1:
            seal = query_one("SELECT * FROM seal WHERE name = ?",
                             (candidates[0]["name"],))
        else:
            lines = [f"找到多个「{name}」："]
            for i, c in enumerate(candidates, 1):
                lines.append(f"{i}. {c['name']}")
            return {"type": "text", "content": "\n".join(lines)}

    lines = [
        f"【{seal['name']}】",
        f"职业：{seal.get('class_name', '-')}",
        f"类型：{seal.get('seal_type', '-')}",
        f"效果：{seal.get('effect', '-')}",
        f"获取方式：{seal.get('how_to_get', '-')}",
    ]

    if seal.get("notes"):
        lines.append(f"备注：{seal['notes']}")

    # 如果有效果图，返回图片
    if seal.get("image_path"):
        return {"type": "image", "content": seal["image_path"]}

    return {"type": "text", "content": "\n".join(lines)}


def get_seal_list(class_name: str = None) -> dict:
    """获取纹章列表（无参数返回总表图片）"""
    # 无参数 → 返回纹章总表图片
    if not class_name:
        if SEAL_LIST_IMAGE.exists():
            return {"type": "image", "content": str(SEAL_LIST_IMAGE)}
        return {"type": "text", "content": "纹章总表图片未找到，请联系管理员。"}

    # 有职业参数 → 按职业筛选
    class_name = class_name.replace("纹章", "").strip()
    seals = query_all(
        "SELECT * FROM seal WHERE class_name = ? ORDER BY name",
        (class_name,)
    )

    if not seals:
        return {"type": "text", "content": f"暂无{class_name}纹章数据。"}

    lines = [f"【{class_name}纹章列表】", ""]
    for i, s in enumerate(seals, 1):
        lines.append(f"{i}. {s['name']}")
    lines.append("")
    lines.append("发送「纹章 名称」查看详情。")

    return {"type": "text", "content": "\n".join(lines)}
