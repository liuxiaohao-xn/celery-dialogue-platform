# -*- coding: utf-8 -*-
# @Time : 2022/6/10 17:22
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : jieba_tokenizer.py
from __future__ import annotations
from tokenizer import Tokenizer, Token
from typing import Text, List, Dict, Any
from src.common.message import UserMsg


class JiebaTokenizer(Tokenizer):
    """jieba 分词器"""
    def tokenize(self, message: UserMsg) -> List[Token]:
        ...

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        ...

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> JiebaTokenizer:
        ...
