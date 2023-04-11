import base64
import io
import struct

import mutagen

from app.models.MusicFile import MusicFile
from app.services.marker.BaseExtractorService import BaseExtractorService
from app.utils.serato import read_bytes
from app.utils.serato.type_detector import detect_type


class MarkerExtractorService(BaseExtractorService):
    @classmethod
    def source_name(cls):
        return "GEOB:Serato Markers2"

    def execute(self, file: MusicFile):
        assert isinstance(file, MusicFile)

        raw_file = file.location
        tagfile = mutagen.File(raw_file)
        if tagfile is not None:
            try:
                data = tagfile[self.source_name()].data
            except KeyError:
                print('File is missing "GEOB:Serato Markers2" tag')
                return 1
        else:
            with open(raw_file, mode='rb') as fp:
                data = fp.read()

        return list(self.__parse(data))

    def __parse(self, data: list):
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
