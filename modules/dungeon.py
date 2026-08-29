"""副本模块 — 进本条件 + 自强战力推荐"""
from pathlib import Path
from core.database import query_one, query_all
from core.alias import resolve_alias

# 自强战力推荐总表图片路径
SOLO_IMAGE = Path(__file__).parent.parent / "templates" / "dungeon_solo.png"


def query_entry(name: str) -> dict:
    """查询进本条件"""
    # 别名解析
    alias_result = resolve_alias(name, "dungeon")
    if alias_result:
        name = alias_result["standard_name"]

    # 精确查询
    entry = query_one("SELECT * FROM dungeon_entry WHERE name = ?", (name,))
    if not entry:
        # 模糊搜索
        candidates = query_all(
            "SELECT name FROM dungeon_entry WHERE name LIKE ? LIMIT 10",
            (f"%{name}%",)
        )
        if not candidates:
            return {"type": "text", "content": f"未找到「{name}」的进本条件数据。"}
        if len(candidates) == 1:
            entry = query_one("SELECT * FROM dungeon_entry WHERE name = ?",
                              (candidates[0]["name"],))
        else:
            lines = [f"找到多个「{name}」："]
            for i, c in enumerate(candidates, 1):
                lines.append(f"{i}. {c['name']}")
            return {"type": "text", "content": "\n".join(lines)}

    lines = [
        f"【{entry['name']} · 进本条件】",
        f"副本类型：{entry.get('dungeon_type', '-')}",
        f"难度：{entry.get('difficulty', '-')}",
        "",
        "最低门槛：",
        f"  C：{entry.get('min_combat_c', '-')}  奶：{entry.get('min_combat_n', '-')}  T：{entry.get('min_combat_t', '-')}",
        "",
        f"最低等级：{entry.get('min_level', '-')}",
        f"推荐队伍：{entry.get('recommend_party_size', '-')}",
    ]

    if entry.get("class_requirement"):
        lines.append(f"职业要求：{entry['class_requirement']}")
    if entry.get("must_mechanic"):
        lines.append(f"必备机制：{entry['must_mechanic']}")
    if entry.get("must_item"):
        lines.append(f"必备道具：{entry['must_item']}")
    if entry.get("prerequisite"):
        lines.append(f"前置副本：{entry['prerequisite']}")
    if entry.get("notes"):
        lines.append(f"备注：{entry['notes']}")

    lines.append("")
    lines.append(f"发送「自强 {entry['name']}」查看自强推荐。")

    return {"type": "text", "content": "\n".join(lines)}


def query_solo(name: str = None) -> dict:
    """查询自强战力推荐（无参数返回总表图片）"""
    # 无参数 → 返回自强战力推荐总表图片
    if not name:
        if SOLO_IMAGE.exists():
            return {"type": "image", "content": str(SOLO_IMAGE)}
        return {"type": "text", "content": "自强战力推荐图片未找到，请联系管理员。"}

    alias_result = resolve_alias(name, "dungeon")
    if alias_result:
        name = alias_result["standard_name"]

    solo = query_one("SELECT * FROM dungeon_solo WHERE dungeon_name = ?", (name,))
    if not solo:
        candidates = query_all(
            "SELECT dungeon_name FROM dungeon_solo WHERE dungeon_name LIKE ? LIMIT 10",
            (f"%{name}%",)
        )
        if not candidates:
            return {"type": "text", "content": f"未找到「{name}」的自强推荐数据。"}
        if len(candidates) == 1:
            solo = query_one("SELECT * FROM dungeon_solo WHERE dungeon_name = ?",
                             (candidates[0]["dungeon_name"],))
        else:
            lines = [f"找到多个「{name}」："]
            for i, c in enumerate(candidates, 1):
                lines.append(f"{i}. {c['dungeon_name']}")
            return {"type": "text", "content": "\n".join(lines)}

    lines = [
        f"【{solo['dungeon_name']} · 自强推荐】",
        f"难度：{solo.get('difficulty', '-')}",
        "",
        f"C 推荐：{solo.get('recommend_c', '-')}",
        f"N 推荐：{solo.get('recommend_n', '-')}",
        f"T 推荐：{solo.get('recommend_t', '-')}",
    ]

    if solo.get("class_notes"):
        lines.append(f"职业备注：{solo['class_notes']}")
    if solo.get("mechanic_notes"):
        lines.append(f"机制备注：{solo['mechanic_notes']}")
    if solo.get("contributor"):
        lines.append(f"贡献者：{solo['contributor']}")
    if solo.get("version_date"):
        lines.append(f"版本：{solo['version_date']}")

    lines.append("")
    lines.append("说明：数据为自强参考，实际受职业、机制熟练度、队伍配置影响。")

    return {"type": "text", "content": "\n".join(lines)}
