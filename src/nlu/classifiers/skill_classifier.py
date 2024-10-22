# -*- coding: utf-8 -*-
# @Time : 2022/6/7 13:46
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : intent_classifier.py
from __future__ import annotations

import re
from src.common.message import SysMsg
from typing import Dict, Text, Any
from src.common.component.component import Component


class SkillClassifier:

    def build_res(self, per_skill_name: None or Text, msg: SysMsg) -> SysMsg:
        msg.set_component_skill_res(per_skill_name)
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
        return self.build_res(None, msg)
