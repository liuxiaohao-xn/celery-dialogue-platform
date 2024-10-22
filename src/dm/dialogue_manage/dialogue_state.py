# -*- coding: utf-8 -*-
# @Time : 2022/8/3 11:04
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : dialogue_manage.py
from typing import Text
import copy
import logging
from src.common.message import SysMsg
import src.common.utils as utils
from src.dm.dialogue_flow.dialogue_flow import DialogueFlow
from src.dm.dialogue_manage.dialogue_entity_info import DialogueStateEntityInfo
from src.dm.dialogue_flow.slot_missing_dialogue_flow import SlotMissingDialogueFlow


logger = logging.getLogger(__name__)


class DialogueState:
    TIMEOUT = 60*1000  # ms
    MAX_DIALOGUE_OVERFLOW_ROUNDS = 3

    def __init__(
            self,
            session_id: Text,
            start_time,
            msg: SysMsg,
            end: bool = False,
    ) -> None:
        self.session_id = session_id
        self.start_time = start_time
        self.skill = copy.deepcopy(msg.get_pre_skill())
        self.intent = copy.deepcopy(msg.get_pre_intent())
        self.end = end
        self.rounds = 0
        self.dialogue_overflow_rounds = 0

        self.dialogue_state_entity_info = DialogueStateEntityInfo(msg.get_cfg_slots_by_intent(self.intent))
        self.dialogue_flow: DialogueFlow = SlotMissingDialogueFlow(self.intent)
        """
        Args:
            session_id: 用户session id
            time: 对话开始时间
            end: 对话结束标志
            round: 对话轮数
        """
    def timeout(self):
        cur_time = utils.get_cur_timestamp()
        intervals = cur_time - self.start_time
        if intervals > DialogueState.TIMEOUT:
            logger.info(f"对话过期时间: {intervals/1000}s. ")
            return True
        return False

    def update_start_time(self):
        self.start_time = utils.get_cur_timestamp()

    def get_dialogue_flow(self) -> DialogueFlow:
        if not self.dialogue_flow:
            raise Exception(f"未发现对话流. ")
        return self.dialogue_flow

    def add_round(self):
        self.rounds += 1

    def add_dialogue_overflow_rounds(self):
        self.dialogue_overflow_rounds += 1

    def reset_dialogue_overflow_rounds(self):
        self.dialogue_overflow_rounds = 0

    def is_dialogue_overflow(self) -> bool:
        if self.dialogue_overflow_rounds > self.MAX_DIALOGUE_OVERFLOW_ROUNDS:
            return True
        return False
