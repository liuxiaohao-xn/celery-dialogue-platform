# -*- coding: utf-8 -*-
# @Time : 2022/6/10 17:02
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : tokenizer.py
from __future__ import annotations
from abc import ABCMeta, abstractmethod
import logging
from typing import Text, List, Dict, Any, Optional
from src.common.message import UserMsg

logger = logging.getLogger(__name__)


class Token:

    def __init__(
            self,
            text: Text,
            start: int,
            end: Optional[int] = None,
    ) -> None:
        """Create a `Token`.

        Args:
            text: The token text.
            start: Token在原始消息中的起始索引.
            end: Token在原始消息中的结束索引.
        """
        self.text = text
        self.start = start
        self.end = end if end else start + len(text)


class Tokenizer(metaclass=ABCMeta):
    """Base class for tokenizers."""

    @abstractmethod
    def tokenize(self, message: UserMsg) -> List[Token]:
        """分词"""
        ...

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        """获取自定义tokenize初始化需要的参数"""
        ...

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> Tokenizer:
        """创建一个Tokenizer对象"""
        ...
