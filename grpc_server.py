# -*- coding: utf-8 -*-
# @Time : 2022/6/30 15:00
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : grpc_server.py
import traceback
import grpc
import logging
from concurrent import futures
from typing import Text
import src.grpc.nlp_pb2_grpc as nlp_pb2_grpc
import src.grpc.nlp_pb2 as nlp_pb2
from src.common.grpc.grpc_req import Request
from src.common.constant import YH_ROBOT_NLP_ERROR
from src.main import chat

stream_handler = logging.StreamHandler()
logger = logging.getLogger(__name__)
logger.addHandler(stream_handler)


class Nlp(nlp_pb2_grpc.NlpService):

    @staticmethod
    def Skill(
            request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None
    ):
        try:
            return chat(
                Request(request)
            ).rev_transform(
                nlp_pb2.NlpSkillResp
            )
        except Exception as e:
            logger.error(e)
            logger.error("\n" + traceback.format_exc())
            return nlp_pb2.NlpSkillResp(
                code=YH_ROBOT_NLP_ERROR,
                msg="nlp系统内部错误.",
                content=nlp_pb2.NlpRespContent(),
                device_info=request.device_info,
                interact_info=request.interact_info
            )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    nlp_pb2_grpc.add_NlpServiceServicer_to_server(Nlp(), server)
    server.add_insecure_port('[::]:10005')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
