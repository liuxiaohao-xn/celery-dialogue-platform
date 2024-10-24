# -*- coding: utf-8 -*-
# @Time : 2022/8/10 14:16
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : success_dialogue_flow.py
from __future__ import annotations
from typing import Text, Dict, List
from src.common.message import SysMsg
from src.common.domain.domain import Slot, Flow, Entity
from src.common.domain.flow_names import FlowName
from src.dm.dialogue_flow.dialogue_flow import DialogueFlow, sync_msg
from src.dm.dialogue_manage.dialogue_entity_info import DialogueStateEntityInfo


class SuccessDialogueFlow(DialogueFlow):

    def __init__(self, intent: Text, hang_slot=None):
        super(SuccessDialogueFlow, self).__init__(intent, hang_slot)
        self.verified_entities: Dict[Text, List[Entity]] = {}

    @property
    def name(self):
        return FlowName.SUCCESS_FLOW

    @property
    def next_flow(self):
        return self._next_flow

    @next_flow.setter
    def next_flow(self, value):
        self._next_flow = value

    def action(self, msg: SysMsg) -> SysMsg:

        flow = msg.parsed_domain.cfg_intents.get(self.intent).success_flow
        return self.get_action_eg(flow.action).run(
            msg,
            self.intent,
            flow
        )

    def jump_to_slot_missing_dialogue_flow(self):
        from src.dm.dialogue_flow.slot_missing_dialogue_flow import SlotMissingDialogueFlow
        self.next_flow = SlotMissingDialogueFlow(self.intent)

    def jump_over(self):
        self.next_flow = None

    @sync_msg
    def process(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> DialogueFlow:

        if dialogue_state_entity_info.slot_missing_entity_info.missing_slots:
            self.jump_to_slot_missing_dialogue_flow()
        else:
            self.verified_entities = dialogue_state_entity_info.verified_entities
            self.jump_over()
        self.close()
        # todo 如果该结束对话需要被监控，新增一个结束挂起对话流，添加到结束对话管理池进行监控

        return self

