# -*- coding: utf-8 -*-
# @Time : 2022/8/3 11:02
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : slot_missing_dialogue_flow.py
from typing import List, Set, Text, Dict
import copy
from src.common.domain.domain import Slot, Entity
from src.common.domain.flow_names import FlowName
from src.common.message import SysMsg
from src.dm.dialogue_flow.dialogue_flow import DialogueFlow, sync_msg
from src.dm.dialogue_manage.dialogue_entity_info import DialogueStateEntityInfo


class SlotMissingDialogueFlow(DialogueFlow):

    def __init__(self, intent: Text, hang_slot: Slot = None):
        super(SlotMissingDialogueFlow, self).__init__(intent, hang_slot)

    @property
    def name(self):
        return FlowName.SLOT_MISSING_FLOW

    @property
    def next_flow(self) -> DialogueFlow:
        # if self.hang_slot.en == "meeting_time":
        #     from src.dm.dialogue_flow.meeting_time_dialogue_flow.meeting_time_verify_dialogue_flow \
        #         import MeetingTimeVerifyDialogueFlow
        #     return MeetingTimeVerifyDialogueFlow(self.intent, self.hang_slot)
        # else:
        #     from src.dm.dialogue_flow.entity_verify_dialogue_flow import EntityVerifyDialogueFlow
        #     return EntityVerifyDialogueFlow(self.intent, self.hang_slot)
        from src.dm.dialogue_flow.entity_verify_dialogue_flow import EntityVerifyDialogueFlow
        return EntityVerifyDialogueFlow(self.intent, self.hang_slot)

    def skip_flow(self) -> bool:
        if not self.end \
                and self.hang_slot \
                and self.name in self.hang_slot.flows.keys():
            self.open()
            return False
        self.close()
        return True

    def exd_activate_info(self, entities: List[Entity], cfg_slots: Dict[Text, Slot]):
        for entity in entities:
            for slot in cfg_slots.values():
                if slot.required and entity.en in slot.polymorphism:
                    return True
        return False

    def activate(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> bool:
        """
            1、无意图
                - 提取到必要槽位对应的实体，激活成功
                - 否则激活失败，转AIUI
            2、有意图
                - 意图和历史意图相等，激活成功
                - 否则激活失败，切换意图
        """
        exd_entities = msg.get_nlu_exd_entities()
        slot_missing_entity_info = dialogue_state_entity_info.slot_missing_entity_info
        if not msg.get_nlu_intent():
            if self.exd_activate_info(exd_entities, dialogue_state_entity_info.cfg_slots):
                slot_missing_entity_info.append_exd_entities(exd_entities)
                return True
            return False
        else:
            if self.intent == msg.get_nlu_intent():
                slot_missing_entity_info.append_exd_entities(exd_entities)
                return True
            else:
                return False

    def action(self, msg: SysMsg) -> SysMsg:
        flow = self.get_flow(self.hang_slot)
        return self.get_action_eg(flow.action).run(
            msg,
            self.hang_slot,
            flow
        )

    @sync_msg
    def process(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> DialogueFlow:

        slot_missing_entity_info = dialogue_state_entity_info.slot_missing_entity_info

        if not self.hang_slot:
            self.hang_slot = slot_missing_entity_info.pop_missing_slot()

        if self.skip_flow():
            return self

        entities = slot_missing_entity_info.get_entities_linked_slot(
            self.hang_slot
        )
        if not entities:
            return self

        slot_missing_entity_info.del_entities(entities)
        dialogue_state_entity_info.init_pending_verified_entity_info(
            copy.deepcopy(self.hang_slot),
            entities
        )
        self.close()
        return self
