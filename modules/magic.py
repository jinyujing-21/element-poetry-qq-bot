"""魔素解构计算模块"""
from pathlib import Path
from core.calculator import calc_magic_decompose

# 魔素公式图片路径
MAGIC_FORMULA_IMAGE = Path(__file__).parent.parent / "templates" / "magic_formula.jpg"


def decompose_magic(args: str) -> dict:
    """魔素解构计算"""
    # 无参数 → 发送公式图片
    if not args:
        if MAGIC_FORMULA_IMAGE.exists():
            return {"type": "image", "content": str(MAGIC_FORMULA_IMAGE)}
        return {"type": "text", "content": "魔素公式图片未找到，请联系管理员。"}

    # 有参数 → 执行计算
    # 解析参数：支持 "10上级魔素"、"10 上级魔素"、"上级魔素*10"
    magic_name, quantity = _parse_magic_args(args)

    if not magic_name:
        return {"type": "text", "content": "格式：魔素计算[数量][魔素名称]\n例：魔素计算10上级魔素"}

    result = calc_magic_decompose(magic_name, quantity)

    if result["error"]:
        return {"type": "text", "content": result["error"]}

    lines = [
        f"解构获取{result['quantity']}{result['name']}需要：",
        "",
        f"所需材料金：{result['material_gold']:,}",
        f"背包金：{result['bag_gold']:,}",
    ]

    return {"type": "text", "content": "\n".join(lines)}


def _parse_magic_args(args: str) -> tuple[str, int]:
    """
    解析魔素计算参数。

    支持格式：
    - 10上级魔素
    - 10 上级魔素
    - 上级魔素*10
    - 上级魔素
    """
    import re

    # 尝试匹配 "数量+名称" 格式
    match = re.match(r'(\d+)\s*(最上级魔素|上级魔素|普通魔素)', args)
    if match:
        return match.group(2), int(match.group(1))

    # 尝试匹配 "名称*数量" 格式
    match = re.match(r'(最上级魔素|上级魔素|普通魔素)\*?\s*(\d+)', args)
    if match:
        return match.group(1), int(match.group(2))

    # 尝试匹配纯名称
    for name in ["最上级魔素", "上级魔素", "普通魔素"]:
        if name in args:
            # 提取数字
            nums = re.findall(r'\d+', args)
            qty = int(nums[0]) if nums else 1
            return name, qty

    return "", 0
