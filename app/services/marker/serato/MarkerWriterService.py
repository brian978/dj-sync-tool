import struct

from app.decoders.serato.mp3.v1.Mp3Decoder import Mp3Decoder
from app.decoders.serato.mp4.v1.Mp4Decoder import Mp4Decoder
from app.models.HotCue import HotCue
from app.models.HotCueType import HotCueType
from app.models.MusicFile import MusicFile
from app.models.serato.EntryModel import EntryModel
from app.models.serato.EntryType import EntryType
from app.serializers.serato.ColorSerializer import ColorSerializer
from app.serializers.serato.EntrySerializer import EntrySerializer
from app.services.marker.BaseWriterService import BaseWriterService


class MarkerWriterService(BaseWriterService):
    def source_name(self):
        return "GEOB:Serato Markers_"

    def execute(self, file: MusicFile):
        assert isinstance(file, MusicFile)

        entries = file.get_markers(self.source_name())

        self.write_hot_cues(file.hot_cues.copy(), entries)
        self.write_cue_loops(file.cue_loops.copy(), entries)
        self.__save(file, entries)

    @staticmethod
    def write_hot_cues(hot_cues: list, entries: list) -> None:
        """
        We need to update the hot cues for the first 5 Entries (0 to 4)
        """
        for idx, entry in enumerate(entries):
            assert isinstance(entry, EntryModel)
            if idx > 4:
                break

            for hot_cue in hot_cues:
                assert isinstance(hot_cue, HotCue)
                if hot_cue.index != idx or hot_cue.type != HotCueType.CUE:
                    continue

                entry.set_hot_cue(hot_cue.start, hot_cue.hex_color())

    def write_cue_loops(self, cue_loops: list, entries: list) -> None:
        """
        Loops will be created on the next 5 (05 - 13)
        """
        for idx, entry in enumerate(entries):
            if len(cue_loops) == 0:
                break

            if idx < 5 or idx > 14:
                continue

            hot_cue = cue_loops.pop(0)
            assert isinstance(hot_cue, HotCue)
            if hot_cue.type != HotCueType.LOOP:
                continue

            entry.set_cue_loop(hot_cue.start, hot_cue.end)

            # Copy over the cue loop start to an empty hot cue (if any)
            if self._copy_over_loops:
                empty_cue_entry = self.__find_empty_hot_cue(hot_cue.index, entries)
                if empty_cue_entry is not None:
                    empty_cue_entry.set_hot_cue(hot_cue.start, hot_cue.hex_color())

    @staticmethod
    def __find_empty_hot_cue(position: int, entries: list):
        for idx, entry in enumerate(entries):
            if idx > 4:
                break

            if idx == position and entry.is_empty():
                return entry

    def __write_tag(self, file: MusicFile, entries: list):
        print(f"Dumping {self.source_name()} for file {file.location}")
        if file.location.lower().endswith(".m4a"):
            decoder = Mp4Decoder('----:com.serato.dj:markers')
            mutagen_file = decoder.encode(music_file=file, entries=entries).tags
        else:
            decoder = Mp3Decoder("GEOB:Serato Markers_")
            mutagen_file = decoder.encode(music_file=file, entries=entries)

        mutagen_file.save(file.location)

    def __save(self, file: MusicFile, entries: list):
        self.__write_tag(file, list(self.__serialize(entries)))

    @staticmethod
    def __serialize(entries: list):
        for entry_model in entries:
            assert isinstance(entry_model, EntryModel)
            match entry_model.model_type():
                case EntryType.COLOR:
                    serializer = ColorSerializer

                case _:
                    serializer = EntrySerializer

            yield serializer.serialize(entry_model)

    def __dump(self, entries) -> bytes:
        data = struct.pack(self.FMT_VERSION, 0x02, 0x05)
        num_entries = len(entries) - 1
        data += struct.pack('>I', num_entries)
        for entry_data in entries:
            data += entry_data.dump()

        return data
