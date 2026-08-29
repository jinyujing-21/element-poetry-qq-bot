"""消息处理器 — 命令解析 → 模块分发"""
import re
from core.alias import resolve_alias, search_fuzzy
from core.database import execute, query_one

# 用户选择状态（boss 多阶段选择等）
_user_selections: dict[str, list[str]] = {}  # user_id -> [boss_name, ...]


# 命令映射表：关键词 → (模块, 动作)
COMMAND_MAP = {
    "菜单": ("menu", "main"),
    "模块菜单": ("menu", "full"),
    "索引": ("menu", "full"),
    "boss属性": ("boss", "table"),
    "属性": ("boss", "table"),
    "进本条件": ("dungeon", "entry"),
    "进本": ("dungeon", "entry"),
    "自强": ("dungeon", "solo"),
    "自强战力推荐": ("dungeon", "solo"),
    "纹章": ("seal", "list"),
    "纹章模块": ("seal", "list"),
    "纹章列表": ("seal", "list"),
    "查纹章": ("seal", "query"),
    "锻造": ("forge", "info"),
    "锻造图纸": ("forge", "recipe"),
    "计算": ("forge", "calculate"),
    "锻造材料计算": ("forge", "calculate"),
    "解构": ("magic", "decompose"),
    "魔素解构": ("magic", "decompose"),
    "魔素解构计算": ("magic", "decompose"),
    "#魔素计算": ("magic", "decompose"),
    "关键词": ("index", "search"),
    "搜索": ("index", "search"),
    "反馈": ("feedback", "submit"),
    "装备继承": ("equip", "inherit"),
    "继承": ("equip", "inherit"),
    "继承关系": ("equip", "inherit"),
    "免费领取水晶": ("crystal", "claim"),
    "纹章兑换计算": ("seal_calc", "guide"),
    "纹章计算": ("seal_calc", "guide"),
    "#计算": ("seal_calc", "calculate"),
    "ping": ("system", "ping"),
}


def parse_command(raw_text: str) -> tuple[str, str, str]:
    """
    解析用户输入。

    返回: (command, module, action)
    command: 原始命令词
    module: 模块名
    action: 动作名
    """
    text = raw_text.strip()

    # 精确匹配命令词
    for cmd, (mod, act) in COMMAND_MAP.items():
        if text == cmd:
            return cmd, mod, act

    # 前缀匹配（命令 + 参数）
    for cmd, (mod, act) in COMMAND_MAP.items():
        if text.startswith(cmd):
            return cmd, mod, act

    # 未识别的输入
    return text, "unknown", "unknown"


def get_command_args(raw_text: str, command: str) -> str:
    """提取命令后面的参数"""
    text = raw_text.strip()
    if text.startswith(command):
        return text[len(command):].strip()
    return ""


def handle_message(user_id: str, group_id: str, raw_text: str) -> dict:
    """
    处理群消息，返回回复内容。

    返回:
        {
            "type": "text" | "image" | "markdown" | "none",
            "content": "文字内容" 或 图片路径 或 Markdown内容,
            "reply_to": 消息ID（可选）
        }
    """
    command, module, action = parse_command(raw_text)

    if module == "system" and action == "ping":
        return {"type": "text", "content": "pong"}

    if module == "menu":
        return _handle_menu(action)

    if module == "boss":
        return _handle_boss(raw_text, command, user_id)

    if module == "dungeon":
        args = get_command_args(raw_text, command)
        if action == "entry":
            return _handle_dungeon_entry(args)
        elif action == "solo":
            return _handle_dungeon_solo(args)

    if module == "seal":
        args = get_command_args(raw_text, command)
        return _handle_seal(args, action)

    if module == "forge":
        args = get_command_args(raw_text, command)
        return _handle_forge(args, action)

    if module == "magic":
        args = get_command_args(raw_text, command)
        return _handle_magic(args)

    if module == "index":
        args = get_command_args(raw_text, command)
        return _handle_search(args)

    if module == "feedback":
        args = get_command_args(raw_text, command)
        return _handle_feedback(user_id, group_id, args)

    if module == "equip":
        args = get_command_args(raw_text, command)
        return _handle_equip(args, action)

    if module == "crystal":
        return _handle_crystal()

    if module == "seal_calc":
        args = get_command_args(raw_text, command)
        return _handle_seal_calc(args, action)

    # 序号选择（boss 多阶段等）
    text = raw_text.strip()
    if text.isdigit() and user_id in _user_selections:
        idx = int(text) - 1
        selections = _user_selections.pop(user_id)
        if 0 <= idx < len(selections):
            from modules.boss import query_boss
            result = query_boss(selections[idx])
            # 清理返回中的 _candidates
            result.pop("_candidates", None)
            return result

    # 未识别 → 尝试当作纹章名查询（至少2个字，且有匹配结果才触发）
    from modules.seal import query_seal
    text = raw_text.strip()
    if len(text) >= 2:
        result = query_seal(text)
        if not result.get("content", "").startswith("未找到"):
            return result

    # 普通聊天，不回复
    return {"type": "none", "content": ""}


