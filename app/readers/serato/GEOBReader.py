import io
import struct

import mutagen

from app.models.MusicFile import MusicFile
from app.readers.ReaderInterface import ReaderInterface
from app.serializers.serato.ColorSerializer import ColorSerializer
from app.serializers.serato.EntrySerializer import EntrySerializer


class GEOBReader(ReaderInterface):
    FMT_VERSION = 'BB'

    def __init__(self, files):
        self.__files = files

    def read(self):
        entries = []
        for file in self.__files:
            assert isinstance(file, MusicFile)

            raw_file = file.location
            tagfile = mutagen.File(raw_file)

            if tagfile is not None:
                try:
                    data = tagfile['GEOB:Serato Markers_'].data
                except KeyError:
                    print('File is missing "GEOB:Serato Markers_" tag')
                    return 1
            else:
                with open(raw_file, mode='rb') as fp:
                    data = fp.read()

            entries = list(self.__parse(io.BytesIO(data)))

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
