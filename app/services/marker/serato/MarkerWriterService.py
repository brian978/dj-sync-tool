from app.factories.serato.DecoderFactory import DecoderFactory
from app.models.HotCue import HotCue
from app.models.HotCueType import HotCueType
from app.models.MusicFile import MusicFile
from app.models.serato.ColorModel import ColorModel
from app.models.serato.EntryModel import EntryModel
from app.models.serato.EntryType import EntryType
from app.serializers.serato.ColorSerializer import ColorSerializer
from app.serializers.serato.EntrySerializer import EntrySerializer
from app.services.BaseWriterService import BaseWriterService
from app.utils.env import env


class MarkerWriterService(BaseWriterService):
    def source_name(self):
        return "Markers_v1"

    def execute(self, file: MusicFile):
        assert isinstance(file, MusicFile)

        entries = file.get_tag_data(self.source_name())

        if len(entries) == 0:
            """
            Serato always creates all v1 entries, so if we have none we need to create them as empty
            """
            entries = self._create_empty_entries()

        self._write_hot_cues(file.hot_cues.copy(), entries)
        self._write_cue_loops(file.cue_loops.copy(), entries)
        self.__save(file, entries)

    @staticmethod
    def _write_hot_cues(hot_cues: list, entries: list[EntryModel]) -> None:
        """
        We need to update the hot cues for the first 5 Entries (0 to 4)
        """
        for idx, entry in enumerate(entries):
            if entry.model_type() not in [EntryType.CUE, EntryType.INVALID]:
                continue

            if idx > 4:
                break

            if not entry.is_writable():
                continue

            for hot_cue in hot_cues:
                assert isinstance(hot_cue, HotCue)
                if hot_cue.index != idx or hot_cue.type != HotCueType.CUE:
                    continue

                entry.set_hot_cue(hot_cue.start, hot_cue.hex_color())

    def _write_cue_loops(self, cue_loops: list, entries: list[EntryModel]) -> None:
        """
        Loops will be created on the next 5 (05 - 13)
        """
        cue_loops = sorted(cue_loops, key=lambda x: int(x.index))
        for idx, entry in enumerate(entries):
            if entry.model_type() not in [EntryType.LOOP, EntryType.INVALID]:
                continue

            if len(cue_loops) == 0:
                break

            if idx < 5 or idx > 14:
                continue

            if not entry.is_writable():
                continue

            offset_idx = idx - 5
            for hot_cue in cue_loops:
                assert isinstance(hot_cue, HotCue)
                if hot_cue.index != offset_idx or hot_cue.type != HotCueType.LOOP:
                    continue

                entry.set_cue_loop(hot_cue.start, hot_cue.end)

                # Copy over the cue loop start to an empty hot cue (if any)
                if env('WRITE_LOOPS_AS_CUES') is True:
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
        decoder = DecoderFactory.marker_decoder(file, 'v1')

        if decoder is None:
            return

        self._logger().debug(f"Dumping {self.source_name()} for file {file.location}")
        decoder.encode(music_file=file, entries=entries).save(file.location)

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

    @staticmethod
    def _create_empty_cue_entry(entry_type: EntryType):
        return EntryModel(*[
            False,
            None,
            False,
            None,
            b'\x00\x7f\x7f\x7f\x7f\x7f',
            b'\x00\x00\x00',
            entry_type,
            False
        ])

    @staticmethod
    def _create_empty_color_entry():
        return ColorModel(*[
            b'\xff\xff\xff',
            EntryType.COLOR
        ])

    def _create_empty_entries(self):
        entries = []

        for i in range(14):
            if i <= 4:
                entry_type = EntryType.CUE
            else:
                entry_type = EntryType.LOOP

            entries.append(self._create_empty_cue_entry(entry_type))

        entries.append(self._create_empty_color_entry())

        return entries
