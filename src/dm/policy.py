# -*- coding: utf-8 -*-
# @Time : 2022/6/13 10:18
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : policy.py
from __future__ import annotations

from typing import Dict, Text, Any, List
import logging
from collections import defaultdict
from src.common.message import SysMsg
from src.common.component.component import Component
from src.dm.dialogue_manage.dialogue_manage import DialogueManage

logger = logging.getLogger(__name__)


class Policy(object):
    """action决策器"""
    ...


class BasePolicy(Component, Policy):

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        return defaultdict()

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> BasePolicy:
        return BasePolicy()

    def process(self, msg: SysMsg) -> SysMsg:
        # 丢弃无效的对话状态
        DialogueManage.discard_invalid_dialogue_state(msg.auth_id)
        # 匹配对话状态，如果匹配成功，则执行匹配的对话状态
        dialogue_state_cash_chain = DialogueManage.get_dialogue_state_cash_chain(msg.auth_id)
        dialogue_state = dialogue_state_cash_chain.match(msg)
        if dialogue_state:
            msg = dialogue_state.process(msg)
            if dialogue_state.end:
                dialogue_state_cash_chain.destroy(dialogue_state)
        else:
            # 未击中意图
            if not msg.get_nlu_intent():
                msg.rsp = 'hit none'
            # 击中公共意图
            elif msg.hit_system_intent():
                msg.rsp = 'hit system intent without content'
            # 击中新意图
            if msg.get_nlu_intent() and not msg.hit_system_intent():
                dialogue_state = DialogueManage.make_not_complete_dialogue_state(msg)
                msg = dialogue_state.process(msg)
                # 对话未结束
                dialogue_state_cash_chain.monitor_not_complete_dialogue(dialogue_state)
        # 监控已结束对话
        if dialogue_state:
            dialogue_state_cash_chain.monitor_completed_dialogue(msg, dialogue_state)
        return msg

