# -*- coding: utf-8 -*-
# @Time : 2022/11/7 15:04
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : dialogue_state.py
import copy
from typing import Text, List
import logging
from src.common.message import SysMsg
import src.common.utils as utils
from src.common.domain.domain import Monitor
from src.dm.dialogue_flow.slot_missing_dialogue_flow import SlotMissingDialogueFlow
from src.dm.dialogue_manage.dialogue_entity_info import DialogueStateEntityInfo
from src.common.utils import get_component_by_klass_name


logger = logging.getLogger(__name__)


class DialogueState:
    UNIQUE_NO = 0

    @property
    def TIME_OUT(self):
        return 60 * 1000  # ms

    @property
    def OVERFLOW_MAX_WAITED_ROUNDS(self):
        """对话未完成，此时切换到新的单轮对话，未完成对话等待轮数，超出后未完成对话将被注销。"""
        return 3

    def __init__(
            self,
            msg: SysMsg,
    ) -> None:
        self.start_time = utils.get_cur_timestamp()
        self.skill = msg.get_nlu_skill()
        self.intent = msg.get_nlu_intent()
        self.end = False
        self.overflow_waited_rounds = 0
        self.flow = None

    def timeout(self):
        cur_time = utils.get_cur_timestamp()
        intervals = cur_time - self.start_time
        if intervals > self.TIME_OUT:
            logger.info(f"对话已过期: {intervals/1000}s. ")
            return True
        return False

    def activate(self, new_msg: SysMsg) -> bool:
        ...

    def discard(self):
        return self.timeout()

    def process(self, new_msg: SysMsg) -> SysMsg:
        ...

    def ext(self, new_msg: SysMsg) -> SysMsg:
        """未识别到技能意图时，通过缓存的提取器来提取实体信息"""
        from src.nlu.extractors.extractor import Extractor
        for klass_name in new_msg.get_nlu_skill_pipeline(self.skill):
            component = get_component_by_klass_name(klass_name)
            if isinstance(component, Extractor):
                new_msg = component.process(new_msg)
        return new_msg

    def overflow_waited_rounds_increase(self):
        self.overflow_waited_rounds += 1

    def close(self):
        self.end = True

    def __lt__(self, other):
        return self.start_time < other.start_time


class NotCompleteDialogueState(DialogueState):
    UNIQUE_NO = 1

    @property
    def OVERFLOW_MAX_WAITED_ROUNDS(self):
        """对话未完成，此时切换到新的单轮对话，未完成对话等待轮数，超出后未完成对话将被注销。"""
        return 3

    def __init__(
            self,
            msg: SysMsg,
    ) -> None:

        super(NotCompleteDialogueState, self).__init__(
            msg=msg
        )
        self.dialogue_state_entity_info = DialogueStateEntityInfo(
            msg.get_intent_slots(self.intent)
        )
        self.flow = SlotMissingDialogueFlow(
            msg.get_nlu_intent()
        )

    def activate(self, new_msg: SysMsg) -> bool:
        return self.flow.activate(new_msg, self.dialogue_state_entity_info)

    def process(self, new_msg: SysMsg) -> SysMsg:
        # 执行flow链
        while self.flow:
            self.flow.process(new_msg, self.dialogue_state_entity_info)
            if self.flow.end:
                if not self.flow.next_flow:
                    break
                self.flow = self.flow.next_flow
            else:
                return self.flow.action(
                    new_msg
                )
        self.close()
        # todo msg中置结束标志
        new_msg.end = True
        return self.flow.action(new_msg)

    def overflow(self):
        if self.overflow_waited_rounds > self.OVERFLOW_MAX_WAITED_ROUNDS:
            return True
        return False

    def discard(self):
        return self.timeout() or self.overflow()


class CompleteDialogueState(DialogueState):
    UNIQUE_NO = 2

    def __init__(
            self,
            msg: SysMsg,
            monitor: Monitor
    ) -> None:

        super(CompleteDialogueState, self).__init__(
            msg=msg
        )
        self.monitor = monitor

    def activate(self, new_msg: SysMsg) -> bool:
        # 初始化的时候检查
        # slots = new_msg.get_cfg_intents().get(self.intent).slots
        # if self.monitor.slot not in slots.keys():
        #     raise Exception(f"{self.intent}在yaml配置的monitor.slot={self.monitor.slot}，在slots中不存在，请确认.")

        # todo entity.slot_name 为空，这里不能这样判断
        slot = new_msg.get_intent_target_slot(
            self.intent,
            slot_name=self.monitor.slot
        )
        for entity in new_msg.get_nlu_exd_entities():
            if entity.en in slot.polymorphism:
                entity.set_slot_info(slot)
                return True
        return False

    def process(self, new_msg: SysMsg) -> SysMsg:
        from src.common.component.component_container import ComponentContainer
        return ComponentContainer.get_register_klass(
            self.monitor.action
        )().run(new_msg, self.monitor)


class ViewDialogueState(DialogueState):
    UNIQUE_NO = 3

    def __init__(
            self,
            msg: SysMsg,
            view_name: Text = ""
    ) -> None:

        super(ViewDialogueState, self).__init__(
            msg=msg
        )
        self.views = {
            'take_a_photo': {
                "start": "准备好哦，3，2，1，茄子/看这里",
                "stop_02": "好的, 照相已停止",
                "continue": "准备好哦，3，2，1，茄子/看这里 ",
                "repeat": "准备好哦，3，2，1，茄子/看这里"
            },
            'take_a_video': {
                "start": "即将录像，3，2，1，开始",
                "stop_02": "好的, 录像已停止",
                "continue": "即将录像，3，2，1，开始",
                "repeat": "即将录像，3，2，1，开始"
            },
            # 'photo_album': {
            #     11, 12, 14, 15, 17, 18, 23
            # }
        }
        self.view_name = view_name
        self.monitor_intents: List[str] = []
        self.monitor_entries: List[Text] = []

    def activate(self, new_msg: SysMsg) -> bool:
        _intent = new_msg.get_nlu_intent()
        if self.view_name not in self.views.keys():
            logger.info(f"未找到视图{self.view_name}.")
            return False
        self.monitor_intents = list(self.views.get(
            self.view_name
        ).keys())
        if _intent in self.monitor_intents or _intent in self.monitor_entries:
            return True
        return False

    def ext(self, new_msg: SysMsg) -> SysMsg:
        return new_msg

    def process(self, new_msg: SysMsg) -> SysMsg:
        new_msg.rsp = self.views.get(self.view_name).get(
            new_msg.get_nlu_intent()
        )
        return new_msg


