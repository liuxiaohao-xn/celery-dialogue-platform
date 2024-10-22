# -*- coding: utf-8 -*-
# @Time : 2022/7/27 14:48
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : dialogue.py
from typing import Text
from src.common.component.component import Component
from src.common.message import SysMsg
from src.common.component.component_linked_list import ComponentLinkedList
from src.common.component.component_container import ComponentContainer
from src.nlu.classifiers.skill_classifier import SkillClassifier
from src.nlu.classifiers.intent_classifier import IntentClassifier
from src.dm.policy import BasePolicy
from src.dm.dialogue_manage.dialogue_manage import DialogueManage


class Dialogue:

    def __init__(self, msg: SysMsg,):
        self.msg = msg

    def get_skill_component(self):
        """get skill model by domain config"""
        return self.get_component_by_klass_name(self.msg.get_skill_model())

    def get_component_by_klass_name(self, klass_name: Text) -> Component:
        """get component instantiate by component klass name"""
        return self.klass_instantiate(
            ComponentContainer.get_register_klass(
                klass_name
            )
        )

    def get_last_skill(self) -> None or Text:
        """获取历史技能"""
        if DialogueManage.check_exist_dialogue_state_by_auth_id(self.msg.auth_id):
            return DialogueManage.get_dialogue_state_by_auth_id(self.msg.auth_id).skill
        return None

    def get_last_intent(self) -> None or Text:
        """获取历史意图"""
        if DialogueManage.check_exist_dialogue_state_by_auth_id(self.msg.auth_id):
            return DialogueManage.get_dialogue_state_by_auth_id(self.msg.auth_id).intent
        return None

    def flow_in_policy(self) -> SysMsg:
        """flow in policy component"""
        return BasePolicy.make_o(
            BasePolicy.get_default_config()
        ).process(self.msg)

    def klass_instantiate(self, klass):
        """组件实例化"""
        return klass.make_o(
            klass.get_default_config()
        )

    def run(self) -> SysMsg:
        """运行pipeline"""
        skill_component = self.get_skill_component()
        component_linked = ComponentLinkedList()
        component_linked.append(skill_component)
        cur_node = component_linked.head
        while cur_node:
            self.msg = cur_node.process(self.msg)
            if isinstance(cur_node.component, SkillClassifier):
                skill = self.msg.get_pre_skill()
                self.msg.set_component_skill_res(skill)
                last_skill = self.get_last_skill()
                if not skill and not last_skill:
                    self.msg.set_component_intent_res(None)
                    return self.flow_in_policy()
                else:
                    for klass_name in self.msg.get_pipeline_by_skill(skill if skill else last_skill):
                        component = self.get_component_by_klass_name(klass_name)
                        component_linked.append(component)
            elif isinstance(cur_node.component, IntentClassifier):
                intent = self.msg.get_pre_intent()
                self.msg.set_component_intent_res(intent)
                last_intent = self.get_last_intent()
                if not intent and not last_intent:
                    return self.flow_in_policy()
            cur_node = cur_node.nex
        return self.msg
