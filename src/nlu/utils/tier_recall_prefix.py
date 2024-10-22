# -*- coding: utf-8 -*-
# @Time : 2022/7/22 11:05
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : tier_recall.py
import sys
from dataclasses import dataclass
from typing import Text, Tuple, List, Set
import pickle
import copy, os
from pypinyin import pinyin, lazy_pinyin, Style
from src.nlu.utils.bk_tree import BKTree
from src.nlu.utils.util import longest_common_prefix
from src.nlu.utils.redis_data import Global_Data

# 预加载
# org_data
Gdata = Global_Data()
data_org_names = Gdata.data_org_names
data_org_names_pinyin_normal = Gdata.data_org_names_pinyin_normal
data_org_names_pinyin_tone = Gdata.data_org_names_pinyin_tone
org_data = Gdata.org_data
# alias_data
data_names = Gdata.data_names
data_alias_names = Gdata.data_alias_names
data_alias_names_pinyin_normal = Gdata.data_alias_names_pinyin_normal
data_alias_names_pinyin_tone = Gdata.data_alias_names_pinyin_tone
alias_data = Gdata.alias_data


sys.path.append(os.path.dirname(__file__))


def init_bk_tree(bk_tree_file: Text) -> BKTree:
    with open(bk_tree_file, "rb") as content:
        bk_t: BKTree = pickle.load(content)
    return bk_t


# 初始化bk_tree
name_bk_tree = init_bk_tree(Gdata.bk_tree_path)
name_alias_bk_tree = init_bk_tree(Gdata.alias_bk_tree_path)
name_pinyin_normal_bk_tree = init_bk_tree(Gdata.pinyin_normal_bk_tree_path)
name_alias_pinyin_normal_bk_tree = init_bk_tree(Gdata.alias_pinyin_normal_bk_tree_path)
name_pinyin_tone_bk_tree = init_bk_tree(Gdata.pinyin_tone_bk_tree_path)
name_alias_pinyin_tone_bk_tree = init_bk_tree(Gdata.alias_pinyin_tone_bk_tree_path)


@dataclass
class EnhancePendingData:
    pending_data: Text
    pending_data_pinyin_normal: Text
    pending_data_pinyin_normal_split: Text
    pending_data_pinyin_tone: Text
    pending_data_label: Text
    # 各维度召回结果
    # pending_data_pre: List[Tuple] = None
    # pending_data_alias_pre: List[Tuple] = None
    # pending_data_pinyin_normal_pre: List[Tuple] = None
    # pending_data_alias_pinyin_normal_pre: List[Tuple] = None
    # pending_data_pinyin_tone_pre: List[Tuple] = None
    # pending_data_alias_pinyin_tone_pre: List[Tuple] = None
    # rank 结果
    pending_data_rank_pre: Set[Text] = None
    pending_data_rank_label: Text = None

    def __str__(self):
        return str({
            "pending_data": self.pending_data,
            # "pending_data_pinyin_normal": self.pending_data_pinyin_normal,
            # "pending_data_pinyin_tone": self.pending_data_pinyin_tone,
            "pending_data_rank_pre": self.pending_data_rank_pre,
            "pending_data_label": self.pending_data_label,
            "pending_data_rank_label": self.pending_data_rank_label
        })


def trf(pin_yin: List, split="") -> Text:
    res = []
    for py in pin_yin:
        res.append(py)
    return split.join(res)


def name_to_pinyin_normal(name: Text) -> Text:
    """格式化拼音"""
    return trf(lazy_pinyin(name))


def name_to_pinyin_normal_split(name: Text) -> Text:
    """格式化拼音, 空格分开"""
    return trf(lazy_pinyin(name), split=" ")


def name_to_pinyin_tone(name: Text) -> Text:
    """数字音调拼音"""
    return ""
    # 不支持 return trf(pinyin(name, style=Style.TONE3))


