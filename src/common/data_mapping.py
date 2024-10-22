import json
from typing import Text, Tuple


class Mapping:
    """技能,意图映射"""
    
    def __init__(self, path):
        self.skill_dict = []
        self.intent_dict = []
        with open(path, 'r', encoding="utf-8-sig") as data_json:
            load_json = json.load(data_json)
            for skill in load_json["skill"]:
                self.skill_dict.append((skill["skill_ID"], skill["skill_name"]))
            for intent in load_json["intent"]:
                self.intent_dict.append((intent["intent_ID"], intent["skill_ID"],intent["intent_name"]))
    
    def get_skill_id(self, skill_name: Text) -> Text:
        for skill in self.skill_dict:
            if skill_name in skill[1]:
                return str(skill[0])
    
    def get_intent_id(self, intent_name: Text) -> Text:
        for intent in self.intent_dict:
            if intent_name in intent[2]:
                return str(intent[0])
    
    def get_skill_name(self, skill_ID: (Text, int)) -> Tuple:
        skill_ID = int(skill_ID)
        for skill in self.skill_dict:
            if skill_ID == skill[0]:
                return tuple(skill[1])
    
    def get_intent_name(self, intent_ID: (Text, int)) -> Tuple:
        intent_ID = int(intent_ID)
        for intent in self.intent_dict:
            if intent_ID == intent[0]:
                return tuple(intent[2])


if __name__ == "__main__":

    mapp = Mapping()
    print("skill_ID:", mapp.get_skill_id("取水"))
    print("intent_ID:", mapp.get_intent_id("取消会议"))
    print("skill_name:", mapp.get_skill_name(3))
    print("intent_name:", mapp.get_intent_name(2))
