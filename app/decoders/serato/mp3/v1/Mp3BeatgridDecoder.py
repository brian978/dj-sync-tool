from app.decoders.serato.BaseDecoder import BaseDecoder
from app.models.MusicFile import MusicFile

# noinspection PyPep8Naming
from mutagen.mp3 import MP3 as MutagenFile


class Mp3BeatgridDecoder(BaseDecoder):
    def decode(self, music_file: MusicFile) -> list:
        raise NotImplementedError('The decode method of the decoder must be implemented!')

    def encode(self, music_file: MusicFile, entries: list) -> MutagenFile:
        raise NotImplementedError('The encode method of the decoder must be implemented!')
