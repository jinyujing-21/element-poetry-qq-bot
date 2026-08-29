"""纹章兑换计算模块"""
import re
from pathlib import Path
from typing import Optional

# 纹章品质（从小到大）
QUALITY_ORDER = ["普通", "稀有", "极品", "史诗", "传奇"]

# 特殊纹章（仅可兑换，4进1进阶）
SPECIAL_SEALS = {"奇袭", "存续", "庇护", "流转"}

# 特殊纹章的普通品质基础兑换材料
SPECIAL_BASE_MATERIALS: dict[str, dict[str, int]] = {
    "奇袭": {"神圣的意志": 1, "圣光之影": 2, "魔素[普通]": 2, "元素碎片": 5},
    "存续": {"魔素[普通]": 1, "元素碎片": 3, "圣光的信仰": 3, "光元素": 4},
    "流转": {"魂之力": 2, "魔素[普通]": 2, "元素碎片": 5},
    "庇护": {"闪耀史莱姆钱币": 2, "魔素[普通]": 2, "元素碎片": 5},
}

# 普通纹章的基础材料（8进1进阶）
# TODO: 需要用户补充每个普通纹章的基础材料
NORMAL_SEAL_MATERIALS: dict[str, dict[str, int]] = {
    "怨恨": {"魔剑碎片": 2, "魔素[普通]": 2, "元素碎片": 5},
    "暴走": {"魔素[普通]": 2, "元素碎片": 5, "熔岩硬币[小]": 10},
    "汲取": {},  # 待补充
    "神恩": {"魔素[普通]": 1, "元素碎片": 2, "熔岩硬币[小]": 10},
    "完璧": {"魔素[普通]": 2, "元素碎片": 5, "古森林钱币": 10},
    "战争热诚": {"魔素[普通]": 1, "闪耀史莱姆钱币": 2, "元素碎片": 3},
}

# 合并所有纹章数据
ALL_SEALS = {**SPECIAL_BASE_MATERIALS, **NORMAL_SEAL_MATERIALS}

# 引导图片路径
CALC_GUIDE_IMAGE = Path(__file__).parent.parent / "templates" / "seal_calc_guide.jpg"


def get_calc_guide() -> dict:
    """返回纹章计算使用说明图片"""
    if CALC_GUIDE_IMAGE.exists():
        return {"type": "image", "content": str(CALC_GUIDE_IMAGE)}
    return {"type": "text", "content": "纹章计算说明图片未找到，请联系管理员。"}


def _quality_index(q: str) -> int:
    """获取品质索引，不存在返回 -1"""
    try:
        return QUALITY_ORDER.index(q)
    except ValueError:
        return -1


def _calc_normal_equivalent(seal_name: str, quality: str) -> int:
    """
    计算一个指定品质纹章需要的普通纹章等价数量。

    普通纹章：普通→稀有→极品→史诗 8进1，史诗→传奇 4进1
      1史诗 = 512 普通, 1传奇 = 2048 普通
    特殊纹章：普通→稀有→极品→史诗 4进1，史诗→传奇 2进1
      1史诗 = 128 普通, 1传奇 = 256 普通
    """
    q_idx = _quality_index(quality)
    if q_idx <= 0:
        return 1

    is_special = seal_name in SPECIAL_SEALS
    total = 1
    for i in range(q_idx):
        if is_special:
            if i == 3:  # 史诗→传奇 2进1
                total *= 2
            else:       # 普通→稀有→极品→史诗 4进1
                total *= 4
        elif i == 3:    # 普通纹章 史诗→传奇 4进1
            total *= 4
        else:           # 普通纹章 其余 8进1
            total *= 8

    # 特殊纹章特殊修正：1史诗 = 128 普通（非 64）
    if is_special and quality == "史诗":
        total = 128
    elif is_special and quality == "传奇":
        total = 256
    return total


