# -*- coding: utf-8 -*-
# @Time : 2022/6/8 14:28
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : component.py
from __future__ import annotations
from typing import Dict, Text, Any
from abc import ABCMeta, abstractmethod
from src.common.message import SysMsg


class Component(metaclass=ABCMeta):
    """组件抽象类"""

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        """获取自定义组件初始化需要的参数."""
        ...

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> Component:
        """根据config创建一个ComponentBase对象, 其中config=cls.get_default_config().
            eg:
                ...
        """
        ...

    @abstractmethod
    def process(self, msg: SysMsg) -> SysMsg:
        ...
