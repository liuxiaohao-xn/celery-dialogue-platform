# -*- coding: utf-8 -*-
# @Time : 2022/6/15 13:43
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : constant.py
from enum import Enum

# 对话销毁
DIALOGUE_TIMEOUT = 100
DIALOGUE_MAX_ROUND = -1
# 系统返回码
YH_ROBOT_NLP_SUCCESS = 0
YH_ROBOT_NLP_ERROR = -1


class Constant(Enum):

    @classmethod
    def get_names(cls):
        return cls._member_names_

    @classmethod
    def get_values(cls):
        values = []
        for name, _ in cls._value2member_map_.items():
            values.append(name)
        return values


class TermKey(Constant):
    SKILL = "skill"
    INTENT = "intent"
    EXT_ENTITIES = "ext_entities"


class ComponentResKey(Constant):
    """组件预测结果key命名"""
    SKILL_RES = "skill_res"
    NLU_CLS_RES = "nlu_cls_res"
    NLU_EXT_RES = "nlu_ext_res"
    NLU_TKZ_RES = "nlu_tkz_res"
    POLICY_RES = "policy_res"


class ActionKey(Constant):
    DATA = "data"
    DEFAULT_RSP = "default_rsp"


class Entity(Constant):
    PEO = "peo"
    DEP = "dep"
    TIME = "time"
    NUMBER = "number"


class ActivateType:
    ACTIVATE_FROM_FLOW = 0
    ACTIVATE_YES = 1
    ACTIVATE_NO = 2
    ACTIVATE_SAME_INTENT = 3
    ACTIVATE_SELECT = 4


class SystemIntent:
    POSITIVE = "positive"
    NEGATIVE = "negative"
    CANCEL = "cancel"
    SELECT = "select"
    SELECT_DATE = "select_date"

    @classmethod
    def system_intent(cls, ):
        return [
            cls.POSITIVE,
            cls.NEGATIVE,
            cls.CANCEL,
            cls.SELECT,
            cls.SELECT_DATE
        ]
