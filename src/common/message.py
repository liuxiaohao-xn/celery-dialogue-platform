# -*- coding: utf-8 -*-
# @Time : 2022/6/7 14:05
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : message.py
from __future__ import annotations
from typing import Dict, Text, Any, List
from src.common.domain.parser_domain import ParsedDomain, Slot, Entity, Intent
from src.common.constant import ComponentResKey, TermKey


class Message:
    def __init__(
            self,
            auth_id: Text,
            session_id: Text,
            text: Text,
    ) -> None:
        self.auth_id = auth_id
        self.session_id = session_id
        self.text = text

    """用户消息组件, 用于封装外部消息"""

    """
    Args:
        auth_id: 用户id.
        session_id: 用户会话id.
        text: 用户文本消息.
    """


class SysMsg(Message):
    """系统消息组件"""

    def __init__(
            self,
            auth_id: Text,
            session_id: Text,
            text: Text,
            parsed_domain: ParsedDomain,
    ) -> None:
        super().__init__(
            auth_id,
            session_id,
            text,
        )
        self.parsed_domain = parsed_domain
        self.res: Dict[Text, Dict[Text, Any]] = {}
        self.rsp = ""
        self.ask_aiui: bool = False
        self.exd_entities: List[Entity] = []
        self.end: bool = True  # 对话是否结束
        self.confirm: bool = False  # 业务意图是否确认
        """
        Args:
            res: sys一次交互预测结果
            parsed_domain: domain解析结果
            has_new_slot: 
                True: 追问阶段通知中台不去调用AIUI
                False: 追问阶段通知中台去调用AIUI
        """

    def not_end(self) -> SysMsg:
        self.end = False
        return self

    def get_intent_id(self) -> Text:
        from src import domain_map
        intent = self.get_pre_intent()
        return domain_map.get_intent_id(intent) if intent else ""

    def _not_found_res_key(self, component_res_key):
        """未找到组件结果key"""
        if not self.res or component_res_key not in self.res.keys():
            raise Exception(f"msg中未找到{component_res_key}.")

    def _not_found_term_key(self, component_res: Dict[Text, Any], term_key: Text):
        """问找到组件term_key"""
        if term_key not in component_res.keys():
            raise Exception(f"暂无预测结果, term_key: {term_key}.")

    def _get_component_res(self, component_res_key: Text) -> Dict[Text, Any]:
        """获取组件结果"""
        self._not_found_res_key(component_res_key)
        return self.res.get(component_res_key)

    def _get_term_res(self, component_res: Dict[Text, Any], term_key: Text):
        """获取组件term结果"""
        self._not_found_term_key(component_res, term_key)
        return component_res.get(term_key)

    def set_component_skill_res(self, pre_skill: None or Text) -> None:
        self.res.update(
            {
                ComponentResKey.SKILL_RES.value: {
                    TermKey.SKILL.value: pre_skill
                }
            }
        )

    def set_component_intent_res(self, pre_intent: None or Text) -> None:
        self.res.update(
            {
                ComponentResKey.NLU_CLS_RES.value: {
                    TermKey.INTENT.value: pre_intent
                }
            }
        )

    def set_component_entity_res(self, exd_entities: List[Entity]) -> None:
        self.res.update(
            {
                ComponentResKey.NLU_EXT_RES.value: {
                    TermKey.EXT_ENTITIES.value: exd_entities
                }
            }
        )

    def get_component_skill_res(self,) -> Dict[Text, Any]:
        """获取skill组件结果"""
        return self._get_component_res(
            component_res_key=ComponentResKey.SKILL_RES.value
        )

    def get_component_intent_res(self) -> Dict[Text, Any]:
        """获取intent组件结果"""
        return self._get_component_res(
            component_res_key=ComponentResKey.NLU_CLS_RES.value
        )

    def get_component_ext_res(self) -> Dict[Text, Any]:
        """获取intent组件结果"""
        return self._get_component_res(
            component_res_key=ComponentResKey.NLU_EXT_RES.value
        )

    def get_pre_skill(self) -> Text:
        """获取预测技能"""
        skill_res = self.get_component_skill_res()
        return self._get_term_res(
            skill_res,
            TermKey.SKILL.value
        )

    def get_pre_intent(self) -> Text:
        """获取预测意图"""
        intent_res = self.get_component_intent_res()
        return self._get_term_res(
            intent_res,
            TermKey.INTENT.value
        )

    def get_exd_entities(self) -> List[Entity]:
        """获取提取的实体"""
        ext_res = self.get_component_ext_res()
        return self._get_term_res(
            ext_res,
            TermKey.EXT_ENTITIES.value
        )

    def get_skill_model(self) -> Text:
        return self.parsed_domain.skill_model

    def get_pipeline_by_skill(self, skill: Text) -> List[Any]:
        """获取skill对应的pipeline"""
        return self.parsed_domain.parsed_domain.get(skill).pipeline

    def get_cfg_intents(self) -> Dict[Text, Intent]:
        """获取配置的意图"""
        return self.parsed_domain.parsed_intents

    def get_cfg_entities(self) -> Dict[Text, Entity]:
        """获取配置的实体"""
        return self.parsed_domain.parsed_entities

    def get_cfg_entity_by_name(self, name: Text) -> Entity:
        """通过名字获取配置实体"""
        return self.get_cfg_entities().get(name)

    def get_cfg_slots_by_intent(self, intent: Text) -> Dict[Text, Slot]:

        return self.parsed_domain.parsed_intents.get(intent).slots
