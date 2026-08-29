"""锻造模块 — 查询 + 材料计算"""
from core.database import query_one, query_all
from core.alias import resolve_alias
from core.calculator import calc_forge


def query_forge(name: str) -> dict:
    """查询锻造装备信息"""
    alias_result = resolve_alias(name, "forge")
    if alias_result:
        name = alias_result["standard_name"]

    equip = query_one("SELECT * FROM forge_equipment WHERE name = ?", (name,))
    if not equip:
        candidates = query_all(
            "SELECT name FROM forge_equipment WHERE name LIKE ? LIMIT 10",
            (f"%{name}%",)
        )
        if not candidates:
            return {"type": "text", "content": f"未找到「{name}」的锻造信息。"}
        if len(candidates) == 1:
            equip = query_one("SELECT * FROM forge_equipment WHERE name = ?",
                              (candidates[0]["name"],))
        else:
            lines = [f"找到多个「{name}」："]
            for i, c in enumerate(candidates, 1):
                lines.append(f"{i}. {c['name']}")
            return {"type": "text", "content": "\n".join(lines)}

    # 查询配方
    recipes = query_all(
        "SELECT material_name, material_quantity, is_prerequisite "
        "FROM forge_recipe WHERE target_item = ?",
        (name,)
    )

    lines = [
        f"【{equip['name']}】",
        f"类型：{equip.get('equip_type', '-')}",
        f"职业限制：{equip.get('class_limit', '-')}",
        f"阶段：{equip.get('stage', '-')}",
        "",
        "锻造材料：",
    ]

    if recipes:
        for r in recipes:
            prefix = "[前置] " if r["is_prerequisite"] else ""
            lines.append(f"  {prefix}{r['material_name']} x{r['material_quantity']}")
    else:
        lines.append("  暂无配方数据")

    if equip.get("forge_location"):
        lines.append(f"\n锻造地点：{equip['forge_location']}")
    if equip.get("forge_npc"):
        lines.append(f"锻造 NPC：{equip['forge_npc']}")
    if equip.get("notes"):
        lines.append(f"备注：{equip['notes']}")

    lines.append("")
    lines.append(f"发送「计算 {equip['name']}」查看总材料计算。")

    return {"type": "text", "content": "\n".join(lines)}


def query_recipe(name: str) -> dict:
    """查询锻造配方详情"""
    recipes = query_all(
        "SELECT * FROM forge_recipe WHERE target_item = ?", (name,)
    )
    if not recipes:
        return {"type": "text", "content": f"未找到「{name}」的锻造配方。"}

    lines = [f"【{name} · 锻造配方】", ""]
    for r in recipes:
        prefix = "[前置装备] " if r["is_prerequisite"] else ""
        lines.append(f"{prefix}{r['material_name']} x{r['material_quantity']}")
        if r["gold_cost"]:
            lines.append(f"  金币：{r['gold_cost']}")
        if r["magic_cost"]:
            lines.append(f"  魔素：{r['magic_cost']}")

    return {"type": "text", "content": "\n".join(lines)}


def calc_forge_materials(args: str) -> dict:
    """计算锻造总材料"""
    # 解析参数：支持 "天灾主手"、"天灾主手*2"、"天灾主手+天灾副手"
    items = _parse_calc_args(args)

    if not items:
        return {"type": "text", "content": "请指定装备名，如：计算 天灾主手"}

    results = []
    for item_name, qty in items:
        result = calc_forge(item_name, qty)
        results.append(result)

    # 合并结果
    lines = []
    for r in results:
        lines.append(f"【{r['target']} x{r['quantity']}】")

        if r["materials"]:
            lines.append("需要材料：")
            for m in r["materials"]:
                lines.append(f"  {m['name']} x{m['quantity']}")
        else:
            lines.append("暂无配方数据")

        if r["prerequisites"]:
            lines.append("前置装备：")
            for p in r["prerequisites"]:
                lines.append(f"  {p['name']} x{p['quantity']}")

        if r["missing"]:
            lines.append("")
            lines.append("还缺：")
            for m in r["missing"]:
                lines.append(f"  {m['name']} x{m['quantity']}")

        lines.append("")

    return {"type": "text", "content": "\n".join(lines)}


def _parse_calc_args(args: str) -> list[tuple[str, int]]:
    """
    解析计算参数。

    支持格式：
    - 天灾主手
    - 天灾主手*2
    - 天灾主手+天灾副手
    - 天灾主手*2+天灾副手
    """
    items = []
    parts = args.replace("，", "+").replace(",", "+").split("+")

    for part in parts:
        part = part.strip()
        if not part:
            continue

        if "*" in part:
            name, qty_str = part.rsplit("*", 1)
            try:
                qty = int(qty_str.strip())
            except ValueError:
                qty = 1
        else:
            name = part
            qty = 1

        items.append((name.strip(), qty))

    return items
