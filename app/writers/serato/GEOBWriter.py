import struct

import mutagen

from app.models.MusicFile import MusicFile
from app.readers.serato.GEOBReader import GEOBReader


class GEOBWriter:
    def export(self, file: MusicFile, entries: list):
        tagfile = mutagen.File(file.location)
        data = self.dump(entries)

        if tagfile is not None:
            tagfile['GEOB:Serato Markers_'] = mutagen.id3.GEOB(
                encoding=0,
                mime='application/octet-stream',
                desc='Serato Markers_',
                data=data,
            )
            tagfile.save()
        else:
            with open(file.location, mode='wb') as fp:
                fp.write(data)

    @staticmethod
    def dump(entries):
        data = struct.pack(GEOBReader.FMT_VERSION, 0x02, 0x05)
        num_entries = len(entries) - 1
        data += struct.pack('>I', num_entries)
        for entry_data in entries:
            data += entry_data.dump()

        return data
