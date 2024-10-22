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
from src.common.constant import SystemIntent
from src.common.component.component import Component
from src.dm.dialogue_manage.dialogue_manage import DialogueManage
from src.dm.dialogue_manage.dialogue_state import DialogueState
from src.dm.dialogue_flow.dialogue_flow import DialogueFlow

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

    def get_last_dialogue_state(self, msg: SysMsg) -> DialogueState:
        """获取对话状态"""
        if not DialogueManage.check_exist_dialogue_state_by_auth_id(msg.auth_id):
            dialogue_state = DialogueManage.make_a_new_dialogue_state(msg)
        else:
            dialogue_state = DialogueManage.get_dialogue_state_by_auth_id(msg.auth_id)
        return dialogue_state

    def destroy_dialogue_state_by_session_id(self, session_id: Text):
        """通过session_id销毁对话状态"""
        DialogueManage.del_dialogue_state_by_session_id(session_id)

    def cash_dialogue_flow(self, dialogue_state: DialogueState, dialogue_flow: DialogueFlow):
        """缓存对话流"""
        dialogue_state.dialogue_flow = dialogue_flow

    def switch_intent(self, msg: SysMsg, dialogue_state: DialogueState) -> bool:
        """切换意图"""
        if msg.get_pre_intent() == dialogue_state.intent:
            return False
        return True

    def return_and_ask_aiui(self, msg: SysMsg) -> SysMsg:
        msg.set_component_skill_res(None)
        msg.set_component_intent_res(None)
        msg.ask_aiui = True
        return msg

    def logging_newline(self, msg: SysMsg, switch=False):
        if not DialogueManage.check_exist_dialogue_state_by_auth_id(msg.auth_id) or switch:
            logger.info(f"\n##### 新会话 #####")
        else:
            if DialogueManage.get_dialogue_state_by_auth_id(msg.auth_id).timeout():
                logger.info(f"\n##### 会话过期, 开启新会话 #####")
        logger.info(f"asr: {msg.text}")

    def process(self, msg: SysMsg) -> SysMsg:
        # test
        # if msg.text == "第1个":
        #     msg.set_component_skill_res("common_skill")
        #     msg.set_component_intent_res("select_num")
        # if msg.text == "是的":
        #     msg.set_component_skill_res("common_skill")
        #     msg.set_component_intent_res("yes")
        # if msg.text == "没有了":
        #     msg.set_component_skill_res("common_skill")
        #     msg.set_component_intent_res("no")
        # if msg.text == "取消会议":
        #     msg.set_component_skill_res("hold_meeting")
        #     msg.set_component_intent_res("cancel_meeting")
        exist_dialogue_state = DialogueManage.check_exist_dialogue_state_by_auth_id(msg.auth_id)
        # 对话溢出
        if exist_dialogue_state:
            last_dialogue_state = DialogueManage.get_dialogue_state_by_auth_id(msg.auth_id)
            if last_dialogue_state.is_dialogue_overflow():
                logger.info(f"对话溢出")
                DialogueManage.del_dialogue_state_by_session_id(last_dialogue_state.session_id)
                exist_dialogue_state = False
        self.logging_newline(msg)
        # 未中意图 + 无历史对话
        if not msg.get_pre_intent() and not exist_dialogue_state:
            return self.return_and_ask_aiui(msg)
        # 中意图 + 无历史对话
        elif msg.get_pre_intent() and not exist_dialogue_state:
            # 系统意图, 转AIUI
            if msg.get_pre_intent() in SystemIntent.system_intent():
                return self.return_and_ask_aiui(msg)
            last_dialogue_state = DialogueManage.make_a_new_dialogue_state(msg)
        # 未中意图 + 历史对话
        elif not msg.get_pre_intent() and exist_dialogue_state:
            last_dialogue_state = DialogueManage.get_dialogue_state_by_auth_id(msg.auth_id)
            # 对话过期，转AIUI
            if last_dialogue_state.timeout():
                DialogueManage.del_dialogue_state_by_session_id(last_dialogue_state.session_id)
                return self.return_and_ask_aiui(msg)
        # 中意图 + 历史对话
        elif msg.get_pre_intent() and exist_dialogue_state:
            last_dialogue_state = DialogueManage.get_dialogue_state_by_auth_id(msg.auth_id)
            # 对话过期
            if last_dialogue_state.timeout():
                DialogueManage.del_dialogue_state_by_session_id(last_dialogue_state.session_id)
                # 中系统意图，转AIUI
                if msg.get_pre_intent() in SystemIntent.system_intent():
                    return self.return_and_ask_aiui(msg)
                # 中非系统意图，新建对话
                else:
                    last_dialogue_state = DialogueManage.make_a_new_dialogue_state(msg)
            # 对话非过期
            else:
                # 中取消会话意图，取消会话并返回
                from src.dm.actions.action import CancelAction
                if msg.get_pre_intent() == SystemIntent.CANCEL:
                    intent = last_dialogue_state.intent
                    msg = CancelAction().run(msg, intent)
                    DialogueManage.del_dialogue_state_by_session_id(last_dialogue_state.session_id)
                    return msg

        # 激活历史对话流
        last_dialogue_flow = last_dialogue_state.get_dialogue_flow()
        if last_dialogue_flow.activate(msg, last_dialogue_state.dialogue_state_entity_info):
            last_dialogue_state.add_round()  # 轮数+1
            last_dialogue_state.update_start_time()  # 更新对话开始时间
            last_dialogue_state.reset_dialogue_overflow_rounds()  # 重置历史对话溢出轮数
            while last_dialogue_flow:
                last_dialogue_flow.process(msg, last_dialogue_state.dialogue_state_entity_info)
                if last_dialogue_flow.end:
                    # 流程结束
                    if not last_dialogue_flow.next_flow:
                        break
                    last_dialogue_flow = last_dialogue_flow.next_flow
                else:
                    self.cash_dialogue_flow(last_dialogue_state, last_dialogue_flow)
                    return last_dialogue_flow.action(msg.not_end())  # 未结束, 返回用户
            msg = last_dialogue_flow.action(msg)
            self.destroy_dialogue_state_by_session_id(last_dialogue_state.session_id)
        else:
            # 未激活 + 无意图
            if not msg.get_pre_intent() or msg.get_pre_intent() in SystemIntent.system_intent():
                last_dialogue_state.add_dialogue_overflow_rounds()  # 跳转AIUI, 历史对话溢出轮数 +1
                return self.return_and_ask_aiui(msg)
            # 创建新的对话状态
            new_dialogue_state = DialogueManage.make_a_new_dialogue_state(msg)
            new_dialogue_flow = new_dialogue_state.get_dialogue_flow()
            new_dialogue_flow.activate(msg, new_dialogue_state.dialogue_state_entity_info)
            new_dialogue_state.add_round()  # 轮数+1
            new_dialogue_state.update_start_time()  # 更新对话开始时间
            while new_dialogue_flow:
                new_dialogue_flow.process(msg, new_dialogue_state.dialogue_state_entity_info)
                if new_dialogue_flow.end:
                    if not new_dialogue_flow.next_flow:
                        break
                    new_dialogue_flow = new_dialogue_flow.next_flow
                else:
                    # 销毁旧的对话
                    self.destroy_dialogue_state_by_session_id(last_dialogue_state.session_id)
                    # 缓存新对话流
                    self.cash_dialogue_flow(new_dialogue_state, new_dialogue_flow)
                    self.logging_newline(msg, switch=True)
                    return new_dialogue_flow.action(msg.not_end())
            last_dialogue_state.add_dialogue_overflow_rounds()  # 中其它意图, 历史对话溢出轮数 +1
            msg = new_dialogue_flow.action(msg)
            self.destroy_dialogue_state_by_session_id(new_dialogue_state.session_id)
        return msg
