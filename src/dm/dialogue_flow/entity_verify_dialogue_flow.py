# -*- coding: utf-8 -*-
# @Time : 2022/8/4 9:34
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : entity_verify_dialogue_flow.py
from __future__ import annotations

import copy
from typing import List, Text
from types import FunctionType
from src.common.message import SysMsg
from src.common.domain.domain import Entity, Slot
from src.common.domain.flow_names import FlowName
from src.nlu.utils.verify.verifies import Verify
from src.dm.dialogue_flow.dialogue_flow import DialogueFlow, sync_msg
from src.dm.dialogue_manage.dialogue_entity_info import DialogueStateEntityInfo


class EntityVerifyDialogueFlow(DialogueFlow):

    def __init__(self, intent: Text, hang_slot: Slot):
        super(EntityVerifyDialogueFlow, self).__init__(intent, hang_slot)
        self.verify_wrong_entities = []
        self.multi_entities = []

    @property
    def name(self):
        return FlowName.ENTITY_VERIFY_FLOW

    @property
    def next_flow(self):
        from src.dm.dialogue_flow.entity_repeat_dialogue_flow import EntityRepeatDialogueFlow
        return EntityRepeatDialogueFlow(self.intent, self.hang_slot)

    def skip_flow(self) -> bool:
        if not self.end \
                and self.hang_slot \
                and self.name in self.hang_slot.flows.keys():
            self.open()
            return False
        self.close()
        return True

    def entity_verify(self, entity: Entity) -> List[Text]:
        """实体验证"""
        try:
            verify_fn = getattr(Verify, entity.verify_fn)
        except:
            return [entity.value]
        if type(verify_fn) is FunctionType:
            return verify_fn(entity.value)
        return [entity.value]

    def action(self, msg: SysMsg) -> SysMsg:
        flow = self.get_flow(self.hang_slot)
        return self.get_action_eg(flow.action).run(
            msg,
            self.hang_slot,
            self.multi_entities,
            self.verify_wrong_entities,
            flow
        )

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
            - 意图和历史意图相等，激活成功
            - 否则激活失败，切换意图
        """
        exd_entities = msg.get_exd_entities()
        pending_verified_entity_info = dialogue_state_entity_info.pending_verified_entity_info
        if not msg.get_pre_intent():
            if self.exd_activate_info(exd_entities):
                pending_verified_entity_info.append_not_verified_entities(exd_entities)
                return True
            return False
        else:
            if self.intent == msg.get_pre_intent():
                pending_verified_entity_info.append_not_verified_entities(exd_entities)
                return True
            else:
                return False

    @sync_msg
    def process(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> DialogueFlow:

        if self.skip_flow():
            return self

        pending_verified_entity_info = dialogue_state_entity_info.pending_verified_entity_info

        if not pending_verified_entity_info.not_verified_entities:
            return self
            # raise Exception(f"槽位{self.hang_slot.en}还没有待验证的实体")

        if not self.hang_slot.multi and len(pending_verified_entity_info.not_verified_entities) > 1:
            self.multi_entities = pending_verified_entity_info.not_verified_entities
            return self
        self.multi_entities = []
        # 1. 验证
        verify_wrong_entities, verify_right_entities, verify_multi_res = [], [], []
        for pending_verified_entity in pending_verified_entity_info.not_verified_entities:
            verify_res = self.entity_verify(pending_verified_entity)
            if not verify_res:
                verify_wrong_entities.append(pending_verified_entity)
            elif len(verify_res) == 1:
                pending_verified_entity.set_verify_value(verify_res[0])
                verify_right_entities.append(pending_verified_entity)
            else:
                verify_multi_res.append((pending_verified_entity, verify_res))

        # 2. 添加验证通过的实体
        dialogue_state_entity_info.append_verified_entities(verify_right_entities)

        # 3. 验证不通过
        if verify_wrong_entities:
            self.verify_wrong_entities = verify_wrong_entities
            return self

        # 4. 验证通过(包含有重复实体)
        dialogue_state_entity_info.init_repeat_verified_entity_info(
            copy.deepcopy(self.hang_slot),
            verify_multi_res
        )
        self.close()
        return self
