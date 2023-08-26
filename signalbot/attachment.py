from abc import ABC
import tempfile
import mimetypes
from pathlib import Path


class UploadAttachment:
    
    def __init__(
        self,
        data: bytes,
        content_type: str | None = None,
        filename: str | None = None,
    ):
        self.content_type = content_type
        self.filename = filename
        self.data = data


class DownloadAttachment:
    
    def __init__(
        self,
        content_type: str,
        filename: str,
        id_: str,
        size: int,
        width: int,
        height: int,
        caption: str,
        upload_timestamp: int,
        raw_attachment: dict
    ):
        self.content_type = content_type
        self.filename = filename
        self.id_ = id_
        self.size = size
        self.width = width
        self.height = height
        self.caption = caption
        self.upload_timestamp = upload_timestamp
        self.raw_attachment = raw_attachment
        
    @classmethod
    def parse(cls, raw_attachment: str):
        return cls(
            content_type = raw_attachment.get('contentType'),
            filename = raw_attachment.get('filename'),
            id_ = raw_attachment.get('id'),
            size = raw_attachment.get('size'),
            width = raw_attachment.get('width'),
            height = raw_attachment.get('height'),
            caption = raw_attachment.get('caption'),
            upload_timestamp = raw_attachment.get('uploadTimestamp'),
            raw_attachment = raw_attachment
        )
        
    def get_filename(self, default='attachment'):
        if self.filename:
            return self.filename
        else:
            return default + mimetypes.guess_extension(self.content_type, strict=False)

        
    def save(self, path: str | None = None):
        self._assert_data()
        
        if path is None:
            directory = tempfile.mkdtemp()
            filename = self.get_filename(default='attachment')
            path = str(Path(directory) / filename)
            
        with open(path, "wb") as f:
            f.write(self.data)
            
        return path

    def _assert_data(self):
        assert self.data is not None, \
        "Attachment data is not fetched yet, call Context.fetch_attachment(attachment) first"
