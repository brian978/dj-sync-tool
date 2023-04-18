import struct
from io import BytesIO
from typing import Generator

from mutagen import id3
# noinspection PyPep8Naming
from mutagen.mp3 import MP3 as MutagenFile

from app.decoders.serato.BaseDecoder import BaseDecoder
from app.models.MusicFile import MusicFile
from app.models.serato.ColorModel import ColorModel
from app.models.serato.EntryData import EntryData
from app.models.serato.EntryModel import EntryModel
from app.models.serato.EntryType import EntryType
from app.utils.serato.encoder import decode, encode


class Mp3Decoder(BaseDecoder):
    STRUCT_LENGTH = 0x16
    TAG_NAME = 'GEOB:Serato Markers_'
    TAG_VERSION = b'\x02\x05'
    MARKERS_NAME = 'Serato Markers_'

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
                    structured = self._dump_color_entry(entry)

                case _:
                    structured = self._dump_cue_entry(entry)
                    entries_count += 1

            assert structured is not None
            payload += structured

        return self._write_data_to_tags(music_file, self._enrich_payload(payload, entries_count))

    def _enrich_payload(self, payload: bytes, entries_count: int | None = None):
        header = self.TAG_VERSION  # version
        if entries_count is not None:
            header += struct.pack('>I', entries_count)  # entries count

        return header + payload

    def _write_data_to_tags(self, music_file: MusicFile, payload: bytes):
        mutagen_file = MutagenFile(music_file.location)
        mutagen_file[self.TAG_NAME] = id3.GEOB(
            encoding=0,
            mime='application/octet-stream',
            desc=self.MARKERS_NAME,
            data=payload,
        )

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

            yield self._create_cue_entry(self._extract_cue_data(entry_data))

        yield self._create_color_entry(self._extract_color_data(fp.read()))

    @staticmethod
    def _get_entry_count(buffer: BytesIO):
        return struct.unpack('>I', buffer.read(4))[0]

    @staticmethod
    def _extract_cue_data(data: bytes) -> list:
        struct_fmt = '>B4sB4s6s4sBB'
        info_size = struct.calcsize(struct_fmt)
        info = struct.unpack(struct_fmt, data[:info_size])
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
                value = value
            entry_data.append(value)

        return entry_data

    @staticmethod
    def _extract_color_data(data: bytes) -> list:
        struct_fmt = '>4s'
        info_size = struct.calcsize(struct_fmt)
        info = struct.unpack(struct_fmt, data[:info_size])
        entry_data = []

        for field, value in zip(ColorModel.FIELDS, info):
            if field == 'color':
                value = decode(value)
            entry_data.append(value)

        return entry_data

    @staticmethod
    def _create_cue_entry(data: list) -> EntryData:
        entry_type = EntryType(int(data[6]))

        obj = EntryData(entry_type)
        obj.set('start_position_set', data[0])
        obj.set('start_position', data[1])
        obj.set('end_position_set', data[2])
        obj.set('end_position', data[3])
        obj.set('field5', data[4])
        obj.set('color', data[5])
        obj.set('type', int(data[6]))
        obj.set('is_locked', bool(data[7]))

        return obj

    # noinspection DuplicatedCode
    @staticmethod
    def _create_color_entry(data: list) -> EntryData:
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

    def _dump_cue_entry(self, entry_data: EntryData) -> bytes:
        return struct.pack('>B4sB4s6s4sBB', *(
            0x7F if not bool(entry_data.get('start_position_set')) else 0x00,
            self._parse_position(entry_data.get('start_position')),
            0x7F if not bool(entry_data.get('end_position_set')) else 0x00,
            self._parse_position(entry_data.get('end_position')),
            entry_data.get('field5'),
            encode(entry_data.get('color')),
            int(entry_data.get('type')),
            int(entry_data.get('is_locked'))
        ))

    @staticmethod
    def _parse_position(value):
        if value is None:
            value = 0x7F7F7F7F.to_bytes(4, 'big')
        else:
            value = encode(struct.pack('>I', value)[1:])

        return value

    def _dump_color_entry(self, entry_data: EntryData) -> bytes:
        return struct.pack('>4s', *(
            encode(entry_data.get('color')),
        ))
