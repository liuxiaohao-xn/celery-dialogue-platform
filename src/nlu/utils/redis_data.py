import json
import logging
import os
import traceback
from collections import namedtuple

import regex as re

from .util import Singleton

cur_path = os.path.dirname(__file__)
logger = logging.getLogger(__name__)

@Singleton
class GlobalData():
    def __init__(self):
        self.skill_rules = []
        self.skill_ID_name = {}
        self.intent_rules = []
        self.intent_ID_name = {}
        self.entity = []
        
        self.data_update()
    
    def data_update(self):
        #数据读取
        try:
            skill_path = os.path.join(cur_path, "data/skill.json")
            intent_path = os.path.join(cur_path, "data/intent.json")
            entity_path = os.path.join(cur_path, "data/entity.json")
            
            with open(skill_path, encoding="UTF-8-sig") as skill:
                skill_json = json.load(skill)
            with open(intent_path, encoding="UTF-8-sig") as intent:
                intent_json = json.load(intent)
            with open(entity_path, encoding="UTF-8-sig") as entity:
                entity_json = json.load(entity)

            # 读取技能正则数据
            re_skill = []
            for sk in skill_json:
                skill_name = sk["skill_name"]
                skill_ID = sk["skill_ID"]
                self.skill_ID_name[skill_ID] = skill_name
                for rule in sk["skill_corpus"]:
                    rule_list = (skill_ID, re.compile(rule))
                    re_skill.append(rule_list)
            self.skill_rules = tuple(re_skill)

            # 读取意图正则数据
            re_intent = []
            for intent in intent_json:
                skill_ID = intent["skill_ID"]
                intent_ID = intent["intent_ID"]
                intent_name = intent["intent_name"]
                self.intent_ID_name[intent_ID] = intent_name
                for rule in intent["intent_corpus"]:
                    rule_list = (skill_ID, intent_ID, re.compile(rule))
                    re_intent.append(rule_list)
            self.intent_rules = tuple(re_intent)

            # 读取会议室等实体数据
            _ent = namedtuple(
                "_ent",["entity_ID","entity_name","entity_word","entity"])
            re_entity = []
            for entity in entity_json:
                for key,value in entity["entity_words"].items():
                    value = [key]+value if len(value)>0 else [key]
                    re_entity.append(
                        _ent(
                            entity_ID = entity["entity_ID"],
                            entity_name = entity["entity_mark"],
                            entity_word = key,
                            entity = value
                        ))
            self.entity = tuple(re_entity)

        except Exception as e:
            logger.error("load_data_ERROR:",e)
            logger.error("\n" + traceback.format_exc())
        
if __name__ == '__main__':
    Gdata = GlobalData()
