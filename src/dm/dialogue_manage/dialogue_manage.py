# -*- coding: utf-8 -*-
# @Time : 2022/8/1 13:39
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : dialogue_manage.py
from __future__ import annotations
from typing import Text, Dict
from src.common.message import SysMsg
import src.common.utils as utils
from src.dm.dialogue_manage.dialogue_state import DialogueState


class DialogueManage:
    # 缓存的对话状态, 一个用户只支持缓存一个对话状态
    CASH_DIALOGUE_STATE: Dict[Text, DialogueState] = {}
    # 对话缓存轮数
    CASH_DIALOGUE_ROUNDS = 3

    @classmethod
    def check_exist_dialogue_state_by_auth_id(cls, auth_id: Text):
        for session_id, dialogue_state in cls.CASH_DIALOGUE_STATE.items():
            if auth_id == session_id[:len(auth_id)]:
                return True
        return False

    @classmethod
    def check_exist_dialogue_state_by_session_id(cls, session_id: Text):
        if session_id in cls.CASH_DIALOGUE_STATE.keys():
            return True
        return False

    @classmethod
    def get_dialogue_state_by_auth_id(cls, auth_id: Text) -> DialogueState:
        for session_id, dialogue_state in cls.CASH_DIALOGUE_STATE.items():
            if auth_id == session_id[:len(auth_id)]:
                return dialogue_state
        raise Exception(f"用户{auth_id}不存在对话状态!")

    @classmethod
    def get_dialogue_state_by_session_id(cls, session_id: Text) -> DialogueState:
        return cls.CASH_DIALOGUE_STATE.get(session_id)

    @classmethod
    def make_a_new_dialogue_state(cls, msg: SysMsg) -> DialogueState:
        dialogue_state = DialogueState(
            session_id=utils.build_session_id_by_auth_id(msg.auth_id),
            start_time=utils.get_cur_timestamp(),
            msg=msg,
        )
        cls.CASH_DIALOGUE_STATE[dialogue_state.session_id] = dialogue_state
        return dialogue_state

    @classmethod
    def del_dialogue_state_by_session_id(cls, session_id: Text) -> None:
        if not cls.check_exist_dialogue_state_by_session_id(session_id):
            raise Exception(f"{session_id}不存在!")
        cls.CASH_DIALOGUE_STATE.pop(session_id)




