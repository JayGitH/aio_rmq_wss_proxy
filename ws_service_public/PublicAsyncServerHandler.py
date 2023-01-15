import asyncio
import json

from logging import Logger

from typing import Dict

from server import AsyncServerHandler, SecuredWebsocketServerProtocol

from ws_service_public.PublicClientsController import PublicClientsController


class MessageKeys:
    EVENT = 'event'
    ROOM = 'room'
    RESULT = 'result'


class Events:
    SUBSCRIBE = 'subscribe'
    UNSUBSCRIBE = 'unsubscribe'


class PublicAsyncServerHandler(AsyncServerHandler):
    """

    Here we just need to override _process_data method to specify which commands supports by our server

    """

    def __init__(self, public_client_controller: PublicClientsController,
                 logger: Logger, exception_queue: asyncio.Queue):
        super(PublicAsyncServerHandler, self).__init__(public_client_controller, logger, exception_queue)

    async def _process_data(self, client_id: str, websocket: SecuredWebsocketServerProtocol, json_obj: Dict):
        event = json_obj.get(MessageKeys.EVENT)
        room_name = json_obj.get(MessageKeys.ROOM)

        if event == Events.SUBSCRIBE:
            if not self._clients_controller.check_room_exist(room_name):
                await self._send_unknown_room_message(websocket, room_name, event)

            else:
                self._clients_controller.subscribe_room(client_id, room_name)
                await self._send_subscribed_message(websocket, room_name)

        elif event == Events.UNSUBSCRIBE:
            if not self._clients_controller.check_room_exist(room_name):
                await self._send_unknown_room_message(websocket, room_name, event)

            else:
                self._clients_controller.unsubscribe_room(client_id, room_name)
                await self._send_unsubscribed_message(websocket, room_name)

        else:
            await self._send_unknown_event_message(websocket, event)

    async def _send_unknown_room_message(self, websocket: SecuredWebsocketServerProtocol, event: str, room_name: str):
        message = json.dumps({
            MessageKeys.EVENT: event,
            MessageKeys.ROOM: room_name,
            MessageKeys.RESULT: f'unknown room: {room_name}'
        })

        await websocket.send(message)
        self._logger.debug(f'{self.name} S > {message}')

    async def _send_subscribed_message(self, websocket: SecuredWebsocketServerProtocol, room_name: str):
        message = json.dumps({
            MessageKeys.EVENT: Events.SUBSCRIBE,
            MessageKeys.ROOM: room_name,
            MessageKeys.RESULT: 'OK'
        })

        await websocket.send(message)
        self._logger.debug(f'{self.name} S > {message}')

    async def _send_unsubscribed_message(self, websocket: SecuredWebsocketServerProtocol, room_name: str):
        message = json.dumps({
            MessageKeys.EVENT: Events.UNSUBSCRIBE,
            MessageKeys.ROOM: room_name,
            MessageKeys.RESULT: 'OK'
        })

        await websocket.send(message)
        self._logger.debug(f'{self.name} S > {message}')

    async def _send_unknown_event_message(self, websocket: SecuredWebsocketServerProtocol, event: str):
        message = json.dumps({
            MessageKeys.EVENT: event,
            MessageKeys.RESULT: f'unknown event: {event}'
        })

        await websocket.send(message)
        self._logger.debug(f'{self.name} S > {message}')