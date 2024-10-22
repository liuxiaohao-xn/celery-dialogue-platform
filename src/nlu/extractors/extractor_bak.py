# -*- coding: utf-8 -*-
# @Time : 2022/6/7 16:48
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : extractor_bak.py
from __future__ import annotations

import copy
import logging
from src.common.message import SysMsg
from typing import Text, Any, List, Dict
from src.common.constant import ComponentResKey, TermKey
from src.common.domain.domain import Slot, Entity

logger = logging.getLogger(__name__)


class EXTEntity:

    def __init__(
            self,
            ext_entity_name: Text,
            ext_entity_val: Any = None,
            ext_entity_pos_start: int = -1,
            ext_entity_pos_end: int = -1,
    ):
        self.ext_entity_name = ext_entity_name
        self.ext_entity_val = ext_entity_val
        self.ext_entity_pos_start = ext_entity_pos_start
        self.ext_entity_pos_end = ext_entity_pos_end
        self.ext_entity_normal_val = ext_entity_val  # todo 默认是ext_entity_val，后期可通过self.set_ext_entity_normal_val(...)更改
        self.ext_entity_mapped_slot_name: Text = None
        self.extra = ""  # todo 如参会人有人和部门，根据具体业务需要特定补充说明，可通过self.set_extra(...)来更改
        self.entity: Entity = None  # todo 绑定domain entity中定义的属性
        self.required: bool = None  # todo 该实体对应的slot是否必须
        """
        Args:
            ext_entity_name: 提取实体类别名
            ext_entity_val: 提取实体值
            ext_entity_pos_start: 提取实体起始位置
            ext_entity_pos_end: 提取实体结束位置
            ext_entity_normal_val: 提取实体归一化值
            ext_entity_mapped_slot_name: 提取实体在本轮意图映射成的槽位名 
        """

    def set_ext_entity_normal_val(self, ext_entity_normal_val: Text):
        self.ext_entity_normal_val = ext_entity_normal_val

    def set_ext_entity_mapped_slot_name(self,  ext_entity_mapped_slot_name):
        self.ext_entity_mapped_slot_name = ext_entity_mapped_slot_name

    def set_extra(self, extra: Any):
        self.extra = extra

    def set_entity(self, entity):
        self.entity = entity

    def __eq__(self, other):
        """切勿修改EXTEntity相等判断条件, 目前认为两个EXTEntity的实体名和值相等，就认为两者相等，暂不考虑位置信息."""
        return self.ext_entity_name == other.ext_entity_name and self.ext_entity_val == other.ext_entity_val


class Extractor(object):
    """An entity extractor."""

    def __init__(self):
        self.nlu_ext_res_key: Text = ComponentResKey.NLU_EXT_RES.value
        self.ext_entities_key: Text = TermKey.EXT_ENTITIES.value
        self.msg: SysMsg = None
        self.intent_cfg_slot_names: List[Text] = []
        """
        Args:
            intent_cfg_slot_names： domain文件中意图配置的槽位名集合
        """

    def get_parsed_cfg_intent_slots(self) -> (Text, Dict[Text, Slot]):
        """根据意图获取解析后的槽位信息"""
        try:
            intent_name = self.msg.res.get(ComponentResKey.NLU_CLS_RES.value).get(TermKey.INTENT.value)
        except:
            """多轮追问时，意图信息从对话状态中提取"""
            from src.dm.manage_dialogue import DialogueStatePool
            dialogue_state = DialogueStatePool.get_dialogue_state_by_sid(self.msg.session_id)
            intent_name = dialogue_state.state.get(ComponentResKey.NLU_CLS_RES.value).get(TermKey.INTENT.value)
        return intent_name, self.msg.parsed_domain.parsed_intents.get(intent_name).slots

    def set_ext_entity_slot_name_and_cfg_entity(self, ext_entity: EXTEntity, cfg_intent_slots: Dict[Text, Slot]):
        """将ext_slots中的entity_name映射成slot_name, 并绑定cfg entity"""
        for slot_name, cfg_intent_slot in cfg_intent_slots.items():
            if ext_entity.ext_entity_name in cfg_intent_slot.entity_cls:
                ext_entity.ext_entity_mapped_slot_name = slot_name
                ext_entity.required = cfg_intent_slot.required
                try:
                    ext_entity.entity = self.msg.parsed_domain.parsed_entities.get(ext_entity.ext_entity_name)
                except Exception:
                    raise Exception(f"获取实体{ext_entity.ext_entity_name}失败.")

    def build_res(
            self,
            msg: SysMsg,
            ext_entities: List[EXTEntity] = [],
    ) -> SysMsg:
        """一次交互的结果."""
        self.msg = msg
        # 获取意图下配置的槽位
        intent_name, cfg_intent_slots = self.get_parsed_cfg_intent_slots()

        # 给提取出的实体赋槽位名、cfg entity、required
        for ext_entity in ext_entities:
            self.set_ext_entity_slot_name_and_cfg_entity(ext_entity, cfg_intent_slots)

        # 过滤掉意图下未配置槽位对应的实体
        for i, ext_entity in enumerate(copy.deepcopy(ext_entities)):
            if not ext_entity.ext_entity_mapped_slot_name:
                logger.info(f"{intent_name}下的槽位未配置实体【{ext_entity.ext_entity_name}】.")
                ext_entities.pop(i)

        # 一个任务可用多个extractor来提取，首次添加需要创建
        if self.nlu_ext_res_key not in self.msg.res.keys():
            self.msg.res.update({
                self.nlu_ext_res_key: {
                    self.ext_entities_key: [],
                }
            })

        # 更新提取到的实体
        exd_slots = self.msg.res.get(self.nlu_ext_res_key).get(self.ext_entities_key)
        for ext_entity in ext_entities:
            exd_slots.append(ext_entity)

        return self.msg
