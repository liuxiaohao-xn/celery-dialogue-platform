# -*- coding: utf-8 -*-
# @Time : 2022/11/7 16:30
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : dialogue_manage.py


from __future__ import annotations
from typing import Text, Dict, List
import copy
from src.dm.dialogue_manage.dialogue_state import DialogueState, NotCompleteDialogueState, \
    CompleteDialogueState, ViewDialogueState
from src.common.message import SysMsg
from src.common.domain.domain import Monitor


class DialogueStateCashChain:

    def __init__(self):
        self.dialogue_state_cash_chain: List[DialogueState] = []

    def pop(self, idx: int):
        self.dialogue_state_cash_chain.pop(idx)

    def append(self, dialogue_state: DialogueState):
        self.destroy(dialogue_state)
        self.dialogue_state_cash_chain.append(dialogue_state)

    def discard_invalid_dialogue_state(self):
        for idx, dialogue_state in enumerate(copy.deepcopy(self.dialogue_state_cash_chain)):
            if dialogue_state.discard():
                self.pop(idx)

    def empty(self) -> bool:
        return len(self.dialogue_state_cash_chain) == 0

    def match(self, msg: SysMsg) -> None or DialogueState:
        self.dialogue_state_cash_chain.sort(reverse=True)
        for state in self.dialogue_state_cash_chain:
            if state.activate(msg):
                return state
            # not activate state
            state.overflow_waited_rounds_increase()
        return None

    def destroy(self, dialogue_state: DialogueState) -> None:
        for idx, state in enumerate(copy.deepcopy(self.dialogue_state_cash_chain)):
            if state.UNIQUE_NO == dialogue_state.UNIQUE_NO:
                self.pop(idx)

    def monitor_dialogue(self, dialogue_state: DialogueState) -> None:
        self.destroy(dialogue_state)
        self.append(dialogue_state)

    def monitor_not_complete_dialogue(self, dialogue_state: DialogueState) -> None:
        # 销毁同类别的对话状态
        if not dialogue_state.end:
            self.monitor_dialogue(dialogue_state)

    def monitor_completed_dialogue(self, msg: SysMsg, dialogue_state: DialogueState) -> None:
        """对话完成时，对需要监听的对话状态进行监听."""
        if dialogue_state.end:
            monitor = msg.parsed_domain.cfg_intents.get(dialogue_state.intent).monitor
            if monitor:
                _c_msg = copy.deepcopy(msg)
                _c_msg.set_nlu_skill(dialogue_state.skill)
                _c_msg.set_nlu_intent(dialogue_state.intent)
                self.monitor_dialogue(
                    DialogueManage.make_complete_dialogue_state(_c_msg, monitor)
                )


class DialogueManage:
    # 缓存对话状态链
    DIALOGUE_STATE_CASH_CHAINS: Dict[Text, DialogueStateCashChain] = {}

    @classmethod
    def get_dialogue_state_cash_chain(cls, auth_id: Text) -> DialogueStateCashChain:
        cls.make_dialogue_state_cash_chain_if_not_exist(auth_id)
        return cls.DIALOGUE_STATE_CASH_CHAINS.get(auth_id)

    @classmethod
    def make_dialogue_state_cash_chain_if_not_exist(cls, auth_id: Text) -> None:
        if not cls.exist_dialogue_state_chain(auth_id):
            cls.DIALOGUE_STATE_CASH_CHAINS[auth_id] = DialogueStateCashChain()

    @classmethod
    def exist_dialogue_state_chain(cls, auth_id: Text) -> bool:
        return auth_id in cls.DIALOGUE_STATE_CASH_CHAINS

    @classmethod
    def discard_invalid_dialogue_state(cls, auth_id):
        dialogue_state_cash_chain = cls.get_dialogue_state_cash_chain(auth_id)
        dialogue_state_cash_chain.discard_invalid_dialogue_state()

    @classmethod
    def make_not_complete_dialogue_state(cls, msg: SysMsg) -> NotCompleteDialogueState:
        return NotCompleteDialogueState(msg)

    @classmethod
    def make_complete_dialogue_state(cls, msg: SysMsg, monitor: Monitor) -> CompleteDialogueState:
        return CompleteDialogueState(msg, monitor)

    @classmethod
    def make_view_dialogue_state(cls, msg: SysMsg, view_name: Text) -> ViewDialogueState:
        return ViewDialogueState(msg, view_name)
