import struct

from app.models.HotCue import HotCue
from app.models.HotCueType import HotCueType
from app.models.MusicFile import MusicFile
from app.models.serato.ColorModel import ColorModel
from app.models.serato.EntryModel import EntryModel
from app.models.serato.EntryType import EntryType
from app.readers.ReaderInterface import ReaderInterface
from app.readers.serato.GEOBReader import GEOBReader
from app.utils.colors import rgb_to_hex
from mutagen import id3
from mutagen import File as MutagenFile


class GEOBWriter:
    __entries = []

    def __init__(self, reader: ReaderInterface):
        self.__reader = reader

    def create_entries(self):
        files = self.__reader.read()
        entries = self.__get_entries(files)

        if len(entries) == 0:
            self.__create_empty_entries()

        for file in files:
            assert isinstance(file, MusicFile)

            self.write_hot_cues(file.hot_cues, entries)
            self.write_cue_loops(file.hot_cues, entries)
            self.__entries.append({"file": file, "entries": entries})

    def export(self):
        for obj in self.__entries:
            file = obj["file"]
            entries = obj["entries"]

            tagfile = MutagenFile(file.location)
            data = self.dump(entries)

            if tagfile is not None:
                tagfile['GEOB:Serato Markers_'] = id3.GEOB(
                    encoding=0,
                    mime='application/octet-stream',
                    desc='Serato Markers_',
                    data=data,
                )
                tagfile.save()
            else:
                with open(file.location, mode='wb') as fp:
                    fp.write(data)

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

    @staticmethod
    def dump(entries):
        data = struct.pack(GEOBReader.FMT_VERSION, 0x02, 0x05)
        num_entries = len(entries) - 1
        data += struct.pack('>I', num_entries)
        for entry_data in entries:
            data += entry_data.dump()

        return data

    @staticmethod
    def __get_entries(files: list):
        return GEOBReader(files).read()

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

            entry.set_cue_loop(
                hot_cue.start,
                hot_cue.end
            )
