# -*- coding: utf-8 -*-
# @Time : 2022/11/14 15:10
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : message.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Text, Any, List
from src.common.domain.domain import Entity, Slot, Entity, Intent
from src.common.domain.parser_domain import ParsedDomain


@dataclass
class ExdInfo:
    skill: Text = field(default_factory=Text)
    intent: Text = field(default_factory=Text)
    entities: List[Entity] = field(default_factory=list)


@dataclass
class SysRsp:
    rsp: Text = field(default_factory=Text)
    end: bool = field(default_factory=bool)


class SysMsg:
    def __init__(
            self,
            auth_id: Text,
            text: Text,
            parsed_domain: ParsedDomain,
    ) -> None:
        self.auth_id = auth_id
        self.text = text
        self.parsed_domain = parsed_domain
        self.exd_info: ExdInfo = ExdInfo()
        self.rsp: Text = ''
        self.end: bool = False

    def set_nlu_skill(self, skill: Text) -> None:
        self.exd_info.skill = skill

    def set_nlu_intent(self, intent: Text) -> None:
        self.exd_info.intent = intent

    def set_nlu_entities(self, entities: List[Entity]) -> None:
        self.exd_info.entities = entities

    def get_nlu_skill(self) -> Text:
        return self.exd_info.skill

    def get_nlu_intent(self) -> Text:
        return self.exd_info.intent

    def get_nlu_exd_entities(self) -> List[Entity]:
        return self.exd_info.entities

    def get_nlu_skill_model(self) -> Text:
        return self.parsed_domain.skill_model

    def get_nlu_skill_pipeline(self, skill: Text) -> List[Any]:
        return self.parsed_domain.cfg_skills.get(skill).pipeline

    def get_o_entity(self, entity_name: Text) -> Entity:
        return self.parsed_domain.cfg_entities.get(
            entity_name
        )

    def get_o_intent(self, intent_name: Text) -> Intent:
        return self.parsed_domain.cfg_intents.get(
            intent_name
        )

    def get_slot_name_by_entity(self, entity: Entity) -> Text:
        intent_obj = self.get_o_intent(
            self.get_nlu_intent()
        )
        for slot_name, slot in intent_obj.slots.items():
            for entity_name in slot.polymorphism:
                if entity_name == entity.en:
                    return slot_name
        raise Exception(f"{entity.en}未找到对应的slot_name.")

    def get_intent_slots(self, intent_name: Text) -> Dict[Text, Slot]:
        return self.get_o_intent(intent_name).slots

    def get_intent_target_slot(self, intent: Text, slot_name: Text) -> Slot:
        return self.get_intent_slots(
            intent
        ).get(slot_name)

    def hit_system_intent(self) -> True:
        # todo 是否集中公共意图
        if self.get_nlu_skill() == "system":
            return True
        return False


if __name__ == "__main__":
    sm = SysMsg('11', 'test')
    print(sm)
