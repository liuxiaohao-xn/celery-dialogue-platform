# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import src.grpc.nlp_pb2 as nlp__pb2


class NlpServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Skill = channel.unary_unary(
                '/nlp.NlpService/Skill',
                request_serializer=nlp__pb2.NlpSkillReq.SerializeToString,
                response_deserializer=nlp__pb2.NlpSkillResp.FromString,
                )
        self.Emotion = channel.unary_unary(
                '/nlp.NlpService/Emotion',
                request_serializer=nlp__pb2.EmotionReq.SerializeToString,
                response_deserializer=nlp__pb2.EmotionResp.FromString,
                )


class NlpServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Skill(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Emotion(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_NlpServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Skill': grpc.unary_unary_rpc_method_handler(
                    servicer.Skill,
                    request_deserializer=nlp__pb2.NlpSkillReq.FromString,
                    response_serializer=nlp__pb2.NlpSkillResp.SerializeToString,
            ),
            'Emotion': grpc.unary_unary_rpc_method_handler(
                    servicer.Emotion,
                    request_deserializer=nlp__pb2.EmotionReq.FromString,
                    response_serializer=nlp__pb2.EmotionResp.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'nlp.NlpService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class NlpService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Skill(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nlp.NlpService/Skill',
            nlp__pb2.NlpSkillReq.SerializeToString,
            nlp__pb2.NlpSkillResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Emotion(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/nlp.NlpService/Emotion',
            nlp__pb2.EmotionReq.SerializeToString,
            nlp__pb2.EmotionResp.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
