""" a thin client to talk to a yuca server. """
import grpc

from yuca.yuca_service_pb2 import DumpRequest, PurgeRequest, ReadRequest, StartRequest, StopRequest
from yuca.yuca_service_pb2_grpc import YucaServiceStub

MAX_MESSAGE_LENGTH = 20 * 1024 * 1024

class YucaClient:
    def __init__(self, addr):
        channel = grpc.insecure_channel(
            addr,
            options=[
                ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
                ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH),
            ],
        )
        self.stub = YucaServiceStub(channel)

    def start(self, pid, period):
        self.stub.Start(StartRequest(process_id=pid, period_millis=period))

    def stop(self, pid):
        self.stub.Stop(StopRequest(process_id=pid))

    def dump(self, pid, output_path, signals):
        self.stub.Dump(DumpRequest(process_id=pid, output_path=output_path, signals=signals))

    def read(self, pid, signals):
        return self.stub.Read(ReadRequest(process_id=pid, signals=signals)).report

    def purge(self):
        return self.stub.Purge(PurgeRequest())
