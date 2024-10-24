# -*- coding: utf-8 -*-
# @Time : 2022/6/7 13:46
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : intent_classifier.py
from __future__ import annotations

import regex as re
import json
import os
from src.common.message import SysMsg
from typing import Dict, Text, Any
from src.common.component.component import Component


cur_path = os.path.dirname(__file__)


class SkillClassifier:

    def build_res(self, skill: Text, msg: SysMsg) -> SysMsg:
        msg.set_nlu_skill(skill)
        return msg


class SECSkillClassifier(Component, SkillClassifier):
    """技能分类器"""

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        return {
            "meeting": re.compile(r"会议|开.{0,10}会"),
            "take_water": re.compile(r"[拿|取].{0,10}[瓶|水]"),
            # "call": ""
        }

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> SkillClassifier:
        # todo 需要判断config.keys()是否都在配置的skills中
        #   ...
        skill_classifier = SECSkillClassifier()
        skill_classifier.model = config
        return skill_classifier

    def process(self, msg: SysMsg) -> SysMsg:
        """技能分类，执行完此函数，msg需要绑定skill_name属性"""
        for skill_name, rec in self.model.items():
            m = rec.search(msg.text)
            if m and m.group():
                return self.build_res(skill_name, msg)
        return self.build_res("", msg)


class DomesticSkillClassifier(Component, SkillClassifier):
    """技能分类器"""

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        res = {}
        for skill_block in json.load(
            open(os.path.join(cur_path, 'skill.json'), encoding=' utf-8-sig'),
        ):
            res.update(
                {
                    skill_block["skill_mark"]: [re.compile(item) for item in skill_block["skill_corpus"]]
                }
            )

        return res

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> DomesticSkillClassifier:
        # todo 需要判断config.keys()是否都在配置的skills中
        #   ...
        skill_classifier = DomesticSkillClassifier()
        skill_classifier.model = config
        return skill_classifier

    def process(self, msg: SysMsg) -> SysMsg:
        """技能分类，执行完此函数，msg需要绑定skill_name属性"""
        for skill_name, re_cs in self.model.items():
            for re_c in re_cs:
                m = re_c.search(msg.text)
                if m and m.group():
                    return self.build_res(skill_name, msg)
        return self.build_res("", msg)


if __name__ == "__main__":
    res = DomesticSkillClassifier.make_o(
        DomesticSkillClassifier.get_default_config()
    ).process(
        SysMsg('', '', '拍下照', None)
    )
