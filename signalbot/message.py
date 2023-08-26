import json
from enum import Enum

from .attachment import ReceiveAttachment


class MessageType(Enum):
    SYNC_MESSAGE = 1
    DATA_MESSAGE = 2


class Message:
    def __init__(
        self,
        source: str,
        timestamp: int,
        type: MessageType,
        text: str,
        base64_attachments: list = None,
        group: str = None,
        reaction: str = None,
        mentions: list = None,
        raw_message: str = None,
    ):
        # required
        self.source = source
        self.timestamp = timestamp
        self.type = type
        self.text = text

        # optional
        self.base64_attachments = base64_attachments
        if self.base64_attachments is None:
            self.base64_attachments = []

        self.group = group

        self.reaction = reaction

        self.mentions = mentions
        if self.mentions is None:
            self.mentions = []

        self.raw_message = raw_message

    def recipient(self) -> str:
        # Case 1: Group chat
        if self.group:
            return self.group

        # Case 2: User chat
        return self.source

    @classmethod
    def parse(cls, raw_message: str):
        try:
            raw_message = json.loads(raw_message)
        except Exception:
            raise UnknownMessageFormatError

        # General attributes
        try:
            source = raw_message["envelope"]["source"]
            timestamp = raw_message["envelope"]["timestamp"]
        except Exception:
            raise UnknownMessageFormatError

        # Option 1: syncMessage
        if "syncMessage" in raw_message["envelope"]:
            type = MessageType.SYNC_MESSAGE
            text = cls._parse_sync_message(raw_message["envelope"]["syncMessage"])
            group = cls._parse_group_information(
                raw_message["envelope"]["syncMessage"]["sentMessage"]
            )
            reaction = cls._parse_reaction(
                raw_message["envelope"]["syncMessage"]["sentMessage"]
            )
            mentions = cls._parse_mentions(
                raw_message["envelope"]["syncMessage"]["sentMessage"]
            )
            base64_attachments = cls._parse_attachments(
                raw_message["envelope"]["syncMessage"]["sentMessage"]
            )

        # Option 2: dataMessage
        elif "dataMessage" in raw_message["envelope"]:
            type = MessageType.DATA_MESSAGE
            text = cls._parse_data_message(raw_message["envelope"]["dataMessage"])
            group = cls._parse_group_information(raw_message["envelope"]["dataMessage"])
            reaction = cls._parse_reaction(raw_message["envelope"]["dataMessage"])
            mentions = cls._parse_mentions(raw_message["envelope"]["dataMessage"])
            base64_attachments = cls._parse_attachments(raw_message["envelope"]["dataMessage"])

        else:
            raise UnknownMessageFormatError

        return cls(
            source,
            timestamp,
            type,
            text,
            base64_attachments,
            group,
            reaction,
            mentions,
            raw_message,
        )

    @classmethod
    def _parse_sync_message(cls, sync_message: dict) -> str:
        try:
            text = sync_message["sentMessage"]["message"]
            return text
        except Exception:
            raise UnknownMessageFormatError

    @classmethod
    def _parse_data_message(cls, data_message: dict) -> str:
        try:
            text = data_message["message"]
            return text
        except Exception:
            raise UnknownMessageFormatError

    @classmethod
    def _parse_group_information(self, message: dict) -> str:
        try:
            group = message["groupInfo"]["groupId"]
            return group
        except Exception:
            return None

    @classmethod
    def _parse_mentions(cls, data_message: dict) -> list:
        try:
            mentions = data_message["mentions"]
            return mentions
        except Exception:
            return []

    @classmethod
    def _parse_reaction(self, message: dict) -> str:
        try:
            reaction = message["reaction"]["emoji"]
            return reaction
        except Exception:
            return None
        
    @classmethod
    def _parse_attachments(self, message: dict) -> str:
        try:
            attachments = message["attachments"]
            attachments_obj = [ReceiveAttachment.parse(attachment) for attachment in attachments]
            return attachments_obj
        except Exception:
            return []

    def __str__(self):
        if self.text is None:
            return ""
        return self.text


class UnknownMessageFormatError(Exception):
    pass
