# -*- coding: utf-8 -*-
# @Time : 2022/6/22 11:30
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : component_container.py
from __future__ import annotations
from typing import Dict, Text, Any, Type, Tuple
import importlib
import inspect
from src.common.utils import read_yaml_file


class ComponentContainer:
    """
    组件管理器
        在 '../../resource/components.yml' 中注册的组件会转成Component的一个属性
        eg. 访问某个已注册的分类器:
            Component.ReluClassifier
    """

    @classmethod
    def load_register_component(cls, register_component_file_path: Text) -> None:
        cls.from_dict(read_yaml_file(register_component_file_path))

    @classmethod
    def from_dict(cls, serialized_components: Dict[Text, Any]) -> None:
        for _, lst_component in serialized_components.items():
            try:
                if not lst_component:
                    continue
                for component in lst_component:
                    class_name, klass = cls.class_from_module_path(component)
                    if class_name in cls.__dict__.keys():
                        e_klass = getattr(cls, class_name)
                        raise Exception(f" 组件 {class_name} 冲突，已存在注册组件：{e_klass} ，"
                                        f" {klass} 注册失败.")
                    setattr(cls, class_name, klass)
            except Exception as e:
                raise Exception(f"组件检索失败, {e}")

    @classmethod
    def get_register_klass(cls, klass_name: Text):
        """获取注册组件"""
        try:
            return getattr(cls, klass_name)
        except Exception:
            raise Exception(f"{klass_name}未找到")

    @classmethod
    def class_from_module_path(cls, module_path: Text) -> Tuple[Text, Type]:
        """根据类路径检索类"""

        module_name, _, class_name = module_path.rpartition(".")
        m = importlib.import_module(module_name)
        klass = getattr(m, class_name, None)

        if klass is None:
            raise ImportError(f"从 {module_path} 不能检索到class.")

        if not inspect.isclass(klass):
            raise Exception(f"从 {module_path} 检索到的类型不是class，是{type(klass)} .")

        return class_name, klass
