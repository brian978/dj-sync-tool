import base64
import io
import os
import struct

from app.decoders.serato.mp3.v2.Mp3Decoder import Mp3Decoder
from app.decoders.serato.mp4.v2.Mp4Decoder import Mp4Decoder
from app.models.MusicFile import MusicFile
from app.models.serato.EntryData import EntryData
from app.models.serato.EntryType import EntryType
from app.serializers.serato.v2.BpmLockSerializer import BpmLockSerializer
from app.serializers.serato.v2.ColorSerializer import ColorSerializer
from app.serializers.serato.v2.CueSerializer import CueSerializer
from app.serializers.serato.v2.LoopSerializer import LoopSerializer
from app.services.marker.BaseExtractorService import BaseExtractorService
from app.utils.serato import read_bytes
from app.utils.serato.type_detector import detect_type


class MarkerExtractorService(BaseExtractorService):
    @classmethod
    def source_name(cls):
        return "GEOB:Serato Markers2"

    @staticmethod
    def remove_padding(data: bytes):
        length = len(data)
        padding = -abs(2 - length % 4)

        return data[:padding]

    def execute(self, file: MusicFile):
        assert isinstance(file, MusicFile)

        filepath = file.location
        filename, file_extension = os.path.splitext(filepath)
        entries = []

        match file_extension:
            case '.m4a':
                decoder = Mp4Decoder('----:com.serato.dj:markersv2')
                data = decoder.decode(music_file=file)

            case '.mp3':
                decoder = Mp3Decoder("GEOB:Serato Markers2")
                data = decoder.decode(music_file=file)

            case _:
                raise TypeError(f"Extension {file_extension} is invalid!")

        if isinstance(data, list):
            entries = list(self.__deserialize(data))

        return entries

    @staticmethod
    def __deserialize(data: list):
        for entry_data in data:
            assert isinstance(entry_data, EntryData)
            match entry_data.data_type():
                case EntryType.CUE:
                    serializer = CueSerializer

                case EntryType.LOOP:
                    serializer = LoopSerializer

                case EntryType.COLOR:
                    serializer = ColorSerializer

                case EntryType.BPM_LOCK:
                    serializer = BpmLockSerializer

                case _:
                    print(f"Entry type {entry_data.data_type()} not supported and cannot be deserialized (v2)!")
                    break

            yield serializer.deserialize(entry_data)

    def __parse(self, data: bytes):
        version_len = struct.calcsize(self.FMT_VERSION)
        version = struct.unpack(self.FMT_VERSION, data[:version_len])
        assert version == (0x01, 0x01)

        b64data = data[version_len:data.index(b'\x00', version_len)].replace(b'\n', b'')
        padding = b'A==' if len(b64data) % 4 == 1 else (b'=' * (-len(b64data) % 4))
        payload = base64.b64decode(b64data + padding)
        fp = io.BytesIO(payload)
        assert struct.unpack(self.FMT_VERSION, fp.read(2)) == (0x01, 0x01)
        while True:
            entry_name = b''.join(read_bytes(fp)).decode('utf-8')
            if not entry_name:
                break

            entry_len = struct.unpack('>I', fp.read(4))[0]
            assert entry_len > 0

            yield detect_type(entry_name).deserialize(fp.read(entry_len))
