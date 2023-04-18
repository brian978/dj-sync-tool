import base64
import struct
from io import BytesIO
from typing import Generator

# noinspection PyPep8Naming
from mutagen.mp3 import MP3 as MutagenFile

from app.decoders.serato.BaseDecoder import BaseDecoder
from app.models.MusicFile import MusicFile
from app.models.serato.EntryData import EntryData
from app.models.serato.EntryModel import EntryModel
from app.models.serato.EntryType import EntryType
from app.utils.serato import split_string
from app.utils.serato.encoder import decode


class Mp3Decoder(BaseDecoder):
    TAG_NAME = 'GEOB:Serato Markers_'
    TAG_VERSION = b'\x02\x05'
    MARKERS_NAME = b'Serato Markers_'

    def decode(self, music_file: MusicFile) -> list:
        assert isinstance(self._source, str)

        filepath = music_file.location
        data = self._read_data_from_tags(filepath)

        if data is None:
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

    def _write_data_to_tags(self, music_file: MusicFile, payload: bytes):
        data = split_string(self._add_padding(base64.b64encode(payload)))
        filepath = music_file.location
        mutagen_file = MutagenFile(filepath)
        tags = mutagen_file.tags
        tags[self.TAG_NAME][0] = MP4FreeForm(data)

        return mutagen_file

    def _read_data_from_tags(self, filepath: str) -> bytes | None:
        tags = MutagenFile(filepath)
        if self.TAG_NAME in tags:
            tag_data = tags[self.TAG_NAME]
            return tag_data.data

        return None

    def _entry_data(self, data: bytes) -> Generator[EntryData, None, None]:
        fp = BytesIO(data)
        assert struct.unpack(self.FMT_VERSION, fp.read(2)) == (0x02, 0x05)

        for i in range(self._get_entry_count(fp)):
            entry_data = fp.read(self.STRUCT_LENGTH)
            assert len(entry_data) == self.STRUCT_LENGTH

            yield self._create_cue_entry(self._extract_cue_data(entry_data), EntryType.CUE)

        yield self._create_color_entry(self._extract_color_data(fp.read()))

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

    @staticmethod
    def _extract_cue_data(data: bytes) -> tuple:
        info_size = struct.calcsize(EntryModel.FMT)
        info = struct.unpack(EntryModel.FMT, data[:info_size])
        entry_data = []

        start_position_set = None
        end_position_set = None
        for field, value in zip(EntryModel.FIELDS, info):
            if field == 'start_position_set':
                assert value in (0x00, 0x7F)
                value = value != 0x7F
                start_position_set = value
            elif field == 'end_position_set':
                assert value in (0x00, 0x7F)
                value = value != 0x7F
                end_position_set = value
            elif field == 'start_position':
                assert start_position_set is not None
                if start_position_set:
                    value = struct.unpack('>I', decode(value).rjust(4, b'\x00'))[0]
                else:
                    value = None
            elif field == 'end_position':
                assert end_position_set is not None
                if end_position_set:
                    value = struct.unpack('>I', decode(value).rjust(4, b'\x00'))[0]
                else:
                    value = None
            elif field == 'color':
                value = decode(value)
            elif field == 'type':
                value = EntryType(value)
            entry_data.append(value)

        return entry_data

    @staticmethod
    def _dump_cue_entry(entry_data: EntryData) -> tuple:
        return (
            entry_data.get('start_position'),
            entry_data.get('end_position'),
            b'\x00',
            b'\xff\xff\xff\xff',
            b'\x00',
            entry_data.get('color'),
            entry_data.get('type'),
            int(entry_data.get('is_locked'))
        )

    @staticmethod
    def _dump_color_entry(entry_data: EntryData) -> tuple:
        return (entry_data.get('color'),)

    def _extract_color_data(self, ) -> tuple:
        pass