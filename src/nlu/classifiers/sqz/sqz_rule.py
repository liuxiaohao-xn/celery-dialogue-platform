# -*- coding: utf-8 -*-
# @Time : 2022/6/28 9:54
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : sqz_rule.py
from src.nlu.classifiers.skill_classifier import SkillClassifier
from src.nlu.classifiers.intent_classifier import IntentClassifier
from src.common.component.component import Component
from typing import Dict, Text, Any
from src.common.message import SysMsg
from src.nlu.classifiers.sqz.skill import Skill_Recognize, Intent_Recognize


class SkillRecognize(Component, SkillClassifier):
    skill_recognize = Skill_Recognize()

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        """获取自定义组件初始化需要的参数."""
        return {}

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> Component:
        """根据config创建一个ComponentBase对象, 其中config=cls.get_default_config().
            eg:
                ...
        """
        component = SkillRecognize()
        component.model = cls.skill_recognize
        return component

    def process(self, msg: SysMsg) -> SysMsg:
        skill = self.model.predict(msg.text)
        skill = skill if skill.strip() else None
        return self.build_res(skill, msg)


class MeetingIntentRecognize(Component, IntentClassifier):
    intent_recognize = Intent_Recognize("1")

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        """获取自定义组件初始化需要的参数."""
        return {}

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> Component:
        """根据config创建一个ComponentBase对象, 其中config=cls.get_default_config().
            eg:
                ...
        """
        component = MeetingIntentRecognize()
        component.model = cls.intent_recognize
        return component

    def process(self, msg: SysMsg) -> SysMsg:
        intent = self.model.predict(msg.text)
        intent = intent if intent.strip() else None
        return self.build_res(intent, msg)


class TakeWaterIntentRecognize(Component, IntentClassifier):
    intent_recognize = Intent_Recognize("2")

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        """获取自定义组件初始化需要的参数."""
        return {}

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> Component:
        """根据config创建一个ComponentBase对象, 其中config=cls.get_default_config().
            eg:
                ...
        """
        component = TakeWaterIntentRecognize()
        component.model = cls.intent_recognize
        return component

    def process(self, msg: SysMsg) -> SysMsg:
        intent = self.model.predict(msg.text)
        intent = intent if intent.strip() else None
        return self.build_res(intent, msg)


class CallIntentRecognize(Component, IntentClassifier):
    intent_recognize = Intent_Recognize("3")

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        """获取自定义组件初始化需要的参数."""
        return {}

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> Component:
        """根据config创建一个ComponentBase对象, 其中config=cls.get_default_config().
            eg:
                ...
        """
        component = CallIntentRecognize()
        component.model = cls.intent_recognize
        return component

    def process(self, msg: SysMsg) -> SysMsg:
        intent = self.model.predict(msg.text)
        intent = intent if intent.strip() else None
        return self.build_res(intent, msg)


class SystemIntentRecognize(Component, IntentClassifier):
    intent_recognize = Intent_Recognize("4")

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        """获取自定义组件初始化需要的参数."""
        return {}

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> Component:
        """根据config创建一个ComponentBase对象, 其中config=cls.get_default_config().
            eg:
                ...
        """
        component = CallIntentRecognize()
        component.model = cls.intent_recognize
        return component

    def process(self, msg: SysMsg) -> SysMsg:
        intent = self.model.predict(msg.text)
        intent = intent if intent.strip() else None
        return self.build_res(intent, msg)
