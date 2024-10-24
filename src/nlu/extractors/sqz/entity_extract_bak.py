# -*- coding:UTF-8 -*-
# !/usr/bin/python3

from typing import Text, List, Tuple

import cn2an
import jieba
import regex as re
from jieba import posseg

from src.nlu.utils.redis_data import GlobalData
from src.nlu.utils.util import Singleton, KMP
jieba.initialize()


@Singleton
class ExtractEntity():
    def __init__(self):
        self.jieba_mark = jieba
        self.data_update()

    def data_update(self):
        Gdata = GlobalData()
        self.default_entity = Gdata.entity
        self.jieba_mark.load_userdict(Gdata.jieba_path)

    def extract(self, query: Text) -> List[Tuple]:
        # 对查询语句进行分词，查找实体
        # 每个实体结果包括（实体类型，实体名，实体在文本的初始位置，实体在文本的结束位置）
        self.entity = []
        self.get_normal_entity(query)
        # if self.entity:
        self.get_number(query)
        return self.entity

    def get_normal_entity(self, query: Text):
        # 抽取配置的实体
        # param query: ASR_text
        for _ent in self.default_entity:
            for ent in _ent.entity:
                index = KMP(query, ent)  # 使用KMP算法匹配关键词以及获取索引
                if index != -1:
                    self.entity.append((_ent.entity_name, _ent.entity_word, index, index + len(ent) - 1))
                    query = query.replace(ent, "###")
                    break

        self.get_rules_entity(query)

    
    def get_rules_entity(self, query: Text):
        """
        获取不规则实体
        :param query: ASR_replace_text
        :return: None
        """
        match1 = re.search("[罐杯瓶份点些](水)(?!果|杯)", query)
        match2 = re.search("(提供|[倒拿送取端加有喝弄有和满])(水)(?!果|杯)", query)
        if match1 != None or match2 != None:
            self.entity.append(("drink", "水", -1, -1))
    
    
    def get_number(self, query: Text):
        # 抽取数字实体
        # param query: ASR_text
        rule = r"([负一二两三四五六七八九十百]+)(个)(小朋友|客人|人)(.*)(每个人|每人|一人)(.{1,2})?([负一二两三四五六七八九十百]+)(杯|瓶|份|罐)"
        rule_compile = re.compile(rule)
        match = rule_compile.search(query)
        if match != None:
            cn_num_1 = match.group(1)
            cn_num_2 = match.group(7)
            an_num_1 = cn2an.cn2an(cn_num_1, mode="smart")
            an_num_2 = cn2an.cn2an(cn_num_2, mode="smart")
            int_num_1 = int(an_num_1)
            int_num_2 = int(an_num_2)
            if int_num_1 < 0 or int_num_2 < 0:
                int_num = -1*abs(int_num_1*int_num_2)
            else:
                int_num = int_num_1 * int_num_2

            self.entity.append(("number", str(int_num), -1, -1))
            return

        flag = False
        rule = r"([负零一二两三四五六七八九十百千万亿几数]+)(个|名|只)?(小朋友|客人|人|杯|瓶|份|罐)"
        rule_compile = re.compile(rule)
        finditers = rule_compile.finditer(query)
        for match in finditers:
            if match != None:
                flag = True
            cn_nums = match.group(1)
            cn_num_list = self.get_complex_num(cn_nums)
            for cn_num in cn_num_list:
                try:
                    # 将中文数字转换为阿拉伯数字,有三种模式，strict,normal,smart
                    an_num = cn2an.cn2an(cn_num, mode="smart")
                    str_num = str(an_num)
                    index = KMP(query, cn_num)  # 使用KMP算法匹配关键词以及获取索引
                    self.entity.append(("number", str_num, index, index + len(cn_num) - 1))
                except Exception as e:
                    # print(e)
                    # 若抽取的不是数字,比如十几，几十这种，则默认为1
                    pass
        if not flag:
            # 若没搜索到数字，则默认为1
            self.entity.append(("number", '1', -1, -1))

    
    def get_complex_num(self, cn_nums:Text):
        """
        获取多数字实体
        :param cn_nums: 汉字数字 如三；四五六
        :return: cn_num_list 汉字数字列表 [四，五，六]
        """
        cn_num_list = []
        flag = False
        rule_1 = r"^(负)?([零一二两三四五六七八九]{2,})$"
        rule_compile_1 = re.compile(rule_1)
        search_1 = rule_compile_1.search(cn_nums)
        if search_1 != None:
            flag = True
            plural = search_1.group(1) if search_1.group(1) else ""
            for cn_num in search_1.group(2):
                cn_num_list.append(plural+cn_num)


        rule_2 = r"^(负)?([几零一二两三四五六七八九]{2,})([十百千万亿])$"
        rule_compile_2 = re.compile(rule_2)
        search_2 = rule_compile_2.search(cn_nums)
        if search_2 != None:
            flag = True
            plural = search_2.group(1) if search_2.group(1) else ""
            for cn_num in search_2.group(2):
                cn_num = plural+cn_num+search_2.group(3)
                cn_num_list.append(cn_num)

        if not flag:
            cn_num_list.append(cn_nums)
        
        return cn_num_list


    def jieba_cut(self, query: Text):
        '''
        通过结巴分词来抽取地点实体
        :param query: ASR_text
        :return: None
        '''
        entity_cut = self.jieba_mark.posseg.cut(query)
        place = [word for word, flag in entity_cut if flag == "ns"]
        if not place:
            self.entity.append(("place", "休息区", -1, -1))
        for pla in place:
            if len(pla) >= 2:
                index = KMP(query, pla)  # 使用KMP算法匹配关键词以及获取索引
                self.entity.append(("place", pla, index, index + len(pla) - 1))



if __name__ == '__main__':

    import time

    ent = ExtractEntity()
    query = [
        '帮我倒杯水',
        '帮我倒一杯水',
        '帮我倒两杯水',
        '帮我倒三杯水',
        '帮我倒一百二十三杯水',
        '帮我倒三千四百五十六杯水',
        '帮我倒四万三千二百一十杯水',
        '帮我倒一亿五千万六千三百五十五杯水',
        '帮我倒几杯水',
        '返回待命点',
        '今天星期几']
    for q in query:
        stime = time.time()
        entity = ent.extract(q)
        etime = time.time()
        print(entity)
        print("cut_time:", round(etime - stime, 7))




