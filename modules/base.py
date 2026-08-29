"""模块基类"""
from abc import ABC, abstractmethod


class BaseModule(ABC):
    """所有模块的基类"""

    name: str = ""
    slug: str = ""

    @abstractmethod
    def handle(self, args: str) -> dict:
        """处理命令，返回回复 dict"""
        pass
