"""菜单模块"""
from pathlib import Path

# 菜单图片路径
MENU_IMAGE = Path(__file__).parent.parent / "templates" / "menu_full.png"


def get_main_menu() -> dict:
    """高频查询菜单（文字版）"""
    text = """【元素之诗 · 功能菜单】

📊 Boss属性
🏔️ 自强战力推荐
📜 纹章
🔨 锻造（数据待补）
💎 魔素解构
⚔️ 装备继承
🔍 关键词搜索

发送对应板块关键词即可使用
如：属性、自强、纹章、解构 等"""
    return {"type": "text", "content": text}


def get_full_menu() -> dict:
    """完整模块菜单（图片版）"""
    if MENU_IMAGE.exists():
        return {"type": "image", "content": str(MENU_IMAGE)}
    # 图片不存在时 fallback 到文字
    return {"type": "text", "content": "菜单图片未找到，请联系管理员。"}