def _calc_materials_for_target(seal_name: str, target_quality: str, owned: dict[str, int] = None) -> dict[str, int]:
    """
    计算兑换目标品质纹章所需的总材料。

    特殊纹章：材料为正常的一半（已折半的基础材料 × 等价数量）
    普通纹章：基础材料 × 等价数量
    """
    base = ALL_SEALS.get(seal_name, {})
    if not base:
        return {}

    target_idx = _quality_index(target_quality)
    if target_idx < 0:
        return {}

    # 计算需要的普通等价数量
    total_equiv = _calc_normal_equivalent(seal_name, target_quality)

    # 扣除已有纹章的等价数量
    if owned:
        for q, cnt in owned.items():
            equiv = _calc_normal_equivalent(seal_name, q) * cnt
            total_equiv -= equiv

    if total_equiv <= 0:
        return {}

    # 按比例计算各材料
    result = {}
    for mat, qty in base.items():
        total = qty * total_equiv
        if total > 0:
            result[mat] = total
    return result


def parse_seal_calc_input(text: str) -> tuple[Optional[str], Optional[str], Optional[dict[str, int]]]:
    """
    解析纹章计算输入。

    格式: #计算[品质][纹章名] 或 #计算[品质][纹章名]-[数量][品质][纹章名]-...

    返回: (target_quality, seal_name, owned) 或 (None, None, None) 表示解析失败
    """
    text = re.sub(r'^#?计算', '', text.strip())

    if not text:
        return None, None, None

    parts = text.split('-')

    target_quality = None
    target_name = None
    owned = {}

    for i, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue

        m = re.match(r'(\d*)(普通|稀有|极品|史诗|传奇)(.+)', part)
        if not m:
            continue

        qty_str, quality, name = m.groups()
        qty = int(qty_str) if qty_str else 1

        if i == 0:
            target_quality = quality
            target_name = name
        else:
            owned[quality] = owned.get(quality, 0) + qty

    return target_quality, target_name, owned


def calculate_seal(text: str) -> dict:
    """
    计算纹章兑换所需材料。

    输入格式: #计算[品质][纹章名] 或带已有纹章的格式
    """
    target_quality, seal_name, owned = parse_seal_calc_input(text)

    if not target_quality or not seal_name:
        return {"type": "text", "content": "格式错误，请使用：#计算[品质][纹章名]\n如：#计算传奇奇袭"}

    if seal_name not in ALL_SEALS:
        available = "、".join(ALL_SEALS.keys())
        return {"type": "text", "content": f"未找到纹章「{seal_name}」的数据。\n当前支持：{available}"}

    if not ALL_SEALS[seal_name]:
        return {"type": "text", "content": f"纹章「{seal_name}」的材料数据待补充。"}

    materials = _calc_materials_for_target(seal_name, target_quality, owned)

    if not materials:
        owned_desc = ""
        if owned:
            owned_parts = [f"{v}个{k}" for k, v in owned.items()]
            owned_desc = f"\n你已拥有：{', '.join(owned_parts)}"
        return {"type": "text", "content": f"你已拥有足够的材料，无需额外兑换。{owned_desc}"}

    # 格式化输出
    total_equiv = _calc_normal_equivalent(seal_name, target_quality)
    seal_type = "特殊纹章" if seal_name in SPECIAL_SEALS else "普通纹章"
    rule = "4进1(史诗→传奇2进1)" if seal_name in SPECIAL_SEALS else "8进1(史诗→传奇4进1)"
    lines = [
        f"【{target_quality}{seal_name} 兑换计算】",
        f"类型：{seal_type}（{rule}）",
        f"需要 {total_equiv} 个普通{seal_name} 等价",
    ]

    if owned:
        owned_parts = []
        for q, cnt in owned.items():
            equiv = _calc_normal_equivalent(seal_name, q) * cnt
            owned_parts.append(f"{cnt}个{q}({equiv}等价)")
        lines.append(f"已有：{', '.join(owned_parts)}")
        lines.append("")

    lines.append("所需材料：")
    for mat, qty in sorted(materials.items()):
        lines.append(f"  {mat} × {qty}")

    return {"type": "text", "content": "\n".join(lines)}
