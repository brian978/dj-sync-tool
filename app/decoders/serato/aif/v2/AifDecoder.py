# noinspection PyPep8Naming
from mutagen import File as MutagenFile, id3

from app.decoders.serato.mp3.v2.Mp3Decoder import Mp3Decoder
from app.models.MusicFile import MusicFile


class AifDecoder(Mp3Decoder):
    def _read_data_from_tags(self, filepath: str) -> bytes | None:
        tags = MutagenFile(filepath)
        if self.TAG_NAME in tags:
            tag_data = tags[self.TAG_NAME]
            return tag_data.data

        return None

    def _write_data_to_tags(self, music_file: MusicFile, payload: bytes):
        mutagen_file = MutagenFile(music_file.location)
        mutagen_file[self.TAG_NAME] = id3.GEOB(
            encoding=0,
            mime='application/octet-stream',
            desc=self.MARKERS_NAME,
            data=payload,
        )

        return mutagen_file
