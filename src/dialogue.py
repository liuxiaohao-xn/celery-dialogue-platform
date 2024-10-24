# -*- coding: utf-8 -*-
# @Time : 2022/7/27 14:48
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : dialogue.py
from src.common.message import SysMsg
from src.common.utils import get_component_by_klass_name
from src.common.component.component_linked_list import ComponentLinkedList
from src.nlu.classifiers.skill_classifier import SkillClassifier
from src.nlu.classifiers.intent_classifier import IntentClassifier
from src.dm.policy import BasePolicy
from src.dm.dialogue_manage.dialogue_manage import DialogueManage


class Dialogue:

    def __init__(self, msg: SysMsg,):
        self.msg = msg

    def get_skill_component(self):
        """get skill model by domain config"""
        return get_component_by_klass_name(
            self.msg.get_nlu_skill_model()
        )

    def flow_in_policy(self) -> SysMsg:
        """flow in policy component"""
        return BasePolicy.make_o(
            BasePolicy.get_default_config()
        ).process(self.msg)

    def ext_entities_from_cashed(self):
        dialogue_state_cash_chain = DialogueManage.get_dialogue_state_cash_chain(self.msg.auth_id)
        dialogue_state_cash_chain.discard_invalid_dialogue_state()
        for dialogue_state in dialogue_state_cash_chain.dialogue_state_cash_chain:
            self.msg = dialogue_state.ext(self.msg)

    def run(self) -> SysMsg:
        # 构造pipeline
        component_linked = ComponentLinkedList()
        component_linked.append(self.get_skill_component())
        cur_node = component_linked.head
        while cur_node:
            self.msg = cur_node.process(self.msg)
            if isinstance(cur_node.component, SkillClassifier):
                if not self.msg.get_nlu_skill():
                    self.ext_entities_from_cashed()
                    return self.flow_in_policy()
                else:
                    for klass_name in self.msg.get_nlu_skill_pipeline(
                            self.msg.get_nlu_skill()
                    ):
                        component = get_component_by_klass_name(klass_name)
                        component_linked.append(component)
            elif isinstance(cur_node.component, IntentClassifier):
                if not self.msg.get_nlu_intent():
                    self.ext_entities_from_cashed()
                    return self.flow_in_policy()
            cur_node = cur_node.nex
        return self.msg
