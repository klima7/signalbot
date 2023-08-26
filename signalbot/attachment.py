import tempfile
import mimetypes
from pathlib import Path


class Attachment:
    
    def __init__(
        self,
        content_type: str = None,
        filename: str = None,
        data: bytes = None
    ):
        self.content_type = content_type
        self.filename = filename
        self.data = data
        
    def __repr__(self):
        return f'{type(self).__name__}(content_type={self.content_type}, filename={self.filename})'


class UploadAttachment(Attachment):
    
    def __init__(
        content_type: str = None,
        filename: str = None,
        data: bytes = None
    ):
        super().__init__(content_type, filename, data)


class DownloadAttachment(Attachment):
    
    def __init__(
        self,
        content_type: str = None,
        filename: str = None,
        id_: str = None,
        size: int = None,
        width: int = None,
        height: int = None,
        caption: str = None,
        upload_timestamp: int = None,
        raw_attachment: dict = None
    ):
        super().__init__(content_type, filename)
        
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
