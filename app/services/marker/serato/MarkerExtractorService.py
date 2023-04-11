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


class MarkerExtractorService(BaseExtractorService):
    @classmethod
    def source_name(cls):
        return "GEOB:Serato Markers_"

    def execute(self, file: MusicFile):
        assert isinstance(file, MusicFile)

        raw_file = file.location
        tagfile = mutagen.File(raw_file)

        if tagfile is not None:
            try:
                data = tagfile[self.source_name()].data
            except KeyError:
                print('File is missing "GEOB:Serato Markers_" tag')
                return 1
        else:
            with open(raw_file, mode='rb') as fp:
                data = fp.read()

        entries = list(self.__parse(io.BytesIO(data)))

        if len(entries) == 0:
            entries = self.__create_empty_entries()

        return entries

    def __parse(self, fp):
        assert struct.unpack(self.FMT_VERSION, fp.read(2)) == (0x02, 0x05)

        num_entries = struct.unpack('>I', fp.read(4))[0]
        for i in range(num_entries):
            entry_data = fp.read(0x16)
            assert len(entry_data) == 0x16

            entry = EntrySerializer.deserialize(entry_data)
            yield entry

        yield ColorSerializer.deserialize(fp.read())

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
