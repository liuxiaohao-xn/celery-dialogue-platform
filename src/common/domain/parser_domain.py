# -*- coding: utf-8 -*-
# @Time : 2022/6/9 18:49
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : parser_domain.py
import os.path
from typing import Dict, Any, Text, List
from src.common.domain.domain import Skill, Entity, Intent, Domain, Slot, Flow
from src.common.utils import read_yaml_file


class ParsedDomain:
    """解析domain.yml文件"""

    def __init__(self, domain_dir: Text) -> None:
        self.skill_model = "SkillRecognize"
        self.parsed_domain: Dict[Text, Skill] = self._parse_domain(
            read_yaml_file(os.path.join(domain_dir, "domain.yml"))
        )["sec_skill"]
        self.intent_map_skill = self._intent_map_skill()
        self.parsed_intents: Dict[Text, Intent] = self._parse_intents(
            read_yaml_file(os.path.join(domain_dir, "intent.yml"))
        )
        self.parsed_entities: Dict[Text, Entity] = self._parse_entities(
            read_yaml_file(os.path.join(domain_dir, "entity.yml"))
        )

    def _intent_map_skill(self):
        _intent_m_skill = {}
        for skill, skill_obj in self.parsed_domain.items():
            for intent in skill_obj.intents:
                _intent_m_skill[intent] = skill
        return _intent_m_skill

    def _set_attrs_en_name(self, attrs: Dict[Text, Any], name: Text):
        """给domain设置en name"""
        attrs["en"] = name
        return attrs

    def _parse_domain_attrs(self, required_attrs: List[Text], attrs: Dict[Text, Any]):
        """解析domain属性，返回必要属性和非必要属性"""
        required_attrs_dic, not_required_attrs_dic = {}, {}
        for required_attr in required_attrs:
            if required_attr not in attrs.keys():
                raise AttributeError(f"缺少必要属性:{required_attr}，请先在yaml文件中配置")
            required_attrs_dic[required_attr] = attrs.pop(required_attr)
        not_required_attrs_dic = attrs
        return required_attrs_dic, not_required_attrs_dic

    def _bind_not_required_attrs(self, domain: Domain, not_required_attrs_dic: Dict[Text, Any]):
        """domain绑定非必要属性"""
        for name, val in not_required_attrs_dic.items():
            setattr(domain, name, val)
        return domain

    def _parse_domain(self, domain_col: Dict[Text, Any]) -> Dict[Text, Dict]:
        """domain解析"""
        domain_dic = {}
        for domain_name, skills in domain_col.items():
            parsed_skills = self._parse_skills(skills)
            domain_dic[domain_name] = parsed_skills
        return domain_dic

    def _parse_skills(self, skill_col: Dict[Text, Any]) -> Dict[Text, Skill]:
        """从YML文件中解析技能"""
        skill_dic = {}
        for skill_name, attrs in skill_col.items():
            try:
                self._set_attrs_en_name(attrs, skill_name)
                required_attrs_dic, not_required_attrs_dic = self._parse_domain_attrs(Skill.required_attrs(), attrs)
                skill = Skill.make_o(**required_attrs_dic)
                skill = self._bind_not_required_attrs(skill, not_required_attrs_dic)
                skill_dic[skill_name] = skill
            except Exception:
                raise Exception(f"解析skill: {skill_name}失败")
        return skill_dic

    def _parse_entities(self, entity_col: Dict[Text, Dict[Text, Any]]) -> Dict[Text, Entity]:
        """从YML文件中解析实体"""
        entity_dict = {}
        for entity_name, attrs in entity_col.items():
            try:
                self._set_attrs_en_name(attrs, entity_name)
                required_attrs_dic, not_required_attrs_dic = self._parse_domain_attrs(Entity.required_attrs(), attrs)
                entity = Entity.make_o(**required_attrs_dic)
                entity = self._bind_not_required_attrs(entity, not_required_attrs_dic)
                entity_dict[entity_name] = entity
            except Exception:
                raise Exception(f"解析entity: {entity_name}失败")
        return entity_dict

    def _parse_intents(self, intent_col: Dict[Text, Any]) -> Dict[Text, Intent]:
        """从YML文件中解析意图"""
        intent_dict = {}
        for intent_name, attrs in intent_col.items():
            try:
                self._set_attrs_en_name(attrs, intent_name)
                required_attrs_dic, not_required_attrs_dic = self._parse_domain_attrs(Intent.required_attrs(), attrs)
                intent = Intent.make_o(**required_attrs_dic)
                intent: Intent = self._bind_not_required_attrs(intent, not_required_attrs_dic)
                if intent.slots:
                    intent.slots = self._parse_intent_slots(intent.slots)
                intent.success_flow = self._parse_flow("success_flow", intent.success_flow)
                if intent.cancel_flow:
                    intent.cancel_flow = self._parse_flow("cancel_flow", intent.cancel_flow)
                intent_dict[intent_name] = intent
            except Exception:
                raise Exception(f"解析entity: {intent_name}失败")

        return intent_dict

    def _parse_intent_slots(self, slots: Dict[Text, Slot]):
        """解析意图绑定的slot"""
        slots_dict = {}
        for slot_name, attrs in slots.items():
            try:
                self._set_attrs_en_name(attrs, slot_name)
                required_attrs_dic, not_required_attrs_dic = self._parse_domain_attrs(Slot.required_attrs(), attrs)
                slot: Slot = Slot.make_o(**required_attrs_dic)
                slot = self._bind_not_required_attrs(slot, not_required_attrs_dic)
                # slot bind missing action
                if slot.flows:
                    slot.flows = self._parse_slot_flows(slot.flows)
            except Exception:
                raise KeyError(f"未找到slot: {slot_name}，请先在YML文件中配置.")
            slots_dict[slot_name] = slot
        return slots_dict

    def _parse_slot_flows(self, flows: Dict[Text, Flow]) -> Dict[Text, Flow]:
        flows_dict = {}
        for flow_name, attrs in flows.items():
            try:
                flow: Flow = self._parse_flow(flow_name, attrs)
            except Exception:
                raise KeyError(f"未找到flow: {flow_name}，请先在YML文件中配置.")
            flows_dict[flow_name] = flow
        return flows_dict

    def _parse_flow(self, flow_name: Text, attrs: [List, Any]) -> Flow:
        try:
            attrs["name"] = flow_name
            required_attrs_dic, not_required_attrs_dic = self._parse_domain_attrs(Flow.required_attrs(), attrs)
            flow: Flow = Flow.make_o(**required_attrs_dic)
            flow = self._bind_not_required_attrs(flow, not_required_attrs_dic)
            return flow
        except Exception:
            raise KeyError(f"未找到flow: {flow_name}，请先在YML文件中配置.")


if __name__ == "__main__":
    path = r"D:\job\git\yh-robot-nlp\resource"
    parsed_domain = ParsedDomain(path)
    print(parsed_domain)
