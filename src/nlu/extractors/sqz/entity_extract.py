# -*- coding:UTF-8 -*-
# !/usr/bin/python3

import regex as re, time
from typing import Text, List, Dict, Tuple
from src.nlu.utils.redis_data import Global_Data
from LAC import LAC
from src.nlu.utils.util import Singleton, KMP
from .time_extract import Extract_Time


@Singleton
class Entity_Name_Time():
    def __init__(self):
        self.lac = LAC(mode='lac')
        self.data_update()

    def data_update(self):
        Gdata = Global_Data()
        self.Ex_time = Extract_Time()
        self.time_rules = Gdata.time_rules
        self.entity = Gdata.entity
        self.lac.load_customization(Gdata.lac_path)

    def cut(self, query):
        # 对查询语句进行分词，查找实体
        entity_cut = self.lac.run(query)
        entity = []
        try:
            # 抽取部门
            entity_dep = self.get_dep(query)
            if len(entity_dep) > 0:
                entity = entity + entity_dep

            # 抽取名字
            cut_query = re.sub("总裁办", "", query)
            name = [entity_cut[0][i] for i, value in enumerate(entity_cut[1]) if value == "PER"]
            for na in name:
                if len(na) >= 2:
                    index = query.index(na)
                    entity.append(("peo", na, index, index + len(na) - 1))

            # 时间抽取
            norm_time = self.Ex_time.extract(query)
            if norm_time:
                for n_t in norm_time:
                    entity.append(("time",n_t,-1,-1))
        except Exception as e:
            print(e)

        return entity

    def get_dep(self, query: Text) -> List[Tuple]:
        #抽取部门实体
        help_word = "(通知|联系|告知|召集|安排|组织|呼叫|拨打|还有|以及|及|和|与|跟|叫|让|喊|给|打|把)"
        help_word_rule = help_word + "(.{})(中心科|开发部|研发部|办公组|中心|部|科|组)"
        short_rule = "(.{2,7})(中心科|办公组|中心|部|科|组)"
        check_rule = "(.{2,4})(中心科|办公组|中心|部|科|组)"
        com_check_rule = re.compile(check_rule)
        com_short_rule = re.compile(short_rule)
        entity = []
        for i in range(5):
            long_rule = help_word_rule.format("{"+str(i+2)+"}")
            com_long_rule = re.compile(long_rule)
            while com_long_rule.search(query):
                search_long = com_long_rule.search(query)
                dep = search_long.group(2).replace("#",'') + search_long.group(3)
                start_dep_index = KMP(query,dep)
                
                if start_dep_index == -1:
                    break
                end_dep_index = start_dep_index+len(dep)
                # 采用切片法来修改字符，防止replace方法将包含相同的字符的部门替换掉
                query = query[:start_dep_index]+"#"*len(dep)+\
                    query[end_dep_index:]
                entity.append(('dep',dep,start_dep_index,end_dep_index-1))
            
            if com_short_rule.search(query) == None:
                break
            while i==4 and com_short_rule.search(query) != None:
                search_short = com_short_rule.search(query)
                dep = search_short.group(1).replace("#",'') + search_short.group(2)
                
                if len(com_check_rule.findall(dep))>=2: # 处理部门连在一起抽出的情况 语音科软件科-> 语音科 软件科
                    for find_dep in com_check_rule.findall(dep):
                        entity.append(('dep',"".join(find_dep),-1,-1))
                    break
                start_dep_index = KMP(query,dep)
                
                if start_dep_index == -1:
                    break
                end_dep_index = start_dep_index+len(dep)
                query = query[:start_dep_index]+"#"*len(dep)+\
                    query[end_dep_index:]
                entity.append(('dep',dep,start_dep_index,end_dep_index-1))
        
        start_dep_index = KMP(query,"总裁办")
        if start_dep_index != -1:
            entity.append(('dep',"总裁办",start_dep_index,start_dep_index+2))
        
        return entity

if __name__ == '__main__':
    
    ent = Entity_Name_Time()
    query = [
        '叫iot开发部的德诚半个小时后来杭州会议室开会',
        '叫语音科的王清川和王庆忠过来办公室开会',
        '下午二点十四分',
        '下午16点40',
        '九点四分',
        '一个钟之后',
        '十四月三号二十四点五刻',
        '过二个小时左右',
        '八月十七号星期四下午三点',
        '明天八月十八号下午三点半',
        '明天星期四下午四点半']
    for q in query:
        stime = time.time()
        entity = ent.cut(q)
        etime = time.time()
        print("entity:",entity)
        print("cut_time:",round(etime-stime,7))




