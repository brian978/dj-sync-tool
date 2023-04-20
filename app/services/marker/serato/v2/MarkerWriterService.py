from app.factories.serato.DecoderFactory import DecoderFactory
from app.models.HotCue import HotCue
from app.models.HotCueType import HotCueType
from app.models.MusicFile import MusicFile
from app.models.serato.EntryModel import EntryModel
from app.models.serato.EntryType import EntryType
from app.models.serato.v2.BaseEntryModel import BaseEntryModel
from app.models.serato.v2.BpmLockModel import BpmLockModel
from app.models.serato.v2.ColorModel import ColorModel
from app.models.serato.v2.CueModel import CueModel
from app.models.serato.v2.LoopModel import LoopModel
from app.serializers.serato.v2.BpmLockSerializer import BpmLockSerializer
from app.serializers.serato.v2.ColorSerializer import ColorSerializer
from app.serializers.serato.v2.CueSerializer import CueSerializer
from app.serializers.serato.v2.LoopSerializer import LoopSerializer
from app.services.BaseWriterService import BaseWriterService


class MarkerWriterService(BaseWriterService):
    @classmethod
    def source_name(cls):
        return "Markers_v2"

    def execute(self, file: MusicFile):
        assert isinstance(file, MusicFile)

        entries = file.get_tag_data(self.source_name())

        self.write_hot_cues(file.hot_cues.copy(), entries)
        self.write_cue_loops(file.cue_loops.copy(), entries)

        # Simulating the behavior of Serato which keeps the entries in the order of the index
        if len(entries):
            entries = [
                self.__find_color_model(entries),
                *self.__find_storable_models(entries, CueModel),
                *self.__find_storable_models(entries, LoopModel),
                self.__find_bpm_lock_model(entries)
            ]

        self.__save(file, list(filter(lambda item: item is not None, entries)))

    @staticmethod
    def __find_storable_models(entries: list, model_type: type[BaseEntryModel]):
        storable = []
        for entry in entries:
            if isinstance(entry, model_type) and entry.get_index() >= 0:
                storable.append(entry)

        return sorted(storable, key=lambda x: int(x.get('index')))

    @staticmethod
    def __find_color_model(entries: list):
        for entry in entries:
            if isinstance(entry, ColorModel):
                return entry

    @staticmethod
    def __find_bpm_lock_model(entries: list):
        for entry in entries:
            if isinstance(entry, BpmLockModel):
                return entry

    def write_hot_cues(self, hot_cues: list, entries: list) -> None:
        at_index = len(entries) - 1
        for hot_cue in hot_cues:
            assert isinstance(hot_cue, HotCue)
            if hot_cue.type != HotCueType.CUE:
                continue

            self.__write_cue_name(CueModel, hot_cue, entries, at_index)
            at_index += 1  # move to next position

    def write_cue_loops(self, hot_cues: list, entries: list) -> None:
        at_index = len(entries) - 1
        for hot_cue in hot_cues:
            assert isinstance(hot_cue, HotCue)
            if hot_cue.type != HotCueType.LOOP:
                continue

            self.__write_cue_name(LoopModel, hot_cue, entries, at_index)

            # # Copy over the cue loop start to an empty hot cue (if any)
            # if not self.__cue_exists(hot_cue.index, entries):
            #     # Create new entry
            #     entries.insert(at_index, CueModel.from_hot_cue(hot_cue))

            at_index += 1  # move to next position

    @staticmethod
    def add_padding(data: bytes):
        return data.ljust(752, b'A')

    def __write_tag(self, file: MusicFile, entries: list):
        if len(entries) == 0:
            return

        decoder = DecoderFactory.marker_decoder(file, 'v2')

        if decoder is None:
            return

        print(f"Dumping {self.source_name()} for file {file.location}")
        decoder.encode(music_file=file, entries=entries).save(file.location)

    def __save(self, file: MusicFile, entries: list):
        self.__write_tag(file, list(self.__serialize(entries)))

    @staticmethod
    def __serialize(entries: list):
        for entry_model in entries:
            assert isinstance(entry_model, EntryModel)
            match entry_model.model_type():
                case EntryType.CUE:
                    serializer = CueSerializer

                case EntryType.LOOP:
                    serializer = LoopSerializer

                case EntryType.COLOR:
                    serializer = ColorSerializer

                case EntryType.BPM_LOCK:
                    serializer = BpmLockSerializer

                case _:
                    print(f"Entry type {entry_model.model_type()} not supported and cannot be serialized (v2)!")
                    break

            yield serializer.serialize(entry_model)

    @staticmethod
    def __cue_exists(position: int, entries: list):
        for idx, entry in enumerate(entries):
            if not isinstance(entry, CueModel):
                continue

            if entry.get_index() == position:
                return True

        return False

    @staticmethod
    def __write_cue_name(model: type[BaseEntryModel], hot_cue: HotCue, entries: list, at_index: int):
        entry_found = False
        for entry in entries:
            if not isinstance(entry, model):
                continue

            idx = entry.get_index()
            if hot_cue.index != idx:
                continue

            entry_found = True
            entry.set_name(hot_cue.name)
            match hot_cue.type:
                case HotCueType.CUE:
                    entry.set_hot_cue(hot_cue.start, hot_cue.hex_color())

                case HotCueType.LOOP:
                    entry.set_cue_loop(hot_cue.start, hot_cue.end)

        if not entry_found:
            # Create new entry
            entries.insert(at_index, model.from_hot_cue(hot_cue))
