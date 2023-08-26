import aiohttp
import base64
import websockets

from .attachment import DownloadAttachment


class SignalAPI:
    def __init__(
        self,
        signal_service: str,
        phone_number: str,
    ):
        self.signal_service = signal_service
        self.phone_number = phone_number

        # self.session = aiohttp.ClientSession()

    async def receive(self):
        try:
            uri = self._receive_ws_uri()
            self.connection = websockets.connect(uri, ping_interval=None)
            async with self.connection as websocket:
                async for raw_message in websocket:
                    yield raw_message

        except Exception as e:
            raise ReceiveMessagesError(e)

    async def send(
        self, receiver: str, message: str, attachments: list = None
    ) -> aiohttp.ClientResponse:
        uri = self._send_rest_uri()
        if attachments is None:
            attachments = []
        base64_attachments = [self._cvt_attachment_to_base64(attachment) for attachment in attachments]
        if base64_attachments:
            print(base64_attachments[0][:500], flush=True)
            print('*'*200, flush=True)
        payload = {
            "base64_attachments": base64_attachments,
            "message": message,
            "number": self.phone_number,
            "recipients": [receiver],
        }
        # try:
        async with aiohttp.ClientSession() as session:
            resp = await session.post(uri, json=payload)
            resp.raise_for_status()
            return resp
        # except (
        #     aiohttp.ClientError,
        #     aiohttp.http_exceptions.HttpProcessingError,
        #     KeyError,
        # ):
        #     raise SendMessageError

    async def react(
        self, recipient: str, reaction: str, target_author: str, timestamp: int
    ) -> aiohttp.ClientResponse:
        uri = self._react_rest_uri()
        payload = {
            "recipient": recipient,
            "reaction": reaction,
            "target_author": target_author,
            "timestamp": timestamp,
        }
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.post(uri, json=payload)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise ReactionError

    async def start_typing(self, receiver: str):
        uri = self._typing_indicator_uri()
        payload = {
            "recipient": receiver,
        }
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.put(uri, json=payload)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise StartTypingError

    async def stop_typing(self, receiver: str):
        uri = self._typing_indicator_uri()
        payload = {
            "recipient": receiver,
        }
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.delete(uri, json=payload)
                resp.raise_for_status()
                return resp
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise StopTypingError
        
    async def fetch_attachment(self, attachment: DownloadAttachment):
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(self._fetch_attachment_uri(attachment.id_))
                resp.raise_for_status()
                attachment.data = await resp.read()
        except (
            aiohttp.ClientError,
            aiohttp.http_exceptions.HttpProcessingError,
        ):
            raise FetchAttachmentError

    def _receive_ws_uri(self):
        return f"ws://{self.signal_service}/v1/receive/{self.phone_number}"

    def _send_rest_uri(self):
        return f"http://{self.signal_service}/v2/send"

    def _react_rest_uri(self):
        return f"http://{self.signal_service}/v1/reactions/{self.phone_number}"

    def _typing_indicator_uri(self):
        return f"http://{self.signal_service}/v1/typing-indicator/{self.phone_number}"
    
    def _fetch_attachment_uri(self, attachment_id: str):
        return f"http://{self.signal_service}/v1/attachments/{attachment_id}"
    
    @staticmethod
    def _cvt_attachment_to_base64(attachment):
        result = ''
        if attachment.content_type:
            result += f'data:{attachment.content_type};'
        if attachment.filename:
            result += f'filename={attachment.filename};'
        if attachment.content_type or attachment.filename:
            result += 'base64,'
        result += base64.b64encode(attachment.data).decode('utf-8')
        return result


class ReceiveMessagesError(Exception):
    pass


class SendMessageError(Exception):
    pass


class TypingError(Exception):
    pass


class StartTypingError(TypingError):
    pass


class StopTypingError(TypingError):
    pass


class ReactionError(Exception):
    pass


class FetchAttachmentError(Exception):
    pass
