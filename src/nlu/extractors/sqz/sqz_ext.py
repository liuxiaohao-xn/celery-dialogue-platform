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
from src.nlu.extractors.sqz.entity_extract import Entity_Name_Time


class EntityNameTime(Component, Extractor):
    entity_name_time = Entity_Name_Time()

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        return {}

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> Extractor:
        extractor = EntityNameTime()
        extractor.model = cls.entity_name_time
        return extractor

    def process(self, msg: SysMsg):
        # 实体提取
        ext_entities = self.model.cut(msg.text)
        return self.build_res(
            msg,
            ext_entities
        )


class ZhNumExtractor(Component, Extractor):

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        return {
            "num": re.compile(u'[一二两三四五六七八九十]{1,3}'),
        }

    @classmethod
    def make_o(cls, config: Dict[Text, Any]) -> Extractor:
        # todo 需要判断config.keys()是否都在配置的skills中
        #   ...
        zh_num_extractor = ZhNumExtractor()
        zh_num_extractor.model = config
        return zh_num_extractor

    def process(self, msg: SysMsg) -> SysMsg:
        """技能分类，执行完此函数，msg需要绑定skill_name属性"""
        import cn2an
        ext_infos = []
        for num in self.model.get("num").findall(msg.text):
            if num == "两":
                num = "二"
            ext_infos.append(("number", cn2an.cn2an(num), -1, -1))
        return self.build_res(msg, ext_infos)
