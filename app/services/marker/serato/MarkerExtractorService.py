import os
import struct

from app.decoders.serato.mp3.v1.Mp3Decoder import Mp3Decoder
from app.models.MusicFile import MusicFile
from app.models.serato.ColorModel import ColorModel
from app.models.serato.EntryModel import EntryModel
from app.models.serato.EntryType import EntryType
from app.serializers.serato.ColorSerializer import ColorSerializer
from app.serializers.serato.EntrySerializer import EntrySerializer
from app.services.marker.BaseExtractorService import BaseExtractorService
from app.utils.colors import rgb_to_hex
from app.decoders.serato.mp4.v1.Mp4Decoder import Mp4Decoder
from app.models.serato.EntryData import EntryData


class MarkerExtractorService(BaseExtractorService):
    @classmethod
    def source_name(cls):
        return "GEOB:Serato Markers_"

    @staticmethod
    def remove_padding(data: bytes):
        length = len(data)
        padding = -abs(1 - length % 4)

        return data[:padding]

    def execute(self, file: MusicFile):
        assert isinstance(file, MusicFile)

        filepath = file.location
        filename, file_extension = os.path.splitext(filepath)
        entries = []

        match file_extension:
            case '.m4a':
                decoder = Mp4Decoder('----:com.serato.dj:markers')
                data = decoder.decode(music_file=file)

            case '.mp3':
                decoder = Mp3Decoder("GEOB:Serato Markers_")
                data = decoder.decode(music_file=file)

            case _:
                print(f"Marker v1 extraction for extension {file_extension} is not yet supported! File: {filepath}")
                return entries

        if isinstance(data, list):
            entries = list(self.__deserialize(data))

        return entries

    @staticmethod
    def __deserialize(data: list):
        for entry_data in data:
            assert isinstance(entry_data, EntryData)
            match entry_data.data_type():
                case EntryType.CUE | EntryType.LOOP | EntryType.INVALID:
                    serializer = EntrySerializer
                case EntryType.COLOR:
                    serializer = ColorSerializer

                case _:
                    print(f"Entry type {entry_data.data_type()} not supported and cannot be deserialized!")
                    break

            yield serializer.deserialize(entry_data)

    def __parse(self, fp):
        assert struct.unpack(self.FMT_VERSION, fp.read(2)) == (0x02, 0x05)

        struct_len = 0x13

        len_bytes = fp.read(4)
        num_entries = struct.unpack('>I', len_bytes)[0]
        for i in range(num_entries):
            entry_data = fp.read(struct_len)
            length = len(entry_data)
            assert length == struct_len
            yield EntrySerializer.deserialize(entry_data)

        yield ColorSerializer.deserialize(fp.read())

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

        return entries

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
