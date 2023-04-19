import base64
import struct
from io import BytesIO
from typing import Generator

# noinspection PyPep8Naming
from mutagen.mp4 import MP4 as MutagenFile

from app.decoders.serato.mp3.v1.Mp3Decoder import Mp3Decoder as Mp3DecoderV1
from app.models.MusicFile import MusicFile
from app.models.serato.EntryData import EntryData
from app.models.serato.EntryType import EntryType
from app.utils.serato import join_string, get_entry_name, split_string


class Mp3Decoder(Mp3DecoderV1):
    TAG_NAME = 'GEOB:Serato Markers2'
    TAG_VERSION = b'\x01\x01'
    MARKERS_NAME = 'Serato Markers2'

    def encode(self, music_file: MusicFile, entries: list) -> MutagenFile:
        payload = b''
        for entry in entries:
            assert isinstance(entry, EntryData)
            match entry.data_type():
                case EntryType.COLOR:
                    structured = self._dump_color_entry(entry)
                case EntryType.CUE:
                    structured = self._dump_cue_entry(entry)
                case EntryType.LOOP:
                    structured = self._dump_loop_entry(entry)
                case EntryType.BPM_LOCK:
                    structured = self._dump_bpm_lock_entry(entry)

                case _:
                    print(f'Invalid entry detected: {entry.data_type()}')
                    break

            assert structured is not None
            payload += structured

        return self._write_data_to_tags(music_file, self._enrich_payload(payload))

    def _enrich_payload(self, payload: bytes, entries_count: int | None = None):
        """
        Serato adds null padding at the end of the string.
        When the payload length is under 512 it pads until that number
        WHEN the payload is over 512 it pads until 1025

        Also, the payload is split at 72 characters before padding is applied
        """
        # Append the version for the non-encoded payload
        payload = self.TAG_VERSION + payload
        payload = self._remove_encoded_data_pad(base64.b64encode(payload))
        payload = self._pad_payload(split_string(payload))
        payload = super()._enrich_payload(payload, entries_count)

        return payload

    def _entry_data(self, data: bytes) -> Generator[EntryData, None, None]:
        fp = BytesIO(data)
        assert struct.unpack(self.FMT_VERSION, fp.read(2)) == (0x01, 0x01)
        payload = fp.read()
        data = join_string(self._remove_null_padding(payload))
        data = self._pad_encoded_data(data)
        decoded = base64.b64decode(data)

        fp = BytesIO(decoded)
        assert struct.unpack(self.FMT_VERSION, fp.read(2)) == (0x01, 0x01)

        while True:
            entry_name = get_entry_name(fp)  # NULL byte between name and length is already omitted
            if len(entry_name) == 0:
                break  # End of data

            struct_length = struct.unpack('>I', fp.read(4))[0]
            assert struct_length > 0  # normally this should not happen
            entry_data = fp.read(struct_length)

            match entry_name:
                case 'COLOR':
                    yield self._create_color_entry(struct.unpack('>c3s', entry_data))
                case 'CUE':
                    yield self.__create_cue_entry(self._extract_cue_data(entry_data), EntryType.CUE)
                case 'LOOP':
                    yield self.__create_cue_entry(self._extract_loop_data(entry_data), EntryType.LOOP)
                case 'BPMLOCK':
                    yield self._create_bpm_lock_entry(struct.unpack('>?', entry_data))

    @staticmethod
    def _remove_null_padding(payload: bytes):
        """
        Used when reading the data from the tags
        """
        return payload[:payload.index(b'\x00')]

    @staticmethod
    def _pad_encoded_data(data: bytes):
        """
        Used when reading the data from the tags
        """
        padding = b'A==' if len(data) % 4 == 1 else (b'=' * (-len(data) % 4))

        return data + padding

    @staticmethod
    def _remove_encoded_data_pad(data: bytes):
        """
        Used when after the base64 encode when writing data to the tags
        """
        return data.replace(b'=', b'A')

    @staticmethod
    def _pad_payload(payload: bytes):
        """
        Used when writing the data to the tags
        """
        length = len(payload)
        if length < 468:
            return payload.ljust(468, b'\x00')

        return payload.ljust(982, b'\x00') + b'\x00'

    @staticmethod
    def _create_color_entry(data: tuple) -> EntryData:
        obj = EntryData(EntryType.COLOR)
        obj.set('field1', data[0])  # just a NULL byte that is probably used for separation
        obj.set('color', data[1])

        return obj

    @staticmethod
    def __create_cue_entry(data: tuple, entry_type) -> EntryData:
        """
        ### CUE
        Struct: (INDEX,   POS_START, NULL, COLOR,     NULL, LOCKED, NAME,         NULL)
        Object: (b'\x00', 254,       0,    b'\xc0&&', 0,    False,  b'first bar', b'\x00')
        """
        obj = EntryData(entry_type)
        obj.set('index', data[0])
        obj.set('start_position_set', True)
        obj.set('start_position', data[1])
        obj.set('end_position_set', entry_type == EntryType.LOOP)
        obj.set('end_position', data[2])
        obj.set('field5', data[3])
        obj.set('color', data[4])
        obj.set('is_locked', bool(data[6]))
        obj.set('name', data[7].decode('utf-8'))
        obj.set('type', entry_type.value)

        return obj

    @staticmethod
    def _create_bpm_lock_entry(data: tuple) -> EntryData:
        obj = EntryData(EntryType.BPM_LOCK)
        obj.set('is_locked', data[0])

        return obj

    @staticmethod
    def _extract_cue_data(data: bytes) -> tuple:
        fp = BytesIO(data)
        fp.seek(1)  # first byte is NULL as it's a separator

        return (
            struct.unpack('>B', fp.read(1))[0],  # INDEX
            struct.unpack('>I', fp.read(4))[0],  # POSITION START
            struct.unpack('>B', fp.read(1))[0],  # NULL separator (aka POSITION END)
            None,  # aka. some field containing (4294967295, 39)
            struct.unpack('>3s', fp.read(3))[0],  # COLOR
            struct.unpack('>B', fp.read(1))[0],  # NULL separator
            struct.unpack('>?', fp.read(1))[0],  # LOCKED
            *fp.read().partition(b'\x00')[:-1]  # NAME + ending NULL separator
        )

    @staticmethod
    def _extract_loop_data(entry_data) -> tuple:
        fp = BytesIO(entry_data)
        fp.seek(1)  # first byte is NULL as it's a separator

        return (
            struct.unpack('>B', fp.read(1))[0],  # INDEX
            struct.unpack('>I', fp.read(4))[0],  # POSITION START
            struct.unpack('>I', fp.read(4))[0],  # POSITION END
            struct.unpack('>5s', fp.read(5))[0],  # some field containing (4294967295, 39)
            struct.unpack('>3s', fp.read(3))[0],  # COLOR - should be 3s
            struct.unpack('>B', fp.read(1))[0],  # NULL separator
            struct.unpack('>?', fp.read(1))[0],  # LOCKED
            *fp.read().partition(b'\x00')[:-1]  # NAME + ending NULL separator
        )

    def _dump_color_entry(self, entry_data: EntryData) -> bytes:
        """
        NAME   NULL  STRUCT LEN        NULL    COLOR
        COLOR  \x00  \x00\x00\x00\x04  \x00    \xff\xff\xff
        """
        data = b''.join((
            struct.pack('>B', 0),
            struct.pack('>3s', entry_data.get('color')),
        ))

        return b''.join([b'COLOR', b'\x00', struct.pack('>I', len(data)), data])

    def _dump_cue_entry(self, entry_data: EntryData) -> bytes:
        """
        NAME   NULL  STRUCT LEN          NULL    INDEX   POS START           POS END   COLOR  NULL  LOCKED  NAME        NULL
        CUE    \x00  \x00\x00\x00\x16    \x00    \x00    \x00\x00\x00\xfe    \x00      \xc0&& \x00  \x00    first bar   \x00
        """
        data = b''.join((
            struct.pack('>B', 0),
            struct.pack('>B', entry_data.get('index')),
            struct.pack('>I', entry_data.get('start_position')),
            struct.pack('>B', 0),
            struct.pack('>3s', entry_data.get('color')),
            struct.pack('>B', 0),
            struct.pack('>?', entry_data.get('is_locked')),
            entry_data.get('name').encode('utf-8'),
            struct.pack('>B', 0)
        ))

        return b''.join([b'CUE', b'\x00', struct.pack('>I', len(data)), data])

    @staticmethod
    def _dump_loop_entry(entry_data: EntryData) -> bytes:
        """
                                            >B      c       I                   I               5s                      3s              >B      ?
        NAME    NULL    STRUCT LEN          NULL    INDEX   POS START           POS END         SOMETHING               COLOR                   LOCKED  NAME        NULL
        LOOP    \x00    \x00\x00\x00\x1f    \x00    \x00    \x00\x00\x00\xfe    \x00\x00\t%     \xff\xff\xff\xff\x00'   \xaa\xe1        \x00    \x00    first loop  \x00
        :param entry_data:
        :return:
        """
        data = b''.join((
            struct.pack('>B', 0),
            struct.pack('>B', entry_data.get('index')),
            struct.pack('>I', entry_data.get('start_position')),
            struct.pack('>I', entry_data.get('end_position')),
            b'\xff\xff\xff\xff\x00',  # don't know what this is exactly
            struct.pack('>3s', entry_data.get('color')),
            struct.pack('>B', 0),
            struct.pack('>?', entry_data.get('is_locked')),
            entry_data.get('name').encode('utf-8'),
            struct.pack('>B', 0)
        ))

        return b''.join([b'LOOP', b'\x00', struct.pack('>I', len(data)), data])

    @staticmethod
    def _dump_bpm_lock_entry(entry_data: EntryData) -> bytes:
        """
        NAME     NULL  STRUCT LEN        LOCKED
        BPMLOCK  \x00  \x00\x00\x00\x01  \x00
        """
        data = b''.join((
            struct.pack('>?', entry_data.get('is_locked')),
        ))

        return b''.join([b'BPMLOCK', b'\x00', struct.pack('>I', len(data)), data])
