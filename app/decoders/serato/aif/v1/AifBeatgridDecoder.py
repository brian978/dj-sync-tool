from app.decoders.serato.mp3.v1.Mp3BeatgridDecoder import Mp3BeatgridDecoder

# noinspection PyPep8Naming
from mutagen import File as MutagenFile


class AifBeatgridDecoder(Mp3BeatgridDecoder):
    def _read_data_from_tags(self, filepath: str) -> bytes | None:
        tags = MutagenFile(filepath)
        if self.TAG_NAME in tags:
            tag_data = tags[self.TAG_NAME]
            return tag_data.data

        return None
