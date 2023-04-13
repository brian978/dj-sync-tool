import base64
import struct

from app.decoders.serato.mp4.v2.Mp4Decoder import Mp4Decoder
from app.models.HotCue import HotCue
from app.models.HotCueType import HotCueType
from app.models.MusicFile import MusicFile
from app.models.serato.EntryModel import EntryModel
from app.models.serato.EntryType import EntryType
from app.models.serato.v2.BaseEntryModel import BaseEntryModel
from app.models.serato.v2.CueModel import CueModel
from app.models.serato.v2.LoopModel import LoopModel
from app.models.serato.v2.ColorModel import ColorModel
from app.models.serato.v2.BpmLockModel import BpmLockModel
from app.serializers.serato.v2.BpmLockSerializer import BpmLockSerializer
from app.serializers.serato.v2.ColorSerializer import ColorSerializer
from app.serializers.serato.v2.CueSerializer import CueSerializer
from app.serializers.serato.v2.LoopSerializer import LoopSerializer
from app.services.marker.BaseWriterService import BaseWriterService
from mutagen import id3
from mutagen import File as MutagenFile

from app.utils.serato import split_string


class MarkerWriterService(BaseWriterService):
    @classmethod
    def source_name(cls):
        return "GEOB:Serato Markers2"

    def execute(self, file: MusicFile):
        assert isinstance(file, MusicFile)

        entries = file.get_markers(self.source_name())

        self.write_hot_cues(file.hot_cues.copy(), entries)
        self.write_cue_loops(file.cue_loops.copy(), entries)

        # Simulating the behavior of Serato which keeps the entries in the order of the index
        entries = [
            self.__find_color_model(entries),
            *self.__find_storable_models(entries, CueModel),
            *self.__find_storable_models(entries, LoopModel),
            self.__find_bpm_lock_model(entries)
        ]

        self.__save(file, entries)

    @staticmethod
    def __find_storable_models(entries: list, model_type: type[BaseEntryModel]):
        sortable = []
        for entry in entries:
            if isinstance(entry, model_type) and entry.get_index() >= 0:
                sortable.append(entry)

        return sortable

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

            # Copy over the cue loop start to an empty hot cue (if any)
            if self._copy_over_loops and not self.__cue_exists(hot_cue.index, entries):
                # Create new entry
                entries.insert(at_index, CueModel.from_hot_cue(hot_cue))

            at_index += 1  # move to next position

    @staticmethod
    def add_padding(data: bytes):
        return data.ljust(752, b'A')

    def __write_tag(self, file: MusicFile, entries: list):
        if len(entries) == 0:
            return

        print(f"Dumping {self.source_name()} for file {file.location}")

        if file.location.lower().endswith(".m4a"):
            decoder = Mp4Decoder('----:com.serato.dj:markers')
            mutagen_file = decoder.encode(music_file=file, entries=entries)
            mutagen_file.tags.save(file.location)
        else:
            tagfile = MutagenFile(file.location)
            tagfile[self.source_name()] = id3.GEOB(
                encoding=0,
                mime='application/octet-stream',
                desc='Serato Markers2',
                data=data,
            )
            tagfile.save()

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

    def __dump(self, entries) -> bytes:
        if len(entries) == 0:
            return b'\x00'

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
                    struct.pack('>I', len(data)),
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
        data = data.ljust(470, b'\x00')

        return data

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

            entry.set_name(hot_cue.name)
            entry_found = True

        if not entry_found:
            # Create new entry
            entries.insert(at_index, model.from_hot_cue(hot_cue))
