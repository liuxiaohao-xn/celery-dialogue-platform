# -*- coding: utf-8 -*-
# @Time : 2022/8/3 11:02
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : slot_missing_dialogue_flow.py
from typing import List, Set, Text, Dict
import copy
from src.common.domain.domain import Slot, Entity
from src.common.domain.flow_names import FlowName
from src.common.message import SysMsg
from src.dm.dialogue_flow.dialogue_flow import DialogueFlow, sync_msg
from src.dm.dialogue_manage.dialogue_entity_info import DialogueStateEntityInfo

class DSStatus:

    TASKING_START = "TASKING_START"
    TASKING_SEEK_CONSENT = "TASKING_SEEK_CONSENT"
    TASKING_SEEK_ENTITY = "TASKING_SEEK_ENTITY"


class SlotMissingDialogueFlowDS(DialogueFlow):

    def __init__(self, intent: Text, hang_slot: Slot = None):
        self.status = DSStatus.TASKING_START
        super(SlotMissingDialogueFlowDS, self).__init__(intent, hang_slot)

    @property
    def name(self):
        return FlowName.SLOT_MISSING_FLOW_DS

    @property
    def next_flow(self) -> DialogueFlow:
        from src.dm.dialogue_flow.entity_verify_dialogue_flow import EntityVerifyDialogueFlow
        return EntityVerifyDialogueFlow(self.intent, self.hang_slot)

    def skip_flow(self) -> bool:
        if not self.end \
                and self.hang_slot \
                and self.name in self.hang_slot.flows.keys():
            self.open()
            return False
        self.close()
        return True

    def exd_activate_info(self, entities: List[Entity], cfg_slots: Dict[Text, Slot]):
        for entity in entities:
            for slot in cfg_slots.values():
                if slot.required and entity.en in slot.polymorphism:
                    return True
        return False
    
    def reset_entity(self, msg, dialogue_state_entity_info: DialogueStateEntityInfo):
        slot_missing_entity_info = dialogue_state_entity_info.slot_missing_entity_info
        # 增加水实体
        drink_entity = msg.get_o_entity("drink")
        drink_entity.set_ext_info(
            value="水",
            start_pos=-1,
            end_pos=-1
        )
        slot_missing_entity_info.exd_entities.append(drink_entity)

    def activate(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> bool:
        
        """以意图来激活，没意图不可激活"""
        intent = msg.get_nlu_intent()
        if not intent:
            return False
        if self.status == DSStatus.TASKING_START and intent=="YHI_ZG_FWQ_QWJ_YL":
            return True
        if self.status == DSStatus.TASKING_SEEK_CONSENT \
        and intent in {
            "YHI_ZG_FWQ_QWJ_YL",
            "YHI_ZG_FWQ_QWJ_YL_NUMS",
            "YHI_ZG_FWQ_QWJ_YL_GOODS",
            "YHI_ZG_FWQ_QWJ_YL_QX",
            "YHI_ZG_FWQ_SYS_QD",
            "YHI_ZG_FWQ_SYS_FD"
        }:
            self.reset_entity(msg, dialogue_state_entity_info)
            return True
        
        if self.status == DSStatus.TASKING_SEEK_ENTITY \
        and intent in {
            "YHI_ZG_FWQ_QWJ_YL",
            "YHI_ZG_FWQ_QWJ_YL_NUMS",
            "YHI_ZG_FWQ_QWJ_YL_GOODS",
            "YHI_ZG_FWQ_QWJ_YL_QX",
        }:
            self.reset_entity(msg, dialogue_state_entity_info)
            return True
        return False

    def action(self, msg: SysMsg) -> SysMsg:
        flow = self.get_flow(self.hang_slot)
        return self.get_action_eg(flow.action).run(
            msg,
            self.hang_slot,
            flow
        )

    def get_goal_entities(self, entities: List[Entity]):
        number_entities, drink_entities = [], []
        for entity in entities:
            if entity.en == 'number':
                number_entities.append(entity)
            elif entity.en == 'drink':
                drink_entities.append(entity)
        return number_entities, drink_entities
    
    @sync_msg
    def process(self, msg: SysMsg, dialogue_state_entity_info: DialogueStateEntityInfo) -> DialogueFlow:
        
        slot_missing_entity_info = dialogue_state_entity_info.slot_missing_entity_info
        if not self.hang_slot:
            self.hang_slot = slot_missing_entity_info.pop_missing_slot()

        if self.skip_flow():
            return self
        
        if msg.get_nlu_intent() == "YHI_ZG_FWQ_QWJ_YL_QX":
            self.intent = "YHI_ZG_FWQ_QWJ_YL_QX"
            self.close()
            return self
        # drink始终默认为水
        drink_entity = msg.get_o_entity("drink")
        drink_entity.set_ext_info(
            value="水",
            start_pos=-1,
            end_pos=-1
        )
        final_drink_entities = [drink_entity]

        cur_number_entities, cur_drink_entities = self.get_goal_entities(
            msg.get_nlu_exd_entities()
        )
        last_number_entities, last_drink_entities = self.get_goal_entities(
            slot_missing_entity_info.exd_entities
        )
        # 如果上轮有缓存结果，则默认为水
        if last_drink_entities:
            last_drink_entities = final_drink_entities
        # 以当前轮信息为主，没有则用上轮缓存结果
        cur_number_entities = cur_number_entities if cur_number_entities else last_number_entities
        cur_drink_entities = cur_drink_entities if cur_drink_entities else last_drink_entities


        if not cur_number_entities and not cur_drink_entities:
            self.status = DSStatus.TASKING_SEEK_ENTITY
            msg.rsp = "目前只提供矿泉水哦，请明确下，您要几杯？"
        elif not cur_number_entities and cur_drink_entities:
            self.status = DSStatus.TASKING_SEEK_ENTITY
            if len(cur_drink_entities)==1 and cur_drink_entities[0].value=="水":
                msg.rsp = "请问您要几杯？一次只能倒1至4杯"
            else:
                msg.rsp = "目前只提供矿泉水哦，请明确下，您要几杯？"
        elif cur_number_entities and not cur_drink_entities:
            if len(cur_number_entities)==1 and 1<=int(cur_number_entities[0].value)<=4:
                self.status = DSStatus.TASKING_SEEK_CONSENT
                msg.rsp = f"很抱歉，目前只提供矿泉水哦，给您倒{cur_number_entities[0].value}杯水可以吗"
            else:
                self.status = DSStatus.TASKING_SEEK_ENTITY
        else:
            if len(cur_drink_entities)==1 and cur_drink_entities[0].value=="水":
                if len(cur_number_entities)==1 and 1<=int(cur_number_entities[0].value)<=4:
                    if msg.get_nlu_intent() != "YHI_ZG_FWQ_SYS_FD":
                        msg.confirm = True
                    self.close()
                else:
                    self.status = DSStatus.TASKING_SEEK_ENTITY
                    msg.rsp = "请明确下，您要几杯？一次只能倒1至4杯"
            else:
                if len(cur_number_entities)==1 and 1<=int(cur_number_entities[0].value)<=4:
                    self.status = DSStatus.TASKING_SEEK_CONSENT
                    msg.rsp = f"很抱歉，目前只提供矿泉水哦，给您倒{cur_number_entities[0].value}杯水可以吗"
                else:
                    self.status = DSStatus.TASKING_SEEK_ENTITY
                    msg.rsp = "目前只提供矿泉水哦，请明确下，您要几杯？"
        slot_missing_entity_info.exd_entities = cur_number_entities + cur_drink_entities
        return self
            