# -*- coding: utf-8 -*-
# @Time : 2022/8/9 18:34
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : entity_follow_up_dialogue_flow.py
from __future__ import annotations
from typing import List, Text
from src.common.message import SysMsg
from src.common.domain.domain import Entity, Slot
from src.common.constant import ActivateType, SystemIntent
from src.common.domain.flow_names import FlowName
from src.dm.dialogue_flow.dialogue_flow import DialogueFlow, sync_msg
from src.dm.dialogue_manage.dialogue_entity_info import DialogueStateEntityInfo


class EntityFollowUpDialogueFlow(DialogueFlow):

    def __init__(self, intent: Text, hang_slot: Slot):
        super(EntityFollowUpDialogueFlow, self).__init__(intent, hang_slot)
        self.activate_type: int = ActivateType.ACTIVATE_FROM_FLOW

    @property
    def name(self):
        return FlowName.ENTITY_FOLLOW_UP_FLOW

    @property
    def next_flow(self):
        return self._next_flow

    @next_flow.setter
    def next_flow(self, value):
        self._next_flow = value

    def exd_activate_info(self, entities: List[Entity]):
        """激活信息：提取实体中有hang_slot对应的实体"""
        for entity in entities:
            if entity.en in self.hang_slot.polymorphism:
                return True
        return False

    def activate(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> bool:
        """
        1.无意图
            - 提取到激活信息，激活成功
            - 否则激活失败，转AIUI
        2.有意图
            - 意图为yes，激活成功
            - 意图为no，激活成功
            - 意图和历史意图相同，激活成功
            - 否则激活失败，切换意图
        """
        exd_entities = msg.get_exd_entities()
        slot_follow_up_entity_info = dialogue_state_entity_info.slot_follow_up_entity_info
        if not msg.get_pre_intent():
            if self.exd_activate_info(exd_entities):
                self.activate_type = ActivateType.ACTIVATE_SAME_INTENT
                slot_follow_up_entity_info.append_follow_up_entities(
                    exd_entities
                )
                return True
            return False
        else:
            if msg.get_pre_intent() == SystemIntent.POSITIVE:
                self.activate_type = ActivateType.ACTIVATE_YES
                return True
            elif msg.get_pre_intent() == SystemIntent.NEGATIVE:
                self.activate_type = ActivateType.ACTIVATE_NO
                return True
            elif msg.get_pre_intent() == self.intent:
                self.activate_type = ActivateType.ACTIVATE_SAME_INTENT
                slot_follow_up_entity_info.append_follow_up_entities(
                    exd_entities
                )
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
            flow,
            self.activate_type
        )

    def jump_to_success_dialogue_flow(self):
        from src.dm.dialogue_flow.success_dialogue_flow import SuccessDialogueFlow
        self.next_flow = SuccessDialogueFlow(self.intent, self.hang_slot)

    def jump_to_entity_verify_dialogue_flow(self):
        from src.dm.dialogue_flow.entity_verify_dialogue_flow import EntityVerifyDialogueFlow
        self.next_flow = EntityVerifyDialogueFlow(self.intent, self.hang_slot)

    @sync_msg
    def process(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> DialogueFlow:

        if self.skip_flow():
            self.jump_to_success_dialogue_flow()
            return self

        slot_follow_up_entity_info = dialogue_state_entity_info.slot_follow_up_entity_info

        if self.activate_type == ActivateType.ACTIVATE_FROM_FLOW or self.activate_type == ActivateType.ACTIVATE_YES:
            return self
        elif self.activate_type == ActivateType.ACTIVATE_NO:
            self.jump_to_success_dialogue_flow()
            self.close()
            return self
        elif self.activate_type == ActivateType.ACTIVATE_SAME_INTENT:
            if not slot_follow_up_entity_info.follow_up_entities:
                return self
            dialogue_state_entity_info.init_pending_verified_entity_info(
                self.hang_slot,
                slot_follow_up_entity_info.follow_up_entities
            )
            # 跳转到实体验证流程
            self.jump_to_entity_verify_dialogue_flow()
            self.close()
            return self
        else:
            raise Exception(f"激活方式{self.activate_type}不支持. ")

