# -*- coding: utf-8 -*-
# @Time : 2022/8/24 17:35
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : meeting_time_verify_dialogue_flow.py
from __future__ import annotations

from typing import List, Text, Tuple
from types import FunctionType
from src.common.message import SysMsg
from src.common.domain.domain import Entity, Slot
from src.common.domain.flow_names import FlowName
from src.common.constant import SystemIntent
from src.nlu.utils.verify.verifies import Verify
from src.dm.dialogue_flow.dialogue_flow import DialogueFlow, sync_msg
from src.dm.dialogue_manage.dialogue_entity_info import DialogueStateEntityInfo
from src.dm.dialogue_flow.entity_verify_dialogue_flow import EntityVerifyDialogueFlow


class MeetingTimeHangStatus:
    MEETING_TIME_OUT_MODE = "MEETING_TIME_OUT_MODE"
    MEETING_TIME_DATA_NOT_ALIGN_WEEK = "MEETING_TIME_DATA_NOT_ALIGN_WEEK"
    MEETING_TIME_CONFIRM = "MEETING_TIME_CONFIRM"
    MEETING_TIME_NOT_COMPLETION = "MEETING_TIME_NOT_COMPLETION"


class MeetingTimeActionStatus:
    MEETING_TIME_OUT_MODE = 1
    MEETING_TIME_DATA_NOT_ALIGN_WEEK = 2
    MEETING_TIME_CONFIRM = 3
    MEETING_TIME_NOT_COMPLETION = 4


class MeetingTimeVerifyDialogueFlow(EntityVerifyDialogueFlow):

    def __init__(self, intent: Text, hang_slot: Slot):
        super(EntityVerifyDialogueFlow, self).__init__(intent, hang_slot)
        self.hang_status = MeetingTimeHangStatus.MEETING_TIME_OUT_MODE
        self.action_status = MeetingTimeActionStatus.MEETING_TIME_OUT_MODE
        self.cash_date_morning: Tuple = None
        self.select_date_morning: List[Tuple] = None

    @property
    def name(self):
        return FlowName.MEETING_TIME_VERIFY_FLOW

    @property
    def next_flow(self):
        from src.dm.dialogue_flow.entity_repeat_dialogue_flow import EntityRepeatDialogueFlow
        return EntityRepeatDialogueFlow(self.intent, self.hang_slot)

    def skip_flow(self) -> bool:
        if not self.end \
                and self.hang_slot \
                and self.name in self.hang_slot.flows.keys():
            self.open()
            return False
        self.close()
        return True

    def entity_verify(self, entity: Entity) -> List[Text]:
        """实体验证"""
        try:
            verify_fn = getattr(Verify, entity.verify_fn)
        except:
            return [entity.value]
        if type(verify_fn) is FunctionType:
            return verify_fn(entity.value)
        return [entity.value]

    def action(self, msg: SysMsg) -> SysMsg:
        flow = self.get_flow(self.hang_slot)
        return self.get_action_eg(flow.action).run(
            msg,
            self.hang_slot,
            self.action_status,
            self.select_date_morning,
            flow
        )

    def exd_activate_info(self, entities: List[Entity]):
        """激活信息：提取实体中有hang_slot对应的实体"""
        for entity in entities:
            if entity.en in self.hang_slot.polymorphism:
                return True
        return False

    def activate(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> bool:
        """
        1.无意图
            - 提取到激活信息，激活成功
            - 否则激活失败，转AIUI
        2.有意图
            - 意图和历史意图相等，激活成功
            - 否则激活失败，切换意图
        """
        exd_entities = msg.get_exd_entities()
        pending_verified_entity_info = dialogue_state_entity_info.pending_verified_entity_info
        if not msg.get_pre_intent():
            if self.exd_activate_info(exd_entities):
                pending_verified_entity_info.append_not_verified_entities(exd_entities)
                return True
            return False
        else:
            if self.intent == msg.get_pre_intent():
                pending_verified_entity_info.append_not_verified_entities(exd_entities)
                return True
            elif msg.get_pre_intent() == SystemIntent.SELECT_DATE:
                return True
            else:
                return False

    def parse_date(self, date: Text) -> Tuple:
        if not date:
            raise Exception(f"无效date: {date}.")
        y, m, d = date.split(" ")[0].split("-")
        return int(y), int(m), int(d)

    def get_select_num(self, msg: SysMsg) -> int:
        for entity in msg.get_exd_entities():
            if entity.en == "number":
                return int(entity.value)
        raise Exception(f"未找到用户选择的日期.")

    def select_date(self, msg: SysMsg) -> Tuple:
        d = self.get_select_num(msg)
        for i_y, i_m, i_d in self.select_date_morning:
            if d == i_d:
                return i_y, i_m, i_d

    @sync_msg
    def process(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> DialogueFlow:

        if self.skip_flow():
            return self

        pending_verified_entity_info = dialogue_state_entity_info.pending_verified_entity_info

        if not pending_verified_entity_info.not_verified_entities:
            return self

        meeting_time_entity = pending_verified_entity_info.not_verified_entities[0]
        from src.nlu.extractors.sqz.time_extract_not_complete import Get_User_Time
        exd_time: Get_User_Time = meeting_time_entity.value

        # 过去式日期
        if self.hang_status == MeetingTimeHangStatus.MEETING_TIME_OUT_MODE:
            if exd_time.is_past_time():
                self.action_status = MeetingTimeActionStatus.MEETING_TIME_OUT_MODE
                return self
            self.hang_status = MeetingTimeHangStatus.MEETING_TIME_DATA_NOT_ALIGN_WEEK

        # 日期星期不对
        if self.hang_status == MeetingTimeHangStatus.MEETING_TIME_DATA_NOT_ALIGN_WEEK:
            if exd_time.is_wrong_week():
                self.action_status = MeetingTimeActionStatus.MEETING_TIME_DATA_NOT_ALIGN_WEEK
                self.hang_status = MeetingTimeHangStatus.MEETING_TIME_OUT_MODE
                return self
            self.hang_status = MeetingTimeHangStatus.MEETING_TIME_CONFIRM

        # 凌晨+明天
        if self.hang_status == MeetingTimeHangStatus.MEETING_TIME_CONFIRM:
            if self.intent == SystemIntent.SELECT_DATE:
                Get_User_Time.date_select(
                    self.select_date(msg)
                )
            else:
                if exd_time.is_date_morning():
                    self.cash_date_morning = exd_time.is_date_morning()
                    self.select_date_morning = [
                        self.parse_date(d) for d in self.cash_date_morning
                    ]
                    self.action_status = MeetingTimeActionStatus.MEETING_TIME_CONFIRM
                    return self
            self.hang_status = MeetingTimeHangStatus.MEETING_TIME_NOT_COMPLETION
        # 日期填充
        if self.hang_status == MeetingTimeHangStatus.MEETING_TIME_NOT_COMPLETION:
            if meeting_time_entity.value.update_above_time != Get_User_Time.TIME_COMPLETED:
                self.hang_status = MeetingTimeHangStatus.MEETING_TIME_NOT_COMPLETION
                return self
            print(Get_User_Time.origin_time)

        self.close()
        return self
