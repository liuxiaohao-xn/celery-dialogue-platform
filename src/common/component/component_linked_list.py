# -*- coding: utf-8 -*-
# @Time : 2022/6/23 16:33
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : component_linked_list.py
from src.common.message import SysMsg


class Node:
    def __init__(self, component):
        self.component = component
        self.nex = None

    def process(self, msg: SysMsg) -> SysMsg:
        return self.component.process(msg)


class ComponentLinkedList:

    def __init__(self, head=None):
        self.head: Node = head

    def append(self, component) -> Node:
        """添加节点，返回添加的节点"""
        if not self.head:
            self.head = Node(component)
            return self.head
        cur = self.head
        while cur and cur.nex:
            cur = cur.nex
        cur.nex = Node(component)
        return cur.nex

    def tail(self) -> Node:
        cur = self.head
        while cur and cur.nex:
            cur = cur.nex
        return cur

    def find(self, component) -> Node:
        """查找节点，没有找到则添加，返回查找到的节点"""
        cur = self.head
        while cur and cur.component != component:
            cur = cur.nex
        return cur if cur else self.append(component)

