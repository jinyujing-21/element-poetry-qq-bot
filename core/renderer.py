"""图片卡片渲染 — Pillow 生成游戏UI风格图片"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from bot.config import OUTPUT_DIR


# 游戏UI配色
COLORS = {
    "bg": (25, 25, 35),           # 深色背景
    "card_bg": (35, 35, 50),      # 卡片背景
    "text": (220, 220, 220),      # 主文字
    "title": (255, 200, 80),      # 标题金色
    "accent": (100, 180, 255),    # 强调蓝色
    "fire": (255, 100, 80),       # 火元素红
    "water": (80, 160, 255),      # 水元素蓝
    "wind": (100, 220, 150),      # 风元素绿
    "thunder": (255, 220, 80),    # 雷元素黄
    "light": (255, 240, 200),     # 光元素白
    "dim": (120, 120, 140),       # 暗淡文字
    "border": (60, 60, 80),       # 边框
}


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """获取字体（优先使用系统中文字体）"""
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    ]
    for fp in font_paths:
        if Path(fp).exists():
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def render_boss_table(bosses: list[dict]) -> str:
    """
    渲染 boss 属性总表图片。

    参数: bosses 列表，每项包含 name, fire_res, water_res 等字段
    返回: 图片文件路径
    """
    if not bosses:
        return ""

    # 计算图片尺寸
    row_height = 36
    header_height = 50
    padding = 20
    col_widths = [160, 80, 80, 80, 80, 80, 80, 100]
    total_width = sum(col_widths) + padding * 2
    total_height = header_height + row_height * len(bosses) + padding * 2

    img = Image.new("RGB", (total_width, total_height), COLORS["bg"])
    draw = ImageDraw.Draw(img)

    font_title = _get_font(18)
    font_header = _get_font(14)
    font_body = _get_font(13)

    # 标题
    y = padding
    draw.text((padding, y), "BOSS 属性总表", fill=COLORS["title"], font=font_title)
    y += 35

    # 表头
    headers = ["名称", "火抗", "水抗", "风抗", "雷抗", "光抗", "物减", "攻击"]
    x = padding
    for i, h in enumerate(headers):
        draw.text((x + 5, y), h, fill=COLORS["accent"], font=font_header)
        x += col_widths[i]
    y += header_height - 10

    # 分隔线
    draw.line([(padding, y), (total_width - padding, y)], fill=COLORS["border"], width=1)
    y += 5

    # 数据行
    for boss in bosses:
        x = padding
        values = [
            boss.get("name", ""),
            str(boss.get("fire_res", "-")),
            str(boss.get("water_res", "-")),
            str(boss.get("wind_res", "-")),
            str(boss.get("thunder_res", "-")),
            str(boss.get("light_res", "-")),
            boss.get("phys_reduce", "-"),
            boss.get("attack_element", "-"),
        ]
        for i, val in enumerate(values):
            color = COLORS["text"]
            # 弱点高亮（数值低 = 弱点）
            if i in (1, 2, 3, 4, 5) and val.isdigit() and int(val) < 100:
                color = COLORS["fire"]
            draw.text((x + 5, y), val, fill=color, font=font_body)
            x += col_widths[i]
        y += row_height

    # 保存
    output_path = OUTPUT_DIR / "boss_table.png"
    img.save(str(output_path), "PNG")
    return str(output_path)


def render_text_card(title: str, lines: list[str],
                     accent_color: tuple = None) -> str:
    """
    渲染通用文字卡片图片。

    返回: 图片文件路径
    """
    if accent_color is None:
        accent_color = COLORS["accent"]

    font_title = _get_font(20)
    font_body = _get_font(15)

    padding = 24
    line_height = 28
    max_width = 500

    # 计算高度
    total_height = padding * 2 + 40 + line_height * len(lines) + 10

    img = Image.new("RGB", (max_width, total_height), COLORS["card_bg"])
    draw = ImageDraw.Draw(img)

    # 标题
    y = padding
    draw.text((padding, y), title, fill=COLORS["title"], font=font_title)
    y += 40

    # 内容
    for line in lines:
        draw.text((padding, y), line, fill=COLORS["text"], font=font_body)
        y += line_height

    # 保存
    safe_title = "".join(c for c in title if c.isalnum() or c in "_- ")[:20]
    output_path = OUTPUT_DIR / f"card_{safe_title}.png"
    img.save(str(output_path), "PNG")
    return str(output_path)