def pre_process_pending_data(pending_datas: List[Text], pending_datas_label: List[Text] = None):
    """待处理数据前置处理, 拼音化, 标签化"""
    if pending_datas_label:
        assert len(pending_datas) == len(pending_datas_label)
    enhance_pending_datas = []
    for i, pending_data in enumerate(pending_datas):
        enhance_pending_datas.append(
            EnhancePendingData(
                pending_data,
                name_to_pinyin_normal(pending_data),
                name_to_pinyin_normal_split(pending_data),
                name_to_pinyin_tone(pending_data),
                pending_datas_label[i] if pending_datas_label else None
            )
        )
    return enhance_pending_datas


def recall(bk_tree: BKTree, item: Text, distance=0) -> List[Tuple]:
    """召回"""
    return bk_tree.find(item, distance)


def name_recall(name: Text, distance=0) -> List[Tuple]:
    """召回名字"""
    return recall(name_bk_tree, name, distance)


def name_alias_recall(name_alias: Text, distance=0) -> List[Tuple]:
    """召回别名"""
    return recall(name_alias_bk_tree, name_alias, distance)


def name_pinyin_normal_recall(name_pinyin_normal: Text, distance=0) -> List[Tuple]:
    """召回pinyin normal"""
    return recall(name_pinyin_normal_bk_tree, name_pinyin_normal, distance)


def name_pinyin_tone_recall(name_pinyin_tone: Text, distance=0) -> List[Tuple]:
    """召回pinyin tone"""
    return recall(name_pinyin_tone_bk_tree, name_pinyin_tone, distance)


def name_alias_pinyin_normal_recall(name_alias_pinyin_normal: Text, distance=1) -> List[Tuple]:
    """召回别名pinyin normal"""
    return recall(name_alias_pinyin_normal_bk_tree, name_alias_pinyin_normal, distance)


def name_alias_pinyin_tone_recall(name_alias_pinyin_tone: Text, distance=1) -> List[Tuple]:
    """召回别名pinyin tone"""
    return recall(name_alias_pinyin_tone_bk_tree, name_alias_pinyin_tone, distance)


def alias_name_mapping_name(name_alisa) -> List[Text]:
    """别名映射成全名 如 晓浩 -> 刘小浩"""
    return alias_data.loc[alias_data["name_alias"] == name_alisa]["name"].tolist()


def name_pinyin_normal_mapping_name(name_pinyin_normal) -> List[Text]:
    """normal 拼音映射成全名 如 liuxiaohao -> 刘小浩"""
    return org_data.loc[org_data["name_pinyin_normal"] == name_pinyin_normal]["name"].tolist()


def name_pinyin_tone_mapping_name(name_pinyin_tone) -> List[Text]:
    """normal tone 拼音映射成全名 如 liu2xiao3hao4 -> 刘小浩"""
    return org_data.loc[org_data["name_pinyin_num"] == name_pinyin_tone]["name"].tolist()


def name_alias_pinyin_normal_mapping_name(name_alias_pinyin_normal) -> List[Text]:
    """别名normal 拼音映射成全名 如 xiaohao -> 刘小浩"""
    return alias_data.loc[alias_data["name_alias_pinyin_normal"] == name_alias_pinyin_normal]["name"].tolist()


def name_alias_pinyin_normal_mapping_alias_name(name_alias_pinyin_normal) -> List[Text]:
    """别名normal 拼音映射成全名 如 xiaohao -> 刘小浩"""
    return alias_data.loc[alias_data["name_alias_pinyin_normal"] == name_alias_pinyin_normal]["name_alias"].tolist()


def name_alias_pinyin_tone_mapping_name(name_alias_pinyin_tone) -> List[Text]:
    """别名tone 拼音映射成全名 如 xiao3hao4 -> 刘小浩"""
    return alias_data.loc[alias_data["name_alias_pinyin_num"] == name_alias_pinyin_tone]["name"].tolist()


def name_recall_res_decision(enhance_pending_data: EnhancePendingData, name_recall_res: List[Tuple]):
    """全名召回决策，直接返回结果"""
    for distance, name in name_recall_res:
        enhance_pending_data.pending_data_rank_pre.add(name)
        enhance_pending_data.pending_data_rank_label = name


