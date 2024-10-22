# -*- coding: utf-8 -*-
# @Time : 2022/8/8 13:48
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : dialogue_entity_info.py
from typing import Text, Dict, List, Tuple
from src.common.domain.domain import Slot, Entity


class SlotMissingEntityInfo:

    def __init__(
            self,
            missing_slots: List[Slot],
    ):
        self.missing_slots = self._sort(missing_slots)
        self.exd_entities: List[Entity] = []

    def _sort(self, slots: List[Slot]) -> List[Slot]:
        """槽位优先级倒排序, 5->4->3->2->1->0"""
        slots.sort(key=lambda slot: slot.id, reverse=True)
        return slots

    def append_exd_entities(self, exd_entities: List[Entity]) -> None:
        """追加实体集"""
        for entity in exd_entities:
            self.append_exd_entity(entity)

    def append_exd_entity(self, entity: Entity) -> None:
        """追加实体"""
        if entity not in self.exd_entities:
            self.exd_entities.append(entity)

    def pop_missing_slot(self) -> None or Slot:
        if not self.missing_slots:
            return None
        missing_slot = self.missing_slots.pop()
        while self.missing_slots and missing_slot.id == 0:
            missing_slot = self.missing_slots.pop()
        return None if missing_slot.id == 0 else missing_slot

    def entity_is_belong_missing_slot(self, entity: Entity) -> bool:
        for slot in self.missing_slots:
            if entity.en in slot.polymorphism:
                return True
        return False

    def get_entities_linked_slot(self, slot: Slot):
        """获取槽位关联的实体"""
        entities = []
        for entity in self.exd_entities:
            if entity.en in slot.polymorphism:
                entities.append(entity)
        return entities

    def del_entity(self, entity: Entity):
        self.exd_entities.remove(entity)

    def del_entities(self, entities: List[Entity]):
        for entity in entities:
            self.del_entity(entity)


class PendingVerifiedEntityInfo:

    def __init__(
            self,
            slot_missing_entity_info: SlotMissingEntityInfo,
            pending_verified_slot: Slot,
            not_verified_entities: List[Entity]
    ):
        self.slot_missing_entity_info = slot_missing_entity_info
        self.pending_verified_slot = pending_verified_slot
        self.not_verified_entities = not_verified_entities

    def clean_not_verified_entities(self) -> None:
        self.not_verified_entities = []

    def append_not_verified_entities(self, exd_entities: List[Entity]) -> None:
        """更新未验证的实体"""
        self.clean_not_verified_entities()
        for entity in exd_entities:
            # 获取当前槽位需要验证的实体
            if entity.en in self.pending_verified_slot.polymorphism:
                self.not_verified_entities.append(entity)
            # 获取缺失槽位对应的实体
            elif self.slot_missing_entity_info.entity_is_belong_missing_slot(entity):
                self.slot_missing_entity_info.append_exd_entity(entity)


class RepeatVerifiedEntityInfo:

    def __init__(
            self,
            repeat_slot: Slot,
            repeat_verified_entities: List[Tuple[Entity, List[Text]]]
    ):
        self.repeat_slot: Slot = repeat_slot
        self.repeat_verified_entities = repeat_verified_entities
        self.select_num: int = 0

    def pop_repeat_verified_entity(self) -> None or Tuple[Entity, List[Text]]:
        if not self.repeat_verified_entities:
            return None
        return self.repeat_verified_entities.pop(0)

    def is_select_overflow(self, repeat_verified_entity: Tuple[Entity, List[Text]]) -> bool:
        if 0 < self.select_num <= len(repeat_verified_entity[1]):
            return False
        return True

    def entity_redress(self, repeat_entity: Tuple[Entity, List[Text]]) -> Entity:
        entity, candidate_values = repeat_entity
        entity.verify_value = candidate_values[self.select_num - 1]
        return entity


class SlotFollowUpEntityInfo:

    def __init__(self, follow_up_slot: Slot):
        self.follow_up_slot = follow_up_slot
        self.follow_up_entities: List[Entity] = []

    def append_follow_up_entities(self, entities: List[Entity]) -> None:
        for entity in entities:
            if entity.en in self.follow_up_slot.polymorphism:
                self.follow_up_entities.append(entity)


