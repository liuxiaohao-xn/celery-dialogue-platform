# -*- coding: utf-8 -*-
# @Time : 2022/6/30 17:03
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : grpc_req.py
from __future__ import annotations
from typing import Text, List
import src.grpc.nlp_pb2 as nlp_pb2

grpcs = (nlp_pb2.NlpSkillReq, nlp_pb2.NlpReqContent, nlp_pb2.NlpDeviceInfo,
         nlp_pb2.NlpInteractInfo, nlp_pb2.NlpSkillInfo, nlp_pb2.NlpRespContent, nlp_pb2.NlpSlot,)


class Base:

    def pos_transform(self, grpc_req: grpcs) -> Base:
        """将grpc_req对象转成Base对象"""
        for attr in self.__dict__.keys():
            try:
                self.__setattr__(attr, grpc_req.__getattribute__(attr))
            except Exception:
                raise AttributeError(f"{self.__class__.__name__}.{attr}转换错误,"
                                     f"请检查{grpc_req.__class__.__name__}.{attr}是否存在.")
        return self

    def rev_transform(self, grpc_response: grpcs) -> grpcs:
        """将Base对象转成grpc_response对象"""
        for attr in self.__dict__.keys():
            try:
                grpc_response.__setattr__(attr, self.__getattribute__(attr))
            except Exception as e:
                raise AttributeError(f"{self.__class__.__name__}.{attr}转换错误,"
                                     f"{e}.")
        return grpc_response


class DeviceInfo(Base):
    """设备信息"""

    def __init__(self, ):
        self.device_sn: Text = None
        self.merchant_id: Text = None

        """
        Args:
            device_sn: 设备sn
            merchant_id: 商户id
        """


class ReqContent(Base):
    """ask文本"""

    def __init__(self):
        self.asr_text: Text = None

        """
        Args:
            asr_text: asr文本
        """


class InteractInfo(Base):
    """接口信息"""

    def __init__(self, ):
        self.interact_id: Text = None

        """
        Args:
            interact_id: 接口id
        """


class SkillInfo(Base):
    """需要查询的技能信息"""

    def __init__(self, ):
        self.code: Text = None

        """
        Args:
            code: 需要识别的技能标识
        """


class Request(Base):
    """robot请求信息"""

    def __init__(self, grpc_req: grpcs):
        self.content: ReqContent = ReqContent()
        self.device_info: DeviceInfo = DeviceInfo()
        self.interact_info: InteractInfo = InteractInfo()
        self.skill_list: List[SkillInfo] = []
        self.pos_transform(grpc_req)

    def pos_transform(self, grpc_req: grpcs) -> Base:
        self.content.pos_transform(grpc_req.content)
        self.device_info.pos_transform(grpc_req.device_info)
        self.interact_info.pos_transform(grpc_req.interact_info)
        self.skill_list = [
            SkillInfo().pos_transform(skill_info) for skill_info in grpc_req.skill_list
        ]


if __name__ == "__main__":
    content = nlp_pb2.NlpReqContent(
        asr_text="马上开会了"
    )
    device_info = nlp_pb2.NlpDeviceInfo(
        device_sn="device_sn",
        merchant_id="123"
    )
    interact_info = nlp_pb2.NlpInteractInfo(
        interact_id="1"
    )
    skill = nlp_pb2.NlpSkillInfo(
        code="秘书"
    )
    skill_list = [skill, skill, skill]

    nlp_skill_req = nlp_pb2.NlpSkillReq(
        content=content,
        device_info=device_info,
        interact_info=interact_info,
        skill_list=skill_list
    )
    req = Request(nlp_skill_req)
    print(req)
