import logging

from concurrent import futures
from time import sleep, time

import grpc

from yuca.yuca_service_pb2 import ReadResponse, StartResponse, StopResponse, PurgeResponse
from yuca.yuca_service_pb2_grpc import YucaService, add_YucaServiceServicer_to_server
from yuca.nvml.sampler import create_report, NvmlSampler

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="yuca-nvml-server (%(asctime)s) [%(name)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S %p %Z",
    level=logging.DEBUG,
)

class YucaNvmlService(YucaService):
    def __init__(self):
        self.is_running = False
        self.executor = futures.ThreadPoolExecutor(1)

    def Start(self, request, context):
        self.sampler = NvmlSampler()
        self.is_running = True
        self.report = None
        logger.info('starting sampling taken one sample')
        self.sampler.sample()
        return StartResponse()

    def Stop(self, request, context):
        if self.is_running:
            self.sampler.sample()
            logger.info('stopping sampling taken one sample')
            self.report = create_report(self.sampler.samples)
            self.is_running = False
        else:
            logger.info('ignoring stop sampling request when not sampling')
        return StopResponse()

    def Read(self, request, context):
        logger.info('returning last report')
        # TODO: ignoring filtering because this should typically be small
        return ReadResponse(report=self.report)

    def Purge(self, request, context):
        logger.info('purging previous data')
        self.sampler.samples.clear()  # clear stored samples
        self.report = None 
        return PurgeResponse()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_YucaServiceServicer_to_server(YucaNvmlService(), server)
    server.add_insecure_port("localhost:8981")
    logger.info('starting yuca single sample nvml server at localhost:8981')
    server.start()
    server.wait_for_termination()
    logger.info('terminating...')


if __name__ == '__main__':
    serve()