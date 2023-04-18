import base64
import struct
from io import BytesIO
from typing import Generator

# noinspection PyPep8Naming
from mutagen.mp4 import MP4 as MutagenFile
from mutagen.mp4 import MP4FreeForm

from app.decoders.serato.BaseDecoder import BaseDecoder
from app.models.MusicFile import MusicFile
from app.models.serato.EntryData import EntryData
from app.models.serato.EntryType import EntryType
from app.utils.serato import split_string, join_string


class Mp4Decoder(BaseDecoder):
    STRUCT_LENGTH = 0x13
    STRUCT_FMT = '>IIc4sc3sBB'
    TAG_NAME = '----:com.serato.dj:markers'
    TAG_VERSION = b'\x02\x05'
    MARKERS_NAME = b'Serato Markers_'

    def decode(self, music_file: MusicFile) -> list:
        assert isinstance(self._source, str)

        filepath = music_file.location
        data = self._read_data_from_tags(filepath)

        if data is None or len(data) == 0:
            return list()

        return list(self._entry_data(data))

    def encode(self, music_file: MusicFile, entries: list) -> MutagenFile:
        assert isinstance(self._source, str)

        payload = b''
        entries_count = 0
        for entry in entries:
            assert isinstance(entry, EntryData)
            match entry.data_type():
                case EntryType.COLOR:
                    structured = struct.pack('>4s', *self._dump_color_entry(entry))

                case _:
                    structured = struct.pack(self.STRUCT_FMT, *self._dump_cue_entry(entry))
                    entries_count += 1

            assert structured is not None
            payload += structured

        return self._write_data_to_tags(music_file, self._enrich_payload(payload, entries_count))

    def _enrich_payload(self, payload: bytes, entries_count: int | None = None):
        header = b'application/octet-stream\x00\x00' + self.MARKERS_NAME + b'\x00'  # header
        header += self.TAG_VERSION  # version

        if entries_count is not None:
            header += struct.pack('>I', entries_count)  # entries count

        return header + payload

    def _write_data_to_tags(self, music_file: MusicFile, payload: bytes):
        data = split_string(self._pad_payload(base64.b64encode(payload)))
        filepath = music_file.location
        mutagen_file = MutagenFile(filepath)
        mutagen_file[self.TAG_NAME] = MP4FreeForm(data)

        return mutagen_file

    def _read_data_from_tags(self, filepath: str) -> bytes | None:
        tags = MutagenFile(filepath).tags
        if self.TAG_NAME in tags:
            tag_data = tags[self.TAG_NAME][0]
            decoded = base64.b64decode(self._pad_encoded_data(join_string(tag_data)))
            return decoded.replace(b'application/octet-stream\x00\x00' + self.MARKERS_NAME + b'\x00', b'')

        return None

    def _entry_data(self, data: bytes) -> Generator[EntryData, None, None]:
        fp = BytesIO(data)
        assert struct.unpack(self.FMT_VERSION, fp.read(2)) == (0x02, 0x05)

        # First 5 are CUE points
        # Next 9 are loops (only the first 8 are populated)
        for i in range(self._get_entry_count(fp)):
            entry_data = fp.read(self.STRUCT_LENGTH)
            assert len(entry_data) == self.STRUCT_LENGTH
            destructured = struct.unpack(self.STRUCT_FMT, entry_data)

            if i < 4:
                yield self._create_cue_entry(destructured, EntryType.CUE)
            elif 4 <= i <= 14:
                yield self._create_cue_entry(destructured, EntryType.LOOP)

        # Last 4 bytes are the color of the track
        yield self._create_color_entry(struct.unpack('>4s', fp.read(4)))

    @staticmethod
    def _pad_encoded_data(data: bytes):
        """
        Used when reading the data from the tags
        """
        padding = b'A==' if len(data) % 4 == 1 else (b'=' * (-len(data) % 4))

        return data + padding

    @staticmethod
    def _pad_payload(data: bytes):
        """
        Used when writing the data to the tags
        """
        length = len(data)
        padding = abs(1 - length % 4)

        return data.ljust(length + padding, b'A')

    @staticmethod
    def _get_entry_count(buffer: BytesIO):
        return struct.unpack('>I', buffer.read(4))[0]

    @staticmethod
    def _create_cue_entry(data: tuple, entry_type: EntryType) -> EntryData:
        obj = EntryData(entry_type)
        obj.set('start_position_set', not (data[0] == 4294967295))
        obj.set('start_position', data[0])
        obj.set('end_position_set', not (data[1] == 4294967295))
        obj.set('end_position', data[1])
        obj.set('field5', None)
        obj.set('color', data[5])
        obj.set('type', int(data[6]))
        obj.set('is_locked', bool(data[7]))

        return obj

    @staticmethod
    def _create_color_entry(data: tuple) -> EntryData:
        obj = EntryData(EntryType.COLOR)
        obj.set('start_position_set', False)
        obj.set('start_position', None)
        obj.set('end_position_set', False)
        obj.set('end_position', None)
        obj.set('field5', None)
        obj.set('color', data[0])
        obj.set('type', EntryType.COLOR)
        obj.set('is_locked', False)

        return obj

    def _dump_cue_entry(self, entry_data: EntryData) -> tuple:
        return (
            self._parse_position(entry_data.get('start_position')),
            self._parse_position(entry_data.get('end_position')),
            b'\x00',
            b'\xff\xff\xff\xff',
            b'\x00',
            entry_data.get('color'),
            entry_data.get('type'),
            int(entry_data.get('is_locked'))
        )

    @staticmethod
    def _parse_position(value):
        if value is None:
            value = 4294967295

        return value

    @staticmethod
    def _dump_color_entry(entry_data: EntryData) -> tuple:
        color = entry_data.get('color')
        if len(color) < 4:
            color = color.rjust(4, b'\x00')

        return (color,)
