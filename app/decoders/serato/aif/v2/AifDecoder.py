# noinspection PyPep8Naming
from mutagen import File as MutagenFile

from app.decoders.serato.mp3.v2.Mp3Decoder import Mp3Decoder


class AifDecoder(Mp3Decoder):
    def _read_data_from_tags(self, filepath: str) -> bytes | None:
        tags = MutagenFile(filepath)
        if self.TAG_NAME in tags:
            tag_data = tags[self.TAG_NAME]
            return tag_data.data

        return None
