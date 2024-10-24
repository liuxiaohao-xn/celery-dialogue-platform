# -*- coding: utf-8 -*-
# @Time : 2022/8/5 17:08
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : entity_repeat_dialogue_flow.py
from __future__ import annotations
from typing import List, Text, Tuple
from src.common.message import SysMsg
from src.common.domain.domain import Entity, Slot
from src.common.domain.flow_names import FlowName
from src.common.constant import ActivateType, SystemIntent
from src.dm.dialogue_flow.dialogue_flow import DialogueFlow, sync_msg
from src.dm.dialogue_manage.dialogue_entity_info import DialogueStateEntityInfo


class EntityRepeatDialogueFlow(DialogueFlow):

    def __init__(self, intent: Text, hang_slot: Slot):
        super(EntityRepeatDialogueFlow, self).__init__(intent, hang_slot)
        self.activate_type = ActivateType.ACTIVATE_FROM_FLOW
        self.repeat_verified_entity: Tuple[Entity, List[Text]] = None

    @property
    def name(self):
        return FlowName.ENTITY_REPEAT_FLOW

    @property
    def next_flow(self):
        from src.dm.dialogue_flow.entity_follow_up_dialogue_flow import EntityFollowUpDialogueFlow
        return EntityFollowUpDialogueFlow(self.intent, self.hang_slot)

    def exd_activate_info(self, entities: List[Entity]):
        """激活信息：提取实体中有hang_slot对应的实体"""
        for entity in entities:
            if entity.en in self.hang_slot.polymorphism:
                return True
        return False

    def activate(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> bool:
        """
        1.无意图
            - 提取到 hang_slot 对应的实体，激活成功
            - 激活失败，转AIUI
        2.有意图
            - 意图和历史意图相等，激活成功
            - 意图为select_num，激活成功
            - 否则激活失败，切换意图
        """
        exd_entities = msg.get_nlu_exd_entities()
        repeat_verified_entity_info = dialogue_state_entity_info.repeat_verified_entity_info
        if not msg.get_nlu_intent():
            if self.exd_activate_info(exd_entities):
                self.activate_type = ActivateType.ACTIVATE_SAME_INTENT
                return True
            return False
        else:
            if msg.get_nlu_intent() == self.intent:
                self.activate_type = ActivateType.ACTIVATE_SAME_INTENT
                return True
            elif msg.get_nlu_intent() == SystemIntent.SELECT:
                self.activate_type = ActivateType.ACTIVATE_SELECT
                repeat_verified_entity_info.select_num = exd_entities[0].value
                return True
            else:
                return False

    def skip_flow(self) -> bool:
        if not self.end \
                and self.hang_slot \
                and self.name in self.hang_slot.flows:
            self.open()
            return False
        self.close()
        return True

    def action(self, msg: SysMsg) -> SysMsg:
        flow = self.get_flow(self.hang_slot)
        return self.get_action_eg(flow.action).run(
            msg,
            self.hang_slot,
            self.repeat_verified_entity,
            flow
        )

    def select_repeat_entity(self, msg: SysMsg) -> None or Entity:
        for entity in msg.get_nlu_exd_entities():
            repeat_entity, values = self.repeat_verified_entity
            if entity.value in values:
                repeat_entity.verify_value = entity.value
                return repeat_entity
        return None

    @sync_msg
    def process(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> DialogueFlow:

        if self.skip_flow():
            return self

        repeat_verified_entity_info = dialogue_state_entity_info.repeat_verified_entity_info

        if not self.repeat_verified_entity:
            self.repeat_verified_entity = repeat_verified_entity_info.pop_repeat_verified_entity()

        while self.repeat_verified_entity:
            """循环追问重复实体"""
            if self.activate_type == ActivateType.ACTIVATE_FROM_FLOW:
                return self
            elif self.activate_type == ActivateType.ACTIVATE_SAME_INTENT:
                # entity = self.select_repeat_entity(msg)
                # if not entity:
                return self
            elif self.activate_type == ActivateType.ACTIVATE_SELECT:
                if repeat_verified_entity_info.is_select_overflow(self.repeat_verified_entity):
                    return self
                entity = repeat_verified_entity_info.entity_redress(self.repeat_verified_entity)
            dialogue_state_entity_info.append_verified_entity(entity)
            self.repeat_verified_entity = repeat_verified_entity_info.pop_repeat_verified_entity()
        else:
            # 无重复实体
            dialogue_state_entity_info.init_slot_follow_up_entity_info(
                self.hang_slot
            )
            self.close()
            return self
