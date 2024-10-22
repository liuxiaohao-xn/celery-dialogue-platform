# -*- coding: utf-8 -*-
# @Time : 2022/6/30 17:54
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : grpc_rsp.py
import logging
from typing import Text, List
import src.grpc.nlp_pb2 as nlp_pb2
from src.common.message import SysMsg
from src.common.grpc.grpc_req import Base, Request, DeviceInfo, InteractInfo, grpcs
from src.common.constant import YH_ROBOT_NLP_SUCCESS
from src.common.utils import format_tts_text, format_skill_name, format_intent_name

logger = logging.getLogger(__name__)


class Slot(Base):
    """提取的槽位信息"""

    def __init__(self, ):
        self.slot: Text = None
        self.norma_value: Text = None
        self.value: Text = None
        self.optional: bool = None
        self.extra: Text = ""
        """
        Args:
            slot: 槽位名
            norma_value: 槽位归一化值
            value: 槽位值
            optional: 是否可选
            extra: 根据业务透传数据
        """

    def __str__(self):
        return str({
            "name": self.slot,
            "value": self.value,
            "normal_value": self.norma_value,
            "optional": self.optional
        })


class RespContent(Base):
    """robot识别信息"""

    def __init__(self, ):
        self.asr_text: Text = None
        self.tts_text: Text = None
        self.skill_id: Text = None
        self.intent_id: Text = None
        self.session_end: bool = None
        self.confirm: bool = None
        self.ask_aiui: bool = None
        self.slots: List[nlp_pb2.NlpSlot] = None
        """
        Args:
            asr_text: asr文本
            tts_text: 系统回复文本，转tts使用
            skill_id: 命中的技能id，不是内部技能，是外部技能，如 秘书 为一个技能
            intent_id: 命中的意图id
            confirm: 意图是否确认
            slots: 提取的槽位信息
        """


class Response(Base):
    """robot回复信息"""

    def __init__(
            self,
            req: Request,
            sys_msg: SysMsg,
            code: int = YH_ROBOT_NLP_SUCCESS,
            msg: Text = "success",
    ):
        self.req = req
        self.sys_msg = sys_msg
        self.session_end = sys_msg.end
        self.confirm = sys_msg.confirm
        self.code = code
        self.msg = msg
        self.device_info: DeviceInfo = self.req.device_info
        self.interact_info: InteractInfo = self.req.interact_info
        self.content: RespContent = RespContent()
        """
        Args:
            req: 外部请求消息
            pre_msg:  内部系统消息
            end: 对话是否结束 对接confirm
            code: 返回码，成功 0， 错误 -1
        """
    def get_ext_slots(self):
        """获取提取到的实体"""
        slots = []
        for ext_entity in self.sys_msg.exd_entities:
            slot = Slot()
            slot.slot = ext_entity.slot_name
            slot.value = str(ext_entity.value)
            slot.norma_value = str(ext_entity.verify_value)
            slot.optional = False if ext_entity.required else True
            slots.append(slot.rev_transform(nlp_pb2.NlpSlot()))
        return slots

    def logging_exd_info(self, slots: List[Slot]):
        exd_info = {
            "skill_name": self.sys_msg.get_pre_skill(),
            "intent_id": self.content.intent_id,
            "intent_name": self.sys_msg.get_pre_intent(),
            "exd_slot": [
                {
                    "name": slot.slot,
                    "value": slot.value,
                    "normal_value": slot.norma_value,
                    "optional": slot.optional
                } for slot in slots
            ]
        }
        logger.info(f"exd_info: {exd_info}")
        logger.info(f"tts: {self.sys_msg.rsp}")

    def rev_transform(self, grpc_response: grpcs) -> grpcs:
        self.content.asr_text = self.req.content.asr_text
        self.content.tts_text = self.sys_msg.rsp
        self.content.tts_text = format_tts_text(self.content.tts_text)
        self.content.intent_id = self.sys_msg.get_pre_intent() if self.sys_msg.get_pre_intent() else ""
        self.content.skill_id = self.sys_msg.parsed_domain.intent_map_skill.get(
            self.content.intent_id
        ) if self.content.intent_id else ""
        self.content.intent_id, self.content.skill_id = format_intent_name(self.content.intent_id), \
                                                        format_skill_name(self.content.skill_id)
        self.content.session_end = self.session_end
        self.content.confirm = self.confirm
        self.content.ask_aiui = self.sys_msg.ask_aiui
        slots = self.get_ext_slots()
        self.logging_exd_info(slots)
        return grpc_response(
            code=self.code,
            msg=self.msg,
            # nlp_pb2.NlpRespContent.slots只能通过初始化赋值,
            # 通过set_attr会报Assignment not allowed to repeated field "slots" in protocol message object.
            content=nlp_pb2.NlpRespContent(
                asr_text=self.content.asr_text,
                tts_text=self.content.tts_text,
                skill_id=self.content.skill_id,
                intent_id=self.content.intent_id,
                session_end=self.content.session_end,
                confirm=self.content.confirm,
                ask_aiui=self.content.ask_aiui,
                slots=slots,
            ),
            device_info=self.device_info.rev_transform(nlp_pb2.NlpDeviceInfo()),
            interact_info=self.interact_info.rev_transform(nlp_pb2.NlpInteractInfo())
        )