def name_alias_recall_res_decision(enhance_pending_data: EnhancePendingData, name_alias_recall_res: List[Tuple]):
    """别名召回决策, 直接返回结果"""
    for distance, name_alias in name_alias_recall_res:
        # name_alias 映射成 name
        names = alias_name_mapping_name(name_alias)
        for name in names:
            enhance_pending_data.pending_data_rank_pre.add(name)


def name_pinyin_normal_recall_res_decision(enhance_pending_data: EnhancePendingData,
                                           name_pinyin_normal_recall_res: List[Tuple]):
    """拼音召回决策, 先缓存结果"""
    for distance, name_pinyin_normal in name_pinyin_normal_recall_res:
        # name_pinyin_normal 映射成 name
        names = name_pinyin_normal_mapping_name(name_pinyin_normal)
        for name in names:
            enhance_pending_data.pending_data_rank_pre.add(name)


def name_pinyin_tone_recall_res_decision(enhance_pending_data: EnhancePendingData,
                                         name_pinyin_tone_recall_res: List[Tuple]):
    """拼音召回决策, 先缓存结果"""
    for distance, name_pinyin_tone in name_pinyin_tone_recall_res:
        # name_pinyin_tone 映射成 name
        names = name_pinyin_tone_mapping_name(name_pinyin_tone)
        for name in names:
            enhance_pending_data.pending_data_rank_pre.add(name)


def name_alias_pinyin_normal_recall_res_decision(enhance_pending_data: EnhancePendingData,
                                                 name_alias_pinyin_normal_recall_res: List[Tuple]):
    """别名拼音召回决策, 先缓存结果"""
    # 直接返回
    for distance, name_alias_pinyin_normal in name_alias_pinyin_normal_recall_res:
        # name_alias_pinyin_normal 映射成 name
        names = name_alias_pinyin_normal_mapping_alias_name(name_alias_pinyin_normal)
        for name in names:
            enhance_pending_data.pending_data_rank_pre.add(name)


def name_alias_pinyin_tone_recall_res_decision(enhance_pending_data: EnhancePendingData,
                                               name_alias_pinyin_tone_recall_res: List[Tuple]):
    """别名拼音召回决策, 先缓存结果"""
    # 直接返回
    for distance, name_alias_pinyin_tone in name_alias_pinyin_tone_recall_res:
        # name_alias_pinyin_tone 映射成 name
        names = name_alias_pinyin_tone_mapping_name(name_alias_pinyin_tone)
        for name in names:
            enhance_pending_data.pending_data_rank_pre.add(name)


def longest_common_prefix_decision(
        enhance_pending_data: EnhancePendingData,
        distance: int
):
    pending_data_rank_pre = list(enhance_pending_data.pending_data_rank_pre)
    if len(pending_data_rank_pre) > 1:
        names_split = []
        for name in pending_data_rank_pre:
            names_split.append(name_to_pinyin_normal_split(name))
        # 拼音最大前缀和进一步删选
        ids = longest_common_prefix(enhance_pending_data.pending_data_pinyin_normal_split, names_split)
        # 映射成全名
        pending_data_rank_pre_filter = [pending_data_rank_pre[i] for i in ids]
        names = []
        for name in pending_data_rank_pre_filter:
            t_names = alias_name_mapping_name(name)
            if not t_names:
                names.append(name)
            else:
                names.extend(t_names)

        if len(names) == 1:
            enhance_pending_data.pending_data_rank_label = names[0]
            return pre(enhance_pending_data, distance)
        # 还未删选出来，返回客户确认
        else:
            enhance_pending_data.pending_data_rank_pre = set(names)
            return pre(enhance_pending_data, distance, True)
    else:
        for name in enhance_pending_data.pending_data_rank_pre:
            names = []
            t_names = alias_name_mapping_name(name)
            if not t_names:
                names.append(name)
            else:
                names.extend(t_names)
            if len(names) == 1:
                enhance_pending_data.pending_data_rank_label = names[0]
                return pre(enhance_pending_data, distance)
            # 还未删选出来，返回客户确认
            else:
                enhance_pending_data.pending_data_rank_pre = set(names)
                return pre(enhance_pending_data, distance, True)


