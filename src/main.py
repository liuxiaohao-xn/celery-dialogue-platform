# -*- coding: utf-8 -*-
# @Time : 2022/7/1 13:41
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : main.py
from typing import Text
import logging
from src.common.message import SysMsg
from src import parsed_domain
from src.common.grpc.grpc_req import Request
from src.common.grpc.grpc_rsp import Response
import src.common.utils as utils
from src.dialogue import Dialogue

logger = logging.getLogger(__name__)


def chat(request: Request) -> Response:
    # logger.info(f"asr_text: {request.content.asr_text}")
    # logger.info(
    #     f"\n\n" +
    #     f"inference_start: \n" +
    #     f"  interact_id: {request.interact_info.interact_id}\n" +
    #     f"  query: {request.content.asr_text}\n\n"
    # )
    msg = SysMsg(
        auth_id=utils.get_auth_id(request),
        text=utils.rm_whitespace(
            request.content.asr_text
        ),
        parsed_domain=parsed_domain
    )
    # test change view
    # from src.dm.dialogue_manage.dialogue_manage import DialogueManage
    # dialogue_state_cash_chain = DialogueManage.get_dialogue_state_cash_chain(msg.auth_id)
    # dialogue_state_cash_chain.append(
    #     DialogueManage.make_view_dialogue_state(msg, request.view_name)
    # )

    msg = Dialogue(msg).run()
    return Response(
        request,
        msg,
    )



