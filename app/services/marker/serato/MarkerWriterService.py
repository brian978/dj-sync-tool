import struct

from app.models.HotCue import HotCue
from app.models.HotCueType import HotCueType
from app.models.MusicFile import MusicFile
from app.services.marker.BaseWriterService import BaseWriterService
from app.utils.colors import rgb_to_hex
from mutagen import id3
from mutagen import File as MutagenFile


class MarkerWriterService(BaseWriterService):
    def source_name(self):
        return "GEOB:Serato Markers_"

    def execute(self, file: MusicFile):
        assert isinstance(file, MusicFile)

        entries = file.get_markers(self.source_name())

        self.write_hot_cues(file.hot_cues.copy(), entries)
        self.write_cue_loops(file.hot_cues.copy(), entries)
        self.__save(file, entries)

    @staticmethod
    def write_hot_cues(hot_cues: list, entries: list) -> None:
        """
        We need to create hot cues for the first 5 Entries (0 to 4)
        """
        for idx, entry in enumerate(entries):
            if idx > 4:
                break

            for hot_cue in hot_cues:
                assert isinstance(hot_cue, HotCue)
                if hot_cue.index != idx or hot_cue.type != HotCueType.CUE:
                    continue

                entry.set_hot_cue(
                    hot_cue.start,
                    rgb_to_hex(hot_cue.color[0], hot_cue.color[1], hot_cue.color[2])
                )

    @staticmethod
    def write_cue_loops(hot_cues: list, entries: list) -> None:
        """
        Loops will be created on the next 5 (05 - 13)
        """
        for idx, entry in enumerate(entries):
            if len(hot_cues) == 0:
                break

            if idx < 5 or idx > 14:
                continue

            hot_cue = hot_cues.pop(0)
            assert isinstance(hot_cue, HotCue)
            if hot_cue.type != HotCueType.LOOP:
                continue

            entry.lock()
            entry.set_cue_loop(
                hot_cue.start,
                hot_cue.end
            )

    def __save(self, file: MusicFile, entries: list):
        tagfile = MutagenFile(file.location)
        data = self.__dump(entries)

        print(f"Dumping {self.source_name()} for file {file.location}")

        if tagfile is not None:
            tagfile[self.source_name()] = id3.GEOB(
                encoding=0,
                mime='application/octet-stream',
                desc='Serato Markers_',
                data=data,
            )
            tagfile.save()
        else:
            with open(file.location, mode='wb') as fp:
                fp.write(data)

    def __dump(self, entries):
        data = struct.pack(self.FMT_VERSION, 0x02, 0x05)
        num_entries = len(entries) - 1
        data += struct.pack('>I', num_entries)
        for entry_data in entries:
            data += entry_data.dump()

        return data
