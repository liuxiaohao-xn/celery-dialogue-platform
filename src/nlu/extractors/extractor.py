# -*- coding: utf-8 -*-
# @Time : 2022/6/7 16:48
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : extractor_bak.py
from __future__ import annotations
import copy
import logging
from src.common.message import SysMsg
from typing import List, Text
from src.common.domain.domain import Slot, Entity, Intent

logger = logging.getLogger(__name__)


class Extractor(object):
    """An entity extractor."""

    # def get_cfg_intent(self, msg: SysMsg) -> Intent:
    #     intent: Intent = msg.parsed_domain.parsed_intents.get(
    #         msg.get_pre_intent()
    #     )
    #     return intent
    #
    # def slot_bind_entity(self, entity: Entity, intent: Intent) -> Slot:
    #     for _, slot in intent.slots.items():
    #         if entity.en in slot.polymorphism:
    #             cp_slot = copy.deepcopy(slot)
    #             cp_slot.filling_entity = entity
    #             return cp_slot
    #     raise Exception(f"槽位{slot.en}.polymorphism不存在{entity.en}!")

    # def build_res(
    #         self,
    #         msg: SysMsg,
    #         ext_infos: List,
    # ) -> SysMsg:
    #     """一次交互的结果."""
    #     intent: Intent = self.get_cfg_intent()
    #     ext_slots = []
    #     if intent.slots:
    #         for ext_info in ext_infos:
    #             entity: Entity = copy.deepcopy(msg.parsed_domain.parsed_entities.get(ext_info[0]))
    #             entity.set_ext_info(
    #                 ext_info[1],
    #                 ext_info[2],
    #                 ext_info[3]
    #             )
    #             ext_slots.append(self.slot_bind_entity(entity, intent))
    #     msg.set_component_slot_res(ext_slots)
    #     return msg

    def build_res(
            self,
            msg: SysMsg,
            exd_infos: List
    ) -> SysMsg:
        """一次交互的结果, exd_infos格式: [(name, value, start_pos, end_pos), ...]."""
        exd_entities: List[Entity] = []
        for exd_info in exd_infos:
            entity: Entity = copy.deepcopy(msg.get_cfg_entity_by_name(exd_info[0]))
            entity.set_ext_info(exd_info[1], exd_info[2], exd_info[3])
            exd_entities.append(entity)
        msg.set_component_entity_res(exd_entities)
        return msg

