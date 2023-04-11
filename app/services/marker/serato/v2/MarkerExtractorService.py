import base64
import io
import struct

import mutagen

from app.models.MusicFile import MusicFile
from app.models.serato.ColorModel import ColorModel
from app.models.serato.EntryModel import EntryModel
from app.models.serato.EntryType import EntryType
from app.serializers.serato.ColorSerializer import ColorSerializer
from app.serializers.serato.EntrySerializer import EntrySerializer
from app.services.marker.BaseExtractorService import BaseExtractorService
from app.utils.colors import rgb_to_hex
from app.utils.serato import read_bytes
from app.utils.serato.type_detector import detect_type


class MarkerExtractorService(BaseExtractorService):
    @classmethod
    def source_name(cls):
        return "GEOB:Serato Markers2"

    def execute(self, file: MusicFile):
        assert isinstance(file, MusicFile)

        raw_file = file.location
        tagfile = mutagen.File(raw_file)
        if tagfile is not None:
            try:
                data = tagfile[self.source_name()].data
            except KeyError:
                print('File is missing "GEOB:Serato Markers2" tag')
                return 1
        else:
            with open(raw_file, mode='rb') as fp:
                data = fp.read()

        entries = list(self.__parse(data))

        if len(entries) == 0:
            entries = self.__create_empty_entries()

        return entries

    def __parse(self, data: list):
        version_len = struct.calcsize(self.FMT_VERSION)
        version = struct.unpack(self.FMT_VERSION, data[:version_len])
        assert version == (0x01, 0x01)

        b64data = data[version_len:data.index(b'\x00', version_len)].replace(b'\n', b'')
        padding = b'A==' if len(b64data) % 4 == 1 else (b'=' * (-len(b64data) % 4))
        payload = base64.b64decode(b64data + padding)
        fp = io.BytesIO(payload)
        assert struct.unpack(self.FMT_VERSION, fp.read(2)) == (0x01, 0x01)
        while True:
            entry_name = b''.join(read_bytes(fp)).decode('utf-8')
            if not entry_name:
                break

            entry_len = struct.unpack('>I', fp.read(4))[0]
            assert entry_len > 0

            yield detect_type(entry_name).deserialize(fp.read(entry_len))

    def __create_empty_entries(self):
        entries = []
        for item in range(0, 15):
            if item <= 4:
                entry = self.create_empty(EntryType.INVALID)
            elif item == 14:
                entry = self.create_empty_color()
            else:
                entry = self.create_empty(EntryType.LOOP)

            entries.append(entry)

        return entries

    @staticmethod
    def create_empty_color():
        return ColorModel(*[
            bytes.fromhex(rgb_to_hex(255, 255, 255)),
        ])

    @staticmethod
    def create_empty(entry_type: EntryType):
        return EntryModel(*[
            False,
            None,
            False,
            None,
            b'\x00\x7f\x7f\x7f\x7f\x7f',
            bytes.fromhex(rgb_to_hex(0, 0, 0)),
            entry_type,
            0
        ])
