# -*- coding: utf-8 -*-
# @Time : 2022/6/9 16:54
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : domain.py
from __future__ import annotations
from dataclasses import dataclass, Field
from typing import Text, List, Any, Dict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Domain:
    """domain数据类"""
    en: Text
    zh: Text

    @classmethod
    def make_o(cls, **kwargs):
        """创建domain对象"""
        pass

    @classmethod
    def required_attrs(cls):
        ...


@dataclass
class Skill(Domain):
    """技能数据类"""
    intents: List[Text]
    pipeline: List[Any]

    @classmethod
    def make_o(cls, **kwargs):
        try:
            return Skill(**kwargs)
        except Exception:
            raise Exception(f"从{kwargs}创建Skill对象失败！")

    @classmethod
    def required_attrs(cls):
        return ["en", "zh", "intents", "pipeline"]



@dataclass
class Intent(Domain):
    """意图数据类"""
    success_flow: Flow
    slots: Dict[Text, Slot] = None
    cancel_flow: Flow = None
    super: List[Text] = None
    monitor: Monitor = None

    @classmethod
    def make_o(cls, **kwargs):
        try:
            return Intent(**kwargs)
        except Exception:
            raise Exception(f"从{kwargs}创建Intent对象失败！")

    @classmethod
    def required_attrs(cls):
        return ["en", "zh", "success_flow"]

    def is_super_intent(self, intent: Text):
        if not super:
            raise Exception(f"{self.en}.super is None!")
        return True if intent in self.super else False


@dataclass
class Monitor:
    slot: Text
    action: Text

    @classmethod
    def make_o(cls, **kwargs):
        try:
            return Monitor(**kwargs)
        except Exception:
            raise Exception(f"从{kwargs}创建Skill对象失败！")

    @classmethod
    def required_attrs(cls):
        return ["slot", "action"]


@dataclass
class Flow:
    name: Text
    action: Text
    response: List[Text]

    @classmethod
    def make_o(cls, **kwargs):
        try:
            return Flow(**kwargs)
        except Exception:
            raise Exception(f"从{kwargs}创建Skill对象失败！")

    @classmethod
    def required_attrs(cls):
        return ["name", "action", "response"]


@dataclass
class Slot(Domain):
    """槽位数据类"""
    id: int
    required: bool
    multi: bool
    polymorphism: List[Text]
    # ext info
    filling_entity: Entity = None
    # flow info
    flows: Dict[Text, Flow] = None

    @classmethod
    def make_o(cls, **kwargs):
        try:
            return Slot(**kwargs)
        except Exception:
            raise Exception(f"从{kwargs}创建Slot对象失败！")

    @classmethod
    def required_attrs(cls):
        return ["en", "zh", "id", "required", "multi", "polymorphism"]


@dataclass
class Entity(Domain):
    """实体数据类"""
    csl: Text
    verify_fn: Text
    # ext info
    start_pos: int = None
    end_pos: int = None
    value: Any = None
    # verify info
    verify_value: Text = None
    # slot info
    slot_name: Text = None
    required: bool = None

    @classmethod
    def make_o(cls, **kwargs):
        try:
            return Entity(**kwargs)
        except Exception:
            raise Exception(f"从{kwargs}创建Entity对象失败！")

    @classmethod
    def required_attrs(cls):
        return ["en", "zh", "csl", "verify_fn"]

    def set_ext_info(self, value: Text, start_pos: int, end_pos: int):
        self.value = value
        self.start_pos = start_pos
        self.end_pos = end_pos

    def set_verify_value(self, verify_value: Text):
        self.verify_value = verify_value

    def set_slot_info(self, slot: Slot):
        self.slot_name = slot.en
        self.required = slot.required

    def __eq__(self, other: Entity):
        """切勿修改EXTEntity相等判断条件, 目前认为两个EXTEntity的实体名和值相等，就认为两者相等，暂不考虑位置信息."""
        return self.en == other.en and (
                self.value == other.value or (self.value and self.verify_value
                                              and self.verify_value == other.verify_value)
        )
