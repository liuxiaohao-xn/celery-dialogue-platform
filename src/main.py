# -*- coding: utf-8 -*-
# @Time : 2022/7/1 13:41
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : main.py
from typing import Text
from src.common.message import SysMsg
from src import parsed_domain
from src.common.grpc.grpc_req import Request
from src.common.grpc.grpc_rsp import Response
import src.common.utils as utils
from src.dialogue import Dialogue


def chat(request: Request) -> Response:
    auth_id: Text = utils.get_auth_id(request)
    session_id = utils.build_session_id_by_auth_id(auth_id)
    text: Text = request.content.asr_text
    msg = SysMsg(
        auth_id=auth_id,
        session_id=session_id,
        text=text,
        parsed_domain=parsed_domain
    )
    msg = Dialogue(msg).run()
    return Response(
        request,
        msg,
    )



