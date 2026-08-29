"""递归计算引擎 — 锻造材料 / 魔素解构"""
from core.database import query_one, query_all


def calc_forge(target: str, quantity: int = 1,
               deducted: dict = None) -> dict:
    """
    递归计算锻造材料。

    参数:
        target: 目标装备名
        quantity: 数量
        deducted: 已有材料 {"材料名": 数量}

    返回:
        {
            "target": "天灾主手",
            "quantity": 1,
            "materials": [{"name": "A材料", "quantity": 20}, ...],
            "prerequisites": [{"name": "xxx武器", "quantity": 1}, ...],
            "gold": 500000,
            "magic": 300,
            "deducted": {"天灾图纸": 1},
            "missing": [{"name": "A材料", "quantity": 16}, ...]
        }
    """
    deducted = deducted or {}
    all_materials = {}
    prerequisites = []
    total_gold = 0
    total_magic = 0

    _collect_materials(target, quantity, all_materials, prerequisites,
                       total_gold, total_magic)

    # 扣除已有材料
    missing = []
    for mat_name, mat_qty in all_materials.items():
        remaining = mat_qty - deducted.get(mat_name, 0)
        if remaining > 0:
            missing.append({"name": mat_name, "quantity": remaining})

    return {
        "target": target,
        "quantity": quantity,
        "materials": [{"name": k, "quantity": v} for k, v in all_materials.items()],
        "prerequisites": prerequisites,
        "deducted": deducted,
        "missing": missing,
    }


def _collect_materials(item: str, qty: int,
                       all_materials: dict, prerequisites: list,
                       total_gold: int, total_magic: int):
    """递归收集材料"""
    recipes = query_all(
        "SELECT material_name, material_quantity, is_prerequisite, gold_cost, magic_cost "
        "FROM forge_recipe WHERE target_item = ?", (item,)
    )

    if not recipes:
        return

    for row in recipes:
        mat_name = row["material_name"]
        mat_qty = row["material_quantity"] * qty
        is_prereq = row["is_prerequisite"]

        if is_prereq:
            prerequisites.append({"name": mat_name, "quantity": mat_qty})
            # 递归展开前置装备
            _collect_materials(mat_name, mat_qty, all_materials,
                               prerequisites, total_gold, total_magic)
        else:
            all_materials[mat_name] = all_materials.get(mat_name, 0) + mat_qty

        total_gold += row["gold_cost"] * qty
        total_magic += row["magic_cost"] * qty


def calc_magic_decompose(magic_name: str, quantity: int = 1) -> dict:
    """
    计算魔素解构费用。

    参数:
        magic_name: 魔素名称（最上级魔素/上级魔素/普通魔素）
        quantity: 数量

    返回:
        {
            "name": "上级魔素",
            "quantity": 10,
            "material_gold": 1250000,  # 材料金
            "bag_gold": 625000,        # 背包金
            "error": None
        }
    """
    # 魔素价格表
    MAGIC_PRICES = {
        "最上级魔素": {"material_gold": 6250000, "bag_gold": 3125000, "limit": 50},
        "上级魔素": {"material_gold": 125000, "bag_gold": 62500, "limit": 150},
        "普通魔素": {"material_gold": 2500, "bag_gold": 1250, "limit": 100},
    }

    # 检查魔素名称是否有效
    if magic_name not in MAGIC_PRICES:
        return {
            "name": magic_name,
            "quantity": quantity,
            "material_gold": 0,
            "bag_gold": 0,
            "error": f"未识别的魔素名称：{magic_name}\n支持：最上级魔素、上级魔素、普通魔素"
        }

    price_info = MAGIC_PRICES[magic_name]
    limit = price_info["limit"]

    # 检查数量是否超限
    if quantity > limit:
        return {
            "name": magic_name,
            "quantity": quantity,
            "material_gold": 0,
            "bag_gold": 0,
            "error": f"{magic_name}计算上限为{limit}个，你输入了{quantity}个"
        }

    # 计算费用
    material_gold = price_info["material_gold"] * quantity
    bag_gold = price_info["bag_gold"] * quantity

    return {
        "name": magic_name,
        "quantity": quantity,
        "material_gold": material_gold,
        "bag_gold": bag_gold,
        "error": None
    }
