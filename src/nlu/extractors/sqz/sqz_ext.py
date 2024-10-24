# -*- coding: utf-8 -*-
# @Time : 2022/6/28 10:30
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : sqz_ext.py
import re
from typing import Dict, Text, Any
from src.common.message import SysMsg
from src.common.component.component import Component
from src.nlu.extractors.extractor import Extractor
from src.nlu.extractors.sqz.entity_extract import ExtractEntity


class MeetingRoomExtractEntity(Component, Extractor):
    extract_entity = ExtractEntity()

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        return {}

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> Extractor:
        extractor = MeetingRoomExtractEntity()
        extractor.model = cls.extract_entity
        return extractor

    def process(self, msg: SysMsg):
        # 实体提取
        ext_entities = self.model.extract(msg.text)
        return self.build_res(
            msg,
            ext_entities
        )

