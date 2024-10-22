# -*- coding: utf-8 -*-
# @Time : 2022/6/7 9:17
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : intent_classifier.py
from typing import Dict, Text, Any
from src.nlu.classifiers.skill_classifier import SysMsg
from src.common.component.component import Component


class IntentClassifier:

    def build_res(self, pre_intent_name: None or Text, msg: SysMsg) -> SysMsg:
        msg.set_component_intent_res(pre_intent_name)
        return msg


class RuleClassifier(Component, IntentClassifier):
    """
        规则模型，用于场景少，场景相关性小的分类
    """

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        return {
            "hold_meeting": "hold_meeting"
        }

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> IntentClassifier:
        # todo 后续具体来实现算法
        rule_classifier = RuleClassifier()
        rule_classifier.model = config
        return rule_classifier

    def process(self, msg: SysMsg) -> SysMsg:
        return self.build_res("hold_meeting", msg)
