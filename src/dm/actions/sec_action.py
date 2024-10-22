# -*- coding: utf-8 -*-
# @Time : 2022/6/17 10:33
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : sec_action.py
import random
import cn2an
import copy
from typing import Text, List, Tuple, Dict
from typing import Text, List, Tuple
from src.common.message import SysMsg
from src.common.domain.domain import Slot, Entity, Flow
from src.dm.actions.action import confirm, SlotMissingAction, EntityErrorAction, EntityRepeatAction, SuccessAction, \
    EntityFollowUpAction


class MeetingSuccessAction(SuccessAction):

    def format_to_zh_time(self, data_time: Text) -> Text:
        d, t = data_time.split(" ")
        s_d = []
        s_t = []
        for e_d, z_d in zip(d.split("-"), ["年", "月", "日"]):
            if z_d == "年":
                s_d.append(
                    "".join([cn2an.an2cn(ee_d) for ee_d in e_d]) + z_d
                )
            else:
                s_d.append(
                    cn2an.an2cn(e_d) + z_d
                )

        for idx, x_t in enumerate(zip(t.split(":"), ["点", "分", "秒"])):
            e_t, z_t = x_t[0], x_t[1]
            if int(e_t) == 0:
                break
            ee_t = ""
            if int(e_t) < 6:
                ee_t = "凌晨" if idx == 0 else ee_t
                s_t.append(ee_t + cn2an.an2cn(e_t) + z_t)
            elif int(e_t) < 12:
                ee_t = "上午" if idx == 0 else ee_t
                s_t.append(ee_t + cn2an.an2cn(e_t) + z_t)
            elif int(e_t) == 12:
                ee_t = "中午" if idx == 0 else ee_t
                s_t.append(ee_t + cn2an.an2cn(e_t) + z_t)
            elif int(e_t) < 19:
                if idx == 0:
                    ee_t = "下午"
                    e_t = int(e_t) - 12
                else:
                    e_t = int(e_t)
                s_t.append(ee_t + cn2an.an2cn(e_t) + z_t)
            else:
                if idx == 0:
                    ee_t = "晚上"
                    e_t = int(e_t) - 12
                else:
                    e_t = int(e_t)
                s_t.append(ee_t + cn2an.an2cn(e_t) + z_t)
        return "".join(s_d) + " " + "".join(s_t)

    def get_attendees(self, entities: List[Entity]) -> List[Text]:
        attendees = []
        for entity in entities:
            if entity.en == "peo" or entity.en == "dep":
                attendees.append(entity.verify_value)
        return attendees

    def get_meeting_time(self, entities: List[Entity]) -> Text:
        for entity in entities:
            if entity.en == "time":
                return self.format_to_zh_time(entity.verify_value)

    @confirm
    def run(self, msg: SysMsg, intent: Text, flow: Flow) -> SysMsg:
        exd_entities = msg.exd_entities
        attendee_info = " ".join(self.get_attendees(exd_entities))
        time_info = self.get_meeting_time(exd_entities)
        msg.rsp = f"好的, 您的会议预定成功. " \
                  f"会议时间: {time_info}." \
                  f"邀请的参会人员: {attendee_info}." \
                  f"请记得准时参加 ."
        return msg


class AttendeeSlotMissingAction(SlotMissingAction):

    def run(self, msg: SysMsg, missing_slot: Slot, flow: Flow) -> SysMsg:
        return super(AttendeeSlotMissingAction, self).run(msg, missing_slot, flow)


class MeetingTimeSlotMissingAction(SlotMissingAction):

    def run(self, msg: SysMsg, missing_slot: Slot, flow: Flow) -> SysMsg:
        return super(MeetingTimeSlotMissingAction, self).run(msg, missing_slot, flow)


class MeetingTimeErrorAction(EntityErrorAction):

    def run(self, msg: SysMsg, slot: Slot, error_entities: List[Entity], flow: Flow) -> SysMsg:
        msg.rsp = random.choice(flow.response)
        return msg


class AttendeeErrorAction(EntityErrorAction):

    def run(self, msg: SysMsg, slot: Slot, multi_entities: List[Entity],
            error_entities: List[Entity], flow: Flow) -> SysMsg:
        error_staffs = "、".join([entity.value for entity in error_entities])
        msg.rsp = f"找不到{error_staffs}, 请说出正确的参会人？"
        return msg


class AttendeeRepeatAction(EntityRepeatAction):

    def run(self, msg: SysMsg, slot: Slot, repeat_entity: Tuple[Entity, List[Text]], flow: Flow) -> SysMsg:
        entity, repeat_names = repeat_entity
        s_repeat_names = "还是".join(repeat_names)
        msg.rsp = f"{entity.value}有重名, 是想邀请{s_repeat_names}呢，请选择."
        return msg


class AttendeeFollowUpAction(EntityFollowUpAction):

    def run(self, msg: SysMsg, slot: Slot, flow: Flow, activate_type: int) -> SysMsg:
        msg.rsp = random.choice(flow.response)
        return msg


class CalleeRepeatAction(EntityRepeatAction):

    def run(self, msg: SysMsg, slot: Slot, repeat_entity: Tuple[Entity, List[Text]], flow: Flow) -> SysMsg:
        entity, repeat_names = repeat_entity
        s_repeat_names = "还是".join(repeat_names)
        msg.rsp = f"{entity.value}有重名, 是想呼叫{s_repeat_names}呢，请选择第几个"
        return msg


class CalleeErrorAction(EntityErrorAction):

    def run(self, msg: SysMsg, slot: Slot, multi_entities: List[Entity],
            error_entities: List[Entity], flow: Flow) -> SysMsg:
        if multi_entities:
            msg.rsp = f"哎呀, 不支持多人呼叫, 请呼叫其中一个。"
            return msg
        error_callees = "、".join([entity.value for entity in error_entities])
        msg.rsp = f"找不到被呼叫人{error_callees}, 请重说."
        return msg


class MakeCallSuccessAction(SuccessAction):

    @confirm
    def run(self, msg: SysMsg, intent: Text, flow: Flow) -> SysMsg:
        return super(MakeCallSuccessAction, self).run(msg, intent, flow)


class TakeWaterAction(SuccessAction):
    @confirm
    def run(self, msg: SysMsg, intent: Text, flow: Flow) -> SysMsg:
        msg.rsp = random.choice(flow.response)
        if not msg.exd_entities:
            entity = copy.deepcopy(msg.get_cfg_entity_by_name("number"))
            entity.set_ext_info("1", -1, -1)
            msg.exd_entities.append(entity)

            slots = msg.get_cfg_slots_by_intent(intent)
            for _, slot in slots.items():
                if "number" in slot.polymorphism:
                    entity.set_slot_info(slot)
                    break
        return msg


