# -*- coding:UTF-8 -*-
# !/usr/bin/python3
import time
from src.nlu.utils.redis_data import Global_Data
from src.nlu.utils.util import Singleton


@Singleton
class Skill_Recognize():
    def __init__(self):
        self.data_update()

    def data_update(self):
        Gdata = Global_Data()
        self.compile = Gdata.skill_rules

    def predict(self, query):
        # 通过正则表达式来判断查询语句的技能
        skill_name = ''
        for rule_compile in self.compile:
            if rule_compile[1].search(query) != None:
                skill_name = rule_compile[0]
                break
        return skill_name

        # skill_ID = filter(lambda x:x[1].search(query)!=None, self.compile)
        # return list(skill_ID)


# @Singleton
class Intent_Recognize():
    def __init__(self, skill_ID):
        self.skill_ID = skill_ID
        self.data_update()

    def data_update(self):
        Gdata = Global_Data()
        self.compile = Gdata.intent_rules

    def predict(self, query):
        # 通过正则表达式来判断查询语句的意图
        intent_name = ''
        fil_compile = filter(lambda x: x[0] == self.skill_ID, self.compile)
        for rule_compile in list(fil_compile):
            if rule_compile[2].search(query) != None:
                intent_name = rule_compile[1]
                break
        return intent_name

        # intent_ID = filter(lambda x:x[1].search(query)!=None, self.compile)
        # return list(intent_ID)


if __name__ == "__main__":
    skill_rec = Skill_Recognize()
    intent_rec = Intent_Recognize()
    query = ["通知张三和李四下午四点到办公室开视频会议","麻烦帮我取几瓶水过来","帮我联系一下总裁办秘书张小萌"]
    for q in query:
        stime = time.time()
        skill = skill_rec.predict(q)
        intent = intent_rec.predict(q)
        etime = time.time()
        print(skill,intent)
        skill_time = etime-stime
        print(round(skill_time, 7))
    