def _handle_menu(action: str) -> dict:
    """处理菜单命令"""
    from modules.menu import get_main_menu, get_full_menu
    if action == "full":
        return get_full_menu()
    return get_main_menu()


def _handle_boss(raw_text: str, command: str, user_id: str = "") -> dict:
    """处理 boss 属性查询"""
    from modules.boss import query_boss, get_boss_images
    args = get_command_args(raw_text, command)

    if not args:
        return get_boss_images()

    result = query_boss(args)
    # 多候选时存储选择列表
    candidates = result.pop("_candidates", None)
    if candidates and user_id:
        _user_selections[user_id] = candidates
    return result


def _handle_dungeon_entry(args: str) -> dict:
    """处理进本条件查询"""
    from modules.dungeon import query_entry
    if not args:
        return {"type": "text", "content": "请指定副本名，如：进本条件 霾火"}
    return query_entry(args)


def _handle_dungeon_solo(args: str) -> dict:
    """处理自强战力推荐查询"""
    from modules.dungeon import query_solo
    return query_solo(args if args else None)


def _handle_seal(args: str, action: str) -> dict:
    """处理纹章查询"""
    from modules.seal import query_seal, get_seal_list
    if action == "list" or not args:
        return get_seal_list(args if args else None)
    return query_seal(args)


def _handle_forge(args: str, action: str) -> dict:
    """处理锻造查询"""
    from modules.forge import query_forge, query_recipe, calc_forge_materials
    if not args:
        return {"type": "text", "content": "请指定装备名，如：锻造 天灾主手"}
    if action == "recipe":
        return query_recipe(args)
    if action == "calculate":
        return calc_forge_materials(args)
    return query_forge(args)


def _handle_magic(args: str) -> dict:
    """处理魔素解构"""
    from modules.magic import decompose_magic
    return decompose_magic(args)


def _handle_search(args: str) -> dict:
    """处理关键词搜索"""
    from modules.index import search_keyword
    if not args:
        return {"type": "text", "content": "请输入搜索关键词，如：关键词 魔技之石"}
    return search_keyword(args)


def _handle_feedback(user_id: str, group_id: str, content: str) -> dict:
    """处理反馈"""
    from modules.feedback import submit_feedback
    if not content:
        return {"type": "text", "content": "请输入反馈内容，如：反馈 霾火T推荐偏低"}
    return submit_feedback(user_id, group_id, content)


def _handle_equip(args: str, action: str) -> dict:
    """处理装备继承查询"""
    from modules.equip import get_equip_inherit_image, query_equip_inherit

    # 无参数 → 返回继承关系图
    if not args:
        return get_equip_inherit_image()

    # 有参数 → 查询具体装备的继承关系
    return query_equip_inherit(args)


def _handle_crystal() -> list[dict]:
    """免费领取水晶（钓鱼）"""
    from pathlib import Path
    img = Path(__file__).parent.parent / "templates" / "free_crystal.jpg"
    result = []
    if img.exists():
        result.append({"type": "image", "content": str(img)})
    result.append({"type": "text", "content": "七匹狼吃不吃"})
    return result


def _handle_seal_calc(args: str, action: str) -> dict:
    """处理纹章兑换计算"""
    from modules.seal_calc import get_calc_guide, calculate_seal
    if action == "guide" or not args:
        return get_calc_guide()
    return calculate_seal(args)
