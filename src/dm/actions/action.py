# -*- coding: utf-8 -*-
# @Time : 2022/8/5 9:40
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : action.py
from abc import ABCMeta, abstractmethod
import random
import logging
from typing import Text, List, Dict, Tuple
from src.common.message import SysMsg
from src.common.domain.domain import Slot, Flow, Entity

logger = logging.getLogger(__name__)


def confirm(func):
    """业务意图确认"""
    def wrapper(*args, **kwargs):
        args[1].confirm = True
        return func(*args, **kwargs)
    return wrapper


class Action(metaclass=ABCMeta):

    @abstractmethod
    def run(self, *args, **kwargs) -> SysMsg:
        """回复用户动作"""
        ...


class SuccessAction(Action):
    """任务成功action"""
    def get_related_entities(self, entities: List[Entity], slot: Slot) -> List[Entity]:
        return [entity for entity in entities if entity.en in slot.polymorphism]

    def run(self, msg: SysMsg, intent: Text, flow: Flow) -> SysMsg:
        msg.rsp = random.choice(flow.response)
        return msg


class CancelAction(Action):
    """取消任务action"""

    def run(self, msg: SysMsg, intent: Text) -> SysMsg:
        cancel_flow = msg.parsed_domain.parsed_intents.get(intent).cancel_flow
        if not cancel_flow:
            raise Exception(f"{intent}未配置cancel_flow. ")
        msg.rsp = random.choice(cancel_flow.response)
        msg.set_component_intent_res(intent)
        return msg


class SlotAction(Action):

    def run(self, msg: SysMsg, slot: Slot, flow: Flow) -> SysMsg:
        ...


class SlotMissingAction(SlotAction):

    def run(self, msg: SysMsg, missing_slot: Slot, flow: Flow) -> SysMsg:
        msg.rsp = random.choice(flow.response)
        print(msg.rsp)
        return msg


class EntityAction(Action):

    def run(self, *args, **kwargs) -> SysMsg:
        ...


class EntityErrorAction(EntityAction):

    def run(self, msg: SysMsg, slot: Slot, multi_entities: List[Entity],
            error_entities: List[Entity], flow: Flow) -> SysMsg:
        ...


class EntityRepeatAction(EntityAction):

    def run(self, msg: SysMsg, slot: Slot, repeat_entity: Tuple[Entity, List[Text]], flow: Flow) -> SysMsg:
        ...


class EntityFollowUpAction(EntityAction):

    def run(self, msg: SysMsg, slot: Slot, flow: Flow, activate_type: int) -> SysMsg:
        ...


