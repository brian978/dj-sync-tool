import base64

# noinspection PyPep8Naming
from mutagen.mp4 import MP4 as MutagenFile

from app.decoders.serato.mp3.v1.Mp3BeatgridDecoder import Mp3BeatgridDecoder
from app.utils.serato import join_string


class Mp4BeatgridDecoder(Mp3BeatgridDecoder):
    TAG_NAME = '----:com.serato.dj:beatgrid'
    TAG_VERSION = b'\x01\x00'
    MARKERS_NAME = b'Serato BeatGrid'

    def _read_data_from_tags(self, filepath: str) -> bytes | None:
        tags = MutagenFile(filepath).tags
        if self.TAG_NAME in tags:
            tag_data = tags[self.TAG_NAME][0]
            decoded = base64.b64decode(self._pad_encoded_data(join_string(tag_data)))
            return decoded.replace(b'application/octet-stream\x00\x00' + self.MARKERS_NAME + b'\x00', b'')

        return None

    @staticmethod
    def _pad_encoded_data(data: bytes):
        """
        Used when reading the data from the tags
        """
        padding = b'A==' if len(data) % 4 == 1 else (b'=' * (-len(data) % 4))

        return data + padding
