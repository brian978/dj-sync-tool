import base64
import struct

from app.models.HotCue import HotCue
from app.models.HotCueType import HotCueType
from app.models.MusicFile import MusicFile
from app.models.serato.v2.CueModel import CueModel
from app.services.marker.BaseWriterService import BaseWriterService
from mutagen import id3
from mutagen import File as MutagenFile

from app.utils.colors import rgb_to_hex


class MarkerWriterService(BaseWriterService):
    @classmethod
    def source_name(cls):
        return "GEOB:Serato Markers2"

    def execute(self, file: MusicFile):
        assert isinstance(file, MusicFile)

        entries = file.get_markers(self.source_name())

        self.write_hot_cues(file.hot_cues.copy(), entries)
        self.__save(file, entries)

    @staticmethod
    def write_hot_cues(hot_cues: list, entries: list) -> None:
        """
        We need to create hot cues for the first 5 Entries (0 to 4)
        """
        for hot_cue in hot_cues:
            assert isinstance(hot_cue, HotCue)
            if hot_cue.type != HotCueType.CUE:
                continue

            entry_found = False
            for entry in entries:
                if not isinstance(entry, CueModel):
                    continue

                idx = entry.get_index()
                if hot_cue.index != idx:
                    continue

                entry.set_name(hot_cue.name)
                entry_found = True

            if not entry_found:
                # Create new entry
                entries.append(CueModel.from_hot_cue(hot_cue))

    def __save(self, file: MusicFile, entries: list):
        tagfile = MutagenFile(file.location)
        data = self.__dump(entries)

        if tagfile is not None:
            tagfile[self.source_name()] = id3.GEOB(
                encoding=0,
                mime='application/octet-stream',
                desc='Serato Markers2',
                data=data
            )
            tagfile.save()
        else:
            with open(file.location, mode='wb') as fp:
                fp.write(data)

    def __dump(self, entries):
        version = struct.pack(self.FMT_VERSION, 0x01, 0x01)

        contents = [version]
        for entry in entries:
            if entry.NAME is None:
                contents.append(entry.dump())
            else:
                data = entry.dump()
                contents.append(b''.join((
                    entry.NAME.encode('utf-8'),
                    b'\x00',
                    struct.pack('>I', (len(data))),
                    data,
                )))

        payload = b''.join(contents)
        payload_base64 = bytearray(base64.b64encode(payload).replace(b'=', b'A'))

        i = 72
        while i < len(payload_base64):
            payload_base64.insert(i, 0x0A)
            i += 73

        data = version
        data += payload_base64
        return data.ljust(470, b'\x00')
