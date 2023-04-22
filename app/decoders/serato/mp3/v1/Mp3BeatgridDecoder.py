import struct
from io import BytesIO

# noinspection PyPep8Naming
from mutagen.mp3 import MP3 as MutagenFile

from app.decoders.serato.BaseDecoder import BaseDecoder
from app.models.MusicFile import MusicFile
from app.models.serato.BpmMarkerModel import BpmMarkerModel


class Mp3BeatgridDecoder(BaseDecoder):
    TAG_NAME = 'GEOB:Serato BeatGrid'
    TAG_VERSION = b'\x01\x00'
    MARKERS_NAME = 'Serato BeatGrid'

    def decode(self, music_file: MusicFile) -> list[BpmMarkerModel]:
        filepath = music_file.location
        data = self._read_data_from_tags(filepath)

        if data is None:
            return list()

        return list(self._entry_data(data))

    def encode(self, music_file: MusicFile, entries: list) -> MutagenFile:
        raise NotImplementedError('The encode method of the decoder must be implemented!')

    def _read_data_from_tags(self, filepath: str) -> bytes | None:
        tags = MutagenFile(filepath)
        if self.TAG_NAME in tags:
            tag_data = tags[self.TAG_NAME]
            return tag_data.data

        return None

    def _entry_data(self, data: bytes):
        fp = BytesIO(data)
        version = struct.unpack(self.FMT_VERSION, fp.read(2))
        assert version == (0x01, 0x00)

        num_markers = self._get_entry_count(fp)
        for i in range(num_markers):
            position = struct.unpack('>f', fp.read(4))[0]
            data = fp.read(4)
            if i == num_markers - 1:
                bpm = struct.unpack('>f', data)[0]
                yield BpmMarkerModel(position, bpm)
            else:
                beats_till_next_marker = struct.unpack('>I', data)[0]
                yield BpmMarkerModel(position, 0, beats_till_next_marker)

        # # What's the meaning of the footer byte?
        # yield Footer(struct.unpack('B', fp.read(1))[0])
        # assert fp.read() == b''

    @staticmethod
    def _get_entry_count(buffer: BytesIO):
        return struct.unpack('>I', buffer.read(4))[0]
