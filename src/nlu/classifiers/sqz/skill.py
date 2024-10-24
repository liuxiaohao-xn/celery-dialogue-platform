# -*- coding:UTF-8 -*-
# !/usr/bin/python3
import time
from typing import Text

from src.nlu.utils.redis_data import GlobalData
from src.nlu.utils.util import Singleton


@Singleton
class SkillRecognize():
    def __init__(self):
        self.data_update()

    def data_update(self):
        Gdata = GlobalData()
        self.skill_compile = Gdata.skill_rules

    def predict(self, query: Text)-> Text:
        # 通过正则表达式来判断查询语句的技能，返回技能名称
        skill_ID = ''
        for rule_compile in self.skill_compile:
            if rule_compile[1].search(query) != None:
                skill_ID = rule_compile[0]
                return skill_ID
        return skill_ID



class IntentRecognize():
    def __init__(self, skill_ID: Text):
        self.skill_ID = skill_ID
        self.data_update()

    def data_update(self):
        Gdata = GlobalData()
        self.intent_compile = Gdata.intent_rules

    def predict(self, query: Text)-> Text:
        # 通过正则表达式来判断查询语句的意图, 返回意图名称
        intent_ID = ''
        filter_compile = filter(lambda x: x[0] == self.skill_ID, self.intent_compile)
        for rule_compile in list(filter_compile):
            if rule_compile[2].search(query) != None:
                intent_ID = rule_compile[1]
                return intent_ID
        return intent_ID

        # intent_ID = filter(lambda x:x[1].search(query)!=None, self.compile)
        # return list(intent_ID)


if __name__ == "__main__":
    skill_rec = SkillRecognize()
    intent_rec = IntentRecognize("YHS_ZG_DL")
    query = [
        "开始导览",
        "继续导览",
        "去上海会议室",
        "去会议室",
        "开始",
        "继续"]
    for q in query:
        stime = time.time()
        skill = skill_rec.predict(q)
        intent = intent_rec.predict(q)
        etime = time.time()
        print(skill,intent)
        skill_time = etime-stime
        print(round(skill_time, 7))
    
