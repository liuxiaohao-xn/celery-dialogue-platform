from typing import Text, Any
import json
import time
from src.dm.dialogue_flow.dialogue_flow import DialogueFlow
from src.common.message import SysMsg


class ViewManage(DialogueFlow):
    views = {}
    cur_view = {}
    cur_view_open_time = time.time()

    @classmethod
    def init_views(cls, view_json_path: Text) -> None:
        for view in json.load(
                open(view_json_path, encoding='utf-8')
        ):
            if view["view_id"] == 0:
                cls.cur_view = view
            view_key = f"{view['view_name']}_{view['view_id']}"
            cls.views.update({
                view_key: view
            })

    @classmethod
    def update_cur_view(cls, view_name: Text, view_id: id) -> None:
        try:
            cls.cur_view = cls.views.get(
                f"{view_name}_{view_id}"
            )
            cls.cur_view_open_time = time.time()
        except:
            raise Exception(f"{view_name}_{view_id} 不存在!")

    # todo 激活view条件  意图继承，首先只做意图系列，不做实体系列。
    def activate(self, msg: SysMsg, dialogue_state_entity_info: Any) -> bool:
        return False


if __name__ == "__main__":
    view_json_pat = r"./view.json"
    ViewManage.init_views(view_json_pat)
    print(
        ViewManage.views,
        '\n',
        ViewManage.cur_view,
        '\n',
        ViewManage.cur_view_open_time
    )
