# -*- coding:UTF-8 -*-
# !/usr/bin/python3

from typing import Text, List, Tuple

from src.nlu.utils.redis_data import GlobalData
from src.nlu.utils.util import Singleton, KMP


@Singleton
class ExtractEntity():
    def __init__(self):
        self.data_update()

    def data_update(self):
        Gdata = GlobalData()
        self.entity = Gdata.entity
    
    def extract(self, query: Text)-> List[Tuple]:
        # 对查询语句进行分词，查找实体
        # 每个实体结果包括（实体类型，实体名，实体在文本的初始位置，实体在文本的结束位置）
        entity = []
        
        # 抽取实体
        for _ent in self.entity:
            for ent in _ent.entity:
                index = KMP(query,ent) #使用KMP算法匹配关键词以及获取索引
                if index != -1:
                    entity.append((_ent.entity_name, _ent.entity_word, index, index+len(ent)-1))
                    break
        return entity



if __name__ == '__main__':
    
    import time
    ent = ExtractEntity()
    query = [
        '叫iot开发部的德诚半个小时后来杭州会议室开会',
        '我想去上海会议室',
        '你能不能带我去成都会议室',
        '我想去上海',
        '你可以带我去杭州会议厅吗',
        '你知道成都办公室怎么走吗',
        '我要到杭州',
        '我要去成都',
        '成都会议室怎么去啊',
        '你知道成都会议室在哪里吗',
        '今天星期几']
    for q in query:
        stime = time.time()
        entity = ent.extract(q)
        etime = time.time()
        print(entity)
        print("cut_time:",round(etime-stime,7))




