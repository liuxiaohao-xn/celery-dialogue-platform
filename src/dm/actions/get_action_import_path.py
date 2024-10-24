# -*- coding: utf-8 -*-
# @Time : 2022/8/10 15:12
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : get_action_import_path.py
from src.dm.actions.action import Action

if __name__ == '__main__':
    def get_subclasses(cls):
        for sub_cls in cls.__subclasses__():
            print('\t- '+sub_cls.__module__+'.'+sub_cls.__name__)
            if len(cls.__subclasses__()) > 0:
                get_subclasses(sub_cls)


    get_subclasses(Action)
