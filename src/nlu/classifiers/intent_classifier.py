# -*- coding: utf-8 -*-
# @Time : 2022/6/7 9:17
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : intent_classifier.py
from __future__ import annotations
from typing import Dict, Text, Any
import json
import os
import regex as re
from src.nlu.classifiers.skill_classifier import SysMsg
from src.common.component.component import Component


cur_path = os.path.dirname(__file__)


class IntentClassifier:

    def build_res(self, intent: Text, msg: SysMsg) -> SysMsg:
        msg.set_nlu_intent(intent)
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


class DomesticIntentClassifier(Component, IntentClassifier):
    """技能分类器"""

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        res = {}
        for intent_block in json.load(
            open(os.path.join(cur_path, 'intent.json'), encoding='utf-8-sig'),
        ):
            res.update(
                {
                    intent_block["intent_mark"]: [re.compile(item) for item in intent_block["intent_corpus"]]
                }
            )

        return res

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> DomesticIntentClassifier:
        # todo 需要判断config.keys()是否都在配置的skills中
        #   ...
        intent_classifier = DomesticIntentClassifier()
        intent_classifier.model = config
        return intent_classifier

    def process(self, msg: SysMsg) -> SysMsg:
        """技能分类，执行完此函数，msg需要绑定skill_name属性"""
        for intent_name, re_cs in self.model.items():
            for re_c in re_cs:
                m = re_c.search(msg.text)
                if m and m.group():
                    print(intent_name)
                    return self.build_res(intent_name, msg)
        return self.build_res("", msg)


if __name__ == "__main__":
    res = DomesticIntentClassifier.make_o(
        DomesticIntentClassifier.get_default_config()
    ).process(
        SysMsg('', '', '拍下照', None)
    )
