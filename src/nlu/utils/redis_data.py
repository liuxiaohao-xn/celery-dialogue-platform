import json,regex as re
from .util import Singleton
from collections import namedtuple
import os
import pandas as pd

cur_path = os.path.dirname(__file__)
@Singleton
class Global_Data():
    def __init__(self):
        self.skill_rules = ()
        self.skill_ID_name = {}
        self.intent_rules = ()
        self.intent_ID_name = {}
        self.entity = ()
        self.time_rules = ()
        self.lac_path = None
        
        self.data_update()
    
    def data_update(self):
        #数据读取
        try:
            skill_path = "data/skill.json"
            intent_path = "data/intent.json"
            entity_path = "data/entity.json"
            time_path = "data/time.json"
            org_data_path = os.path.join(cur_path, "data/org_data")
            alias_data_path = os.path.join(cur_path, "data/alias_data")
            
            self.lac_path = os.path.join(cur_path, "data/LACdict.txt")
            # 读取BK树数据
            self.bk_tree_path = os.path.join(cur_path, "data/bk_tree_data/data_names.txt")
            self.alias_bk_tree_path = os.path.join(cur_path, "data/bk_tree_data/data_names_alias.txt")
            self.pinyin_normal_bk_tree_path = os.path.join(cur_path, "data/bk_tree_data/data_names_pinyin_normal.txt")
            self.alias_pinyin_normal_bk_tree_path = os.path.join(cur_path, "data/bk_tree_data/data_name_alias_pinyin_normal.txt")
            self.pinyin_tone_bk_tree_path = os.path.join(cur_path, "data/bk_tree_data/data_names_pinyin_num.txt")
            self.alias_pinyin_tone_bk_tree_path = os.path.join(cur_path, "data/bk_tree_data/data_name_alias_pinyin_num.txt")
            
            # 读取名字实体的拼音数据
            self.data_org_names = pd.read_csv(os.path.join(org_data_path, "names.csv"), encoding="gbk")
            self.data_org_names_pinyin_normal = pd.read_csv(os.path.join(org_data_path, "names_pinyin_normal.csv"), encoding="gbk")
            self.data_org_names_pinyin_tone = pd.read_csv(os.path.join(org_data_path, "names_pinyin_num.csv"), encoding="gbk")
            self.org_data = pd.concat([self.data_org_names, self.data_org_names_pinyin_normal, self.data_org_names_pinyin_tone], axis=1)
            
            self.data_names = pd.read_csv(os.path.join(alias_data_path, "names.csv"), encoding="gbk")
            self.data_alias_names = pd.read_csv(os.path.join(alias_data_path, "name_alias.csv"), encoding="gbk")
            self.data_alias_names_pinyin_normal = pd.read_csv(os.path.join(alias_data_path, r"name_alias_pinyin_normal.csv"), encoding="gbk")
            self.data_alias_names_pinyin_tone = pd.read_csv(os.path.join(alias_data_path, r"name_alias_pinyin_num.csv"), encoding="gbk")
            self.alias_data = pd.concat([self.data_names, 
                                        self.data_alias_names,
                                        self.data_alias_names_pinyin_normal,
                                        self.data_alias_names_pinyin_tone],
                                        axis=1)
            
            # 读取技能意图数据
            with open(os.path.join(cur_path, skill_path), encoding="UTF-8-sig") as skill:
                skill_json = json.load(skill)
            with open(os.path.join(cur_path, intent_path) ,encoding="UTF-8-sig") as intent:
                intent_json = json.load(intent)
            with open(os.path.join(cur_path, entity_path), encoding="UTF-8-sig") as entity:
                entity_json = json.load(entity)
            with open(os.path.join(cur_path, time_path), encoding="UTF-8-sig") as time_rule:
                time_json = json.load(time_rule)

            # 获取技能正则
            re_skill = []
            for sk in skill_json:
                skill_name = sk["skill_mark"]
                for rule in sk["skill_corpus"]:
                    rule_dict = (skill_name, re.compile(rule))
                    re_skill.append(rule_dict)
            self.skill_rules = tuple(re_skill)

            # 获取意图正则
            re_intent = []
            for intent in intent_json:
                intent_name = intent["intent_mark"]
                skill_ID = intent["skill_ID"]
                for rule in intent["intent_corpus"]:
                    rule_dict = (skill_ID, intent_name, re.compile(rule))
                    re_intent.append(rule_dict)
            self.intent_rules = tuple(re_intent)

            # 获取实体
            _ent = namedtuple(
                "_ent", ["entity_ID", "entity_name", "entity_word", "entity"])
            re_entity = []
            for entity in entity_json:
                for key, value in entity["entity_words"].items():
                    value = [key] + value if len(value) > 0 else [key]
                    re_entity.append(
                        _ent(
                            entity_ID=entity["entity_ID"],
                            entity_name=entity["entity_mark"],
                            entity_word=key,
                            entity=value
                        ))
            self.entity = tuple(re_entity)

            # 获取时间正则
            time_rule = "|".join(time_json["time_rules"])
            self.time_rules = re.compile(time_rule)

            return True
        except Exception:
            raise Exception("load_ERROR")

if __name__ == '__main__':
    Gdata = Global_Data()
