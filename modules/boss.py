"""boss 属性模块 — 图片优先"""
from pathlib import Path
from core.database import query_one, query_all
from core.alias import resolve_alias
from core.renderer import render_boss_table, render_text_card

# boss 属性总表图片
BOSS_IMAGES = [
    Path(__file__).parent.parent / "templates" / "boss_table_1.png",
    Path(__file__).parent.parent / "templates" / "boss_table_2.png",
    Path(__file__).parent.parent / "templates" / "boss_table_3.png",
]


def query_boss(name: str) -> dict:
    """
    查询单个 boss 属性。

    支持：
    - 精确名称：boss属性 岩峰龙-本体
    - 别名：boss属性 岩峰龙
    - 模糊搜索：boss属性 岩峰 → 返回候选列表

    多候选时返回带 _candidates 字段的 dict，供 handler 存储选择状态。
    """
    # 1. 先走别名
    alias_result = resolve_alias(name, "boss")
    if alias_result:
        name = alias_result["standard_name"]

    # 2. 精确查询
    boss = query_one("SELECT * FROM boss WHERE name = ?", (name,))
    if boss:
        return _render_single_boss(boss)

    # 3. 模糊搜索
    candidates = query_all(
        "SELECT name FROM boss WHERE name LIKE ? LIMIT 10",
        (f"%{name}%",)
    )

    if not candidates:
        return {"type": "text", "content": f"未找到「{name}」相关的 boss 数据。"}

    if len(candidates) == 1:
        boss = query_one("SELECT * FROM boss WHERE name = ?", (candidates[0]["name"],))
        return _render_single_boss(boss)

    # 多个候选
    candidate_names = [c["name"] for c in candidates]
    lines = [f"找到多个「{name}」："]
    for i, c in enumerate(candidates, 1):
        lines.append(f"{i}. {c['name']}")
    lines.append("")
    lines.append("发送序号查看详情")

    return {"type": "text", "content": "\n".join(lines), "_candidates": candidate_names}


def get_boss_table_image(filter_keyword: str = None) -> str:
    """获取 boss 属性总表图片"""
    if filter_keyword:
        bosses = query_all(
            "SELECT * FROM boss WHERE name LIKE ? OR dungeon LIKE ? OR attack_element LIKE ?",
            (f"%{filter_keyword}%", f"%{filter_keyword}%", f"%{filter_keyword}%")
        )
    else:
        bosses = query_all("SELECT * FROM boss ORDER BY dungeon, name")

    if not bosses:
        return ""

    return render_boss_table(bosses)


def _render_single_boss(boss: dict) -> dict:
    """渲染单个 boss 信息"""
    lines = [
        f"【{boss['name']}】",
        f"副本：{boss.get('dungeon', '-')}",
        f"难度：{boss.get('difficulty', '-')}",
        f"阶段：{boss.get('stage', '-')}",
        "",
        f"物理减伤：{boss.get('phys_reduce', '-')}",
        f"法术减伤：{boss.get('magic_reduce', '-')}",
        "",
        f"火抗：{boss.get('fire_res', '-')}",
        f"光抗：{boss.get('light_res', '-')}",
        f"雷抗：{boss.get('thunder_res', '-')}",
        f"水抗：{boss.get('water_res', '-')}",
        f"风抗：{boss.get('wind_res', '-')}",
        "",
        f"攻击属性：{boss.get('attack_element', '-')}",
    ]

    if boss.get("is_estimated"):
        lines.append("⚠ 部分数据为推测")
    if boss.get("notes"):
        lines.append(f"备注：{boss['notes']}")
    if boss.get("version_date"):
        lines.append(f"版本：{boss['version_date']}")

    return {"type": "text", "content": "\n".join(lines)}


def get_boss_images() -> list[dict]:
    """返回 boss 属性总表全部图片"""
    result = []
    for img in BOSS_IMAGES:
        if img.exists():
            result.append({"type": "image", "content": str(img)})
    if not result:
        return [{"type": "text", "content": "Boss 属性图片未找到，请联系管理员。"}]
    return result