class DialogueStateEntityInfo:
    """对话状态实体信息"""

    def __init__(
            self,
            cfg_slots: Dict[Text, Slot],
    ):
        self.cfg_slots = cfg_slots

        self.slot_missing_entity_info = SlotMissingEntityInfo(list(cfg_slots.values()))
        self.pending_verified_entity_info: PendingVerifiedEntityInfo = None
        self.repeat_verified_entity_info: RepeatVerifiedEntityInfo = None
        self.slot_follow_up_entity_info: SlotFollowUpEntityInfo = None

        self.verified_entities: Dict[Text, List[Entity]] = {}

    def get_last_exd_entities(self) -> List[Entity]:
        """获取提取到的实体"""
        last_exd_entities = []
        exd_entities = self.slot_missing_entity_info.exd_entities
        not_verified_entities = self.pending_verified_entity_info.not_verified_entities \
            if self.pending_verified_entity_info else []
        repeat_verified_entities = self.repeat_verified_entity_info.repeat_verified_entities \
            if self.repeat_verified_entity_info else []
        follow_up_entities = self.slot_follow_up_entity_info.follow_up_entities \
            if self.slot_follow_up_entity_info else []
        # 添加 已验证 + 无重复 的实体
        for _, entities in self.verified_entities.items():
            for entity in entities:
                if entity not in last_exd_entities:
                    if not entity.verify_value:
                        entity.verify_value = entity.value
                    last_exd_entities.append(entity)
        # 添加 已验证 + 有重复 的实体
        for entity, name_lst in repeat_verified_entities:
            if entity not in last_exd_entities:
                entity.verify_value = "|".join(name_lst)
                last_exd_entities.append(entity)
        # 添加 未验证 的实体
        for entity in not_verified_entities:
            if entity not in last_exd_entities:
                last_exd_entities.append(entity)
        # 添加 追问 的实体
        for entity in follow_up_entities:
            if entity not in last_exd_entities:
                last_exd_entities.append(entity)
        # 添加 提取 的实体
        for entity in exd_entities:
            if entity not in last_exd_entities:
                last_exd_entities.append(entity)
        self.entity_set_slot_info(last_exd_entities)
        return last_exd_entities

    def entity_set_slot_info(self, entities: List[Entity]) -> None:
        """exd entity设置槽位信息"""
        for entity in entities:
            for _, slot in self.cfg_slots.items():
                if entity.en in slot.polymorphism:
                    entity.set_slot_info(slot)
                    break

    def init_pending_verified_entity_info(
            self,
            pending_verified_slot: Slot,
            not_verified_entities: List[Entity]
    ):
        self.pending_verified_entity_info = PendingVerifiedEntityInfo(
            self.slot_missing_entity_info,
            pending_verified_slot,
            not_verified_entities
        )

    def init_repeat_verified_entity_info(
            self,
            repeat_slot: Slot,
            repeat_verified_entities: List[Tuple[Entity, List[Text]]]
    ):
        self.repeat_verified_entity_info = RepeatVerifiedEntityInfo(
            repeat_slot,
            repeat_verified_entities
        )

    def init_slot_follow_up_entity_info(
            self,
            follow_up_slot: Slot
    ):
        self.slot_follow_up_entity_info = SlotFollowUpEntityInfo(
            follow_up_slot
        )

    def deduplicate_append_entity(self, entities: List[Entity], entity: Entity):
        """去重添加"""
        if entity not in entities:
            entities.append(entity)
        return entities

    def append_verified_entity(self, verified_entity: Entity) -> None:
        if verified_entity.en not in self.verified_entities.keys():
            self.verified_entities[verified_entity.en] = [verified_entity]
        else:
            verified_entities = self.verified_entities.get(verified_entity.en)
            self.verified_entities[verified_entity.en] = \
                self.deduplicate_append_entity(verified_entities, verified_entity)

    def append_verified_entities(self, verified_entities: List[Entity]) -> None:
        if verified_entities:
            for verified_entity in verified_entities:
                self.append_verified_entity(verified_entity)
