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


class Extractor:
    """An entity extractor."""

    def build_res(
            self,
            msg: SysMsg,
            exd_infos: List
    ) -> SysMsg:
        """一次交互的结果, exd_infos格式: [(name, value, start_pos, end_pos), ...]."""
        exd_entities: List[Entity] = []
        for exd_info in exd_infos:
            entity: Entity = copy.deepcopy(
                msg.get_o_entity(exd_info[0])
            )
            entity.set_ext_info(
                exd_info[1],
                exd_info[2],
                exd_info[3]
            )
            exd_entities.append(entity)
        msg.set_nlu_entities(
            exd_entities
        )
        return msg

