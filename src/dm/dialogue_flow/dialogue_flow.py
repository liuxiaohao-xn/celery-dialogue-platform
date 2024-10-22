# -*- coding: utf-8 -*-
# @Time : 2022/8/3 11:02
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : dialogue_flow.py
from __future__ import annotations
from typing import Text, List, Dict
from src.common.message import SysMsg
from src.common.domain.domain import Slot, Flow, Entity
from src.common.component.component_container import ComponentContainer
from src.dm.actions.action import Action
from src.dm.dialogue_manage.dialogue_entity_info import DialogueStateEntityInfo


class DialogueFlow:

    def __init__(self, intent: Text, hang_slot: Slot) -> None:
        self.intent = intent
        self.hang_slot = hang_slot
        self.end = False

    @property
    def name(self):
        """流程名
            配置域: src.common.domain.flow_names.FlowName
            作用: 用于slot会话流程配置
                eg: intent_A 必要槽位 slot_A 缺失, 那在slot_A.flows下可配置该对话流程.
        """
        return ""

    @property
    def next_flow(self):
        """该流程运行完后, 会运行next_flow."""
        return self

    def open(self):
        """流程未结束标志, 如果流程未结束, 会挂起当前流程, 返回询问用户信息."""
        self.end = False

    def close(self):
        """流程结束标志, 如果流程结束, 关闭当前流程, 继续走下一个流程."""
        self.end = True

    def activate(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> bool:
        """asr文本激活挂起流程
            激活: 则会执行该挂起流程 self.process(...)
            未激活: 不会执行挂起流程
                1. 如果中了其它意图, 则切换会话意图
                2. 未中其它意图, 则走aiui.
        """
        ...

    def skip_flow(self) -> bool:
        """跳过当前流程
            如果slot中未配置该流程名, 则会跳过该流程, 执行next_flow.
        """
        return ...

    def get_flow(self, slot: Slot) -> Flow:
        return slot.flows.get(self.name)

    def get_action_eg(self, action_name: Text) -> Action:
        """根据action name 获取action实例."""
        return ComponentContainer.get_register_klass(action_name)()

    def action(self, msg: SysMsg) -> SysMsg:
        """流程action
            asr激活并执行该流程后, 流程未结束, 则会执行该方法.
        """
        ...

    def process(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> DialogueFlow:
        """流程业务处理函数
            流程被激活后, 执行该业务流程.
        """
        ...


def filter_not_related_entities(entities: List[Entity], cfg_slots: Dict[Text, Slot]) -> List[Entity]:
    """过滤掉槽位不相关的实体"""
    related_entities = []
    for _, slot in cfg_slots.items():
        for entity in entities:
            if entity.en in slot.polymorphism:
                related_entities.append(entity)
    return related_entities


def sync_msg(func):
    """信息同步
        执行完业务处理函数后，需要将处理后的信息同步到msg(主要是意图信息和槽位信息).
    """
    def wrapper(*args, **kwargs) -> DialogueFlow:

        dialogue_flow: DialogueFlow = func(*args, **kwargs)
        msg: SysMsg = args[1]
        dialogue_state_entity_info: DialogueStateEntityInfo = args[2]
        msg.exd_entities = filter_not_related_entities(
            dialogue_state_entity_info.get_last_exd_entities(),
            dialogue_state_entity_info.cfg_slots
        )
        msg.set_component_intent_res(dialogue_flow.intent)
        return dialogue_flow
    return wrapper
