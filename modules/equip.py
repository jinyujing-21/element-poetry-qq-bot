"""装备继承模块"""
from pathlib import Path
from core.database import query_all

# 装备继承关系图路径
EQUIP_INHERIT_IMAGE = Path(__file__).parent.parent / "templates" / "equip_inherit.jpg"

# 所有装备名称（用于模糊匹配）
ALL_EQUIPS = ["海妖", "黑钢", "焱祭", "骸骨", "劫影", "罗刹", "古藤", "血源", "缚灵"]


def get_equip_inherit_image() -> dict:
    """获取装备继承关系图"""
    if EQUIP_INHERIT_IMAGE.exists():
        return {"type": "image", "content": str(EQUIP_INHERIT_IMAGE)}
    return {"type": "text", "content": "装备继承关系图暂未加载。"}


def query_equip_inherit(equip_name: str) -> dict:
    """查询单个装备的继承关系"""
    # 模糊匹配装备名
    matched_equip = None
    for equip in ALL_EQUIPS:
        if equip in equip_name or equip_name in equip:
            matched_equip = equip
            break

    if not matched_equip:
        return {"type": "text", "content": f"未找到「{equip_name}」相关的装备继承信息。"}

    # 查询该装备作为源装备的继承关系
    inherit_from = query_all(
        "SELECT to_equip, material, level_loss FROM equip_inherit WHERE from_equip = ?",
        (matched_equip,)
    )

    # 查询该装备作为目标装备的继承关系
    inherit_to = query_all(
        "SELECT from_equip, material, level_loss FROM equip_inherit WHERE to_equip = ?",
        (matched_equip,)
    )

    if not inherit_from and not inherit_to:
        return {"type": "text", "content": f"「{matched_equip}」暂无继承关系数据。"}

    lines = [f"【{matched_equip} 继承关系】", ""]

    # 该装备可以继承到哪些装备
    if inherit_from:
        lines.append(f"▼ {matched_equip} 可继承到：")
        for item in inherit_from:
            lines.append(f"  → {item['to_equip']}")
            lines.append(f"    材料：{item['material']}")
            lines.append(f"    等级：{item['level_loss']}")
            lines.append("")

    # 哪些装备可以继承到该装备
    if inherit_to:
        lines.append(f"▲ 可从以下装备继承到 {matched_equip}：")
        for item in inherit_to:
            lines.append(f"  ← {item['from_equip']}")
            lines.append(f"    材料：{item['material']}")
            lines.append(f"    等级：{item['level_loss']}")
            lines.append("")

    lines.append("提示：品质及宝石不会继承，请谨慎选择！")

    return {"type": "text", "content": "\n".join(lines)}
