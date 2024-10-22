# -*- coding: utf-8 -*-
# @Time : 2022/6/30 15:51
# @Author : liuxiaohao
# @Email : liuxh4@infore.com
# @File : grpc_client.py
from __future__ import print_function
import grpc
import src.grpc.nlp_pb2_grpc as nlp_pb2_grpc
import src.grpc.nlp_pb2 as nlp_pb2


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = nlp_pb2_grpc.NlpServiceStub(channel)
        response = stub.Skill(nlp_pb2.NlpSkillReq(
            content=content,
            device_info=device_info,
            interact_info=interact_info,
            skill_list=skill_list
        ))
    print(f'code: {response.code}, msg:{response.msg}')


if __name__ == '__main__':
    content = nlp_pb2.NlpReqContent(
        asr_text="叫张三来开会"
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
    skill_list = [skill]
    run()
