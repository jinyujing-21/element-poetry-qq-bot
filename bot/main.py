"""机器人入口 — 官方QQ机器人SDK (qq-botpy) WebSocket模式"""
import asyncio
import logging
import os
import botpy
from botpy import Intents

# 配置日志
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# QQ开放平台配置
QQ_APPID = os.getenv("QQ_APPID", "")
QQ_SECRET = os.getenv("QQ_SECRET", "")
QQ_TOKEN = os.getenv("QQ_TOKEN", "")


def extract_message(message) -> str | None:
    """从消息对象中提取纯文本内容"""
    if hasattr(message, 'content'):
        return message.content.strip() if message.content else None
    return None


class ElementPoetryBot(botpy.Client):
    """元素之诗QQ机器人"""

    async def on_ready(self):
        """机器人连接成功"""
        logger.info("WebSocket连接成功，机器人已在线")

    async def on_message_create(self, event):
        """处理群消息事件"""
        try:
            from bot.handler import handle_message

            text = extract_message(event.message)
            if not text:
                return

            user_id = str(event.author.member_openid)
            group_id = event.group_openid

            # 处理消息
            reply = handle_message(user_id, group_id, text)

            # 发送回复（支持单条 dict 或多条 list）
            replies = reply if isinstance(reply, list) else [reply]
            for r in replies:
                if r["type"] == "text":
                    await self.send_group_msg(group_id, r["content"])
                elif r["type"] == "image":
                    await self.send_group_image(group_id, r["content"])
                elif r["type"] == "markdown":
                    await self.send_group_markdown(group_id, r["content"])

        except Exception as e:
            logger.error(f"处理群消息异常: {e}")

    async def send_group_msg(self, group_id: str, content: str):
        """发送群文本消息"""
        try:
            await self.api.post_group_message(int(group_id), content)
            logger.info(f"已发送文本消息到群 {group_id}")
        except Exception as e:
            logger.error(f"发送文本消息失败: {e}")

    async def send_group_image(self, group_id: str, image_path: str):
        """发送群图片"""
        try:
            import base64
            from pathlib import Path

            img_file = Path(image_path)
            if not img_file.exists():
                logger.error(f"图片不存在: {image_path}")
                return

            with open(img_file, "rb") as f:
                img_data = base64.b64encode(f.read()).decode()

            await self.api.post_group_message(int(group_id), image=img_data)
            logger.info(f"已发送图片到群 {group_id}: {image_path}")
        except Exception as e:
            logger.error(f"发送图片失败: {e}")

    async def send_group_markdown(self, group_id: str, markdown_content: str, params: list = None):
        """发送群Markdown消息"""
        try:
            from botpy.message import MessageMarkdown, MessageMarkdownParams

            if params:
                md = MessageMarkdown(
                    custom_template_id="",
                    params=[MessageMarkdownParams(key=k, values=[v]) for k, v in params]
                )
            else:
                md = MessageMarkdown(content=markdown_content)

            await self.api.post_group_message(int(group_id), markdown=md)
            logger.info(f"已发送Markdown消息到群 {group_id}")
        except Exception as e:
            logger.error(f"发送Markdown消息失败: {e}")


async def main():
    """主函数 — WebSocket模式"""
    from core.database import init_db

    logger.info("正在初始化数据库...")
    init_db()

    logger.info(f"正在启动QQ机器人 WebSocket模式 (AppID: {QQ_APPID})...")

    # 创建机器人客户端 - 使用public_messages接收QQ群消息
    intents = Intents(
        public_messages=True
    )

    client = ElementPoetryBot(
        intents=intents,
        is_sandbox=False
    )

    logger.info("正在连接QQ服务器...")
    async with client:
        await client.start(QQ_APPID, QQ_SECRET)


if __name__ == "__main__":
    asyncio.run(main())
