"""反馈模块"""
from core.database import execute


def submit_feedback(user_id: str, group_id: str, content: str) -> dict:
    """提交反馈"""
    execute(
        "INSERT INTO feedback (user_id, group_id, content) VALUES (?, ?, ?)",
        (user_id, group_id, content)
    )

    return {
        "type": "text",
        "content": f"已记录反馈：\n{content}\n\n等待管理员审核，感谢！"
    }
