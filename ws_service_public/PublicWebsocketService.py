import asyncio

from logging import Logger

from server import AsyncServer, MainServerLoop, SecuredWebsocketServerProtocol

from ws_service_public.PublicAsyncServerHandler import PublicAsyncServerHandler
from ws_service_public.PublicClientsController import PublicClientsController
from ws_service_public.PublicRmqConsumer import PublicRmqConsumer
from ws_service_public.PublicClientsSender import PublicClientsSender


class PublicWebsocketService(MainServerLoop):
    """

    Just need to describe our instances and that's all

    """

    def __init__(self, rmq_host: str, rmq_port: int,
                 ws_host: str, ws_port: int,
                 logger: Logger):
        exception_queue = asyncio.Queue()

        clients_controller = PublicClientsController(logger, exception_queue)

        async_server_handler = PublicAsyncServerHandler(clients_controller, logger, exception_queue)

        # setup for websocket instance which is like connected client
        SecuredWebsocketServerProtocol.CHECK_IP_ADDRESS_METHOD = None
        SecuredWebsocketServerProtocol.CHECK_TOKEN_METHOD = None
        SecuredWebsocketServerProtocol.FORWARDING_IS_ON = False

        async_server = AsyncServer(async_server_handler.do_action,
                                   SecuredWebsocketServerProtocol,
                                   ws_host, ws_port, logger)

        received_messages_queue = asyncio.Queue()

        aio_rmq_consumer = PublicRmqConsumer(rmq_host, rmq_port, received_messages_queue, logger, exception_queue)

        clients_sender = PublicClientsSender(received_messages_queue, clients_controller, logger, exception_queue)

        super(PublicWebsocketService, self).__init__('Public WS Service',
                                                     async_server,
                                                     async_server_handler,
                                                     aio_rmq_consumer,
                                                     clients_controller,
                                                     clients_sender,
                                                     logger,
                                                     exception_queue)