def pre(enhance_pending_data: EnhancePendingData, distance=0, not_sure=False):
    # 递归停止条件 有预测结果 or distance>2 or 结果不能确定
    if enhance_pending_data.pending_data_rank_label or distance > 2 or not_sure:
        return enhance_pending_data

    if not enhance_pending_data.pending_data_rank_pre:
        enhance_pending_data.pending_data_rank_pre = set()

    if distance == 0:
        # 全名召回
        name_recall_res: List[Tuple] = sorted(name_recall(enhance_pending_data.pending_data))
        if name_recall_res:
            name_recall_res_decision(enhance_pending_data, name_recall_res)
            return pre(enhance_pending_data, distance)
        # 别名召回
        name_alias_recall_res: List[Tuple] = sorted(name_alias_recall(enhance_pending_data.pending_data))
        if name_alias_recall_res:
            name_alias_recall_res_decision(enhance_pending_data, name_alias_recall_res)
            # 别名映射成两个名字, 不确定, 返回用户确认
            if len(enhance_pending_data.pending_data_rank_pre) > 1:
                return pre(enhance_pending_data, distance, True)
            else:
                for name in enhance_pending_data.pending_data_rank_pre:
                    enhance_pending_data.pending_data_rank_label = name
                    return pre(enhance_pending_data, distance)
    # 拼音召回
    name_pinyin_normal_recall_res: List[Tuple] = \
        sorted(name_pinyin_normal_recall(enhance_pending_data.pending_data_pinyin_normal, distance))
    # 别名拼音召回
    name_alias_pinyin_normal_recall_res: List[Tuple] = \
        name_alias_pinyin_normal_recall(enhance_pending_data.pending_data_pinyin_normal, distance)
    if name_pinyin_normal_recall_res and not name_alias_pinyin_normal_recall_res:
        # 拼音召回决策
        name_pinyin_normal_recall_res_decision(
            enhance_pending_data,
            name_pinyin_normal_recall_res
        )
        return longest_common_prefix_decision(enhance_pending_data, distance)

    elif not name_pinyin_normal_recall_res and name_alias_pinyin_normal_recall_res:
        # 别名拼音召回决策
        name_alias_pinyin_normal_recall_res_decision(
            enhance_pending_data,
            name_alias_pinyin_normal_recall_res
        )
        return longest_common_prefix_decision(enhance_pending_data, distance)

    elif not name_pinyin_normal_recall_res and not name_alias_pinyin_normal_recall_res:
        distance += 1
        return pre(enhance_pending_data, distance)
    else:
        # 共同决策
        # 拼音召回决策
        name_pinyin_normal_recall_res_decision(
            enhance_pending_data,
            name_pinyin_normal_recall_res
        )
        name_pinyin_normal_pre = copy.deepcopy(enhance_pending_data.pending_data_rank_pre)
        enhance_pending_data.pending_data_rank_pre = set()
        # 别名拼音召回决策
        name_alias_pinyin_normal_recall_res_decision(
            enhance_pending_data,
            name_alias_pinyin_normal_recall_res
        )
        enhance_pending_data.pending_data_rank_pre.update(name_pinyin_normal_pre)
        return longest_common_prefix_decision(enhance_pending_data, distance)
    distance += 1
    return pre(enhance_pending_data, distance)


def recall_and_check_name(name: Text) -> List[Text]:
    # 召回并校验名字
    # pending_name = pre_process_pending_data([name])
    # pre_name = pre(pending_name[0]).pending_data_rank_label
    # if not pre_name:
    #     return []
    # return pre_name.split("|")
    res = pre(pre_process_pending_data([name])[0])
    if not res.pending_data_rank_label and not res.pending_data_rank_pre:
        return []
    return [res.pending_data_rank_label] if res.pending_data_rank_label else list(res.pending_data_rank_pre)


if __name__ == "__main__":
    pending_datas = ["李博","伟博","沈博","沈总","总裁","川博","刘总","超博","刘博","李丽","志强"]
    # pending_datas_labels = ["李伟","李伟","沈岗","沈岗","沈岗","王清川","刘晓宁","刘志超","刘志超","李立"]
    for i,name in enumerate(pending_datas):
        entity_names = recall_and_check_name(name)
        print(entity_names)



