from mutagen import FileType as MutagenFile

from app.models.MusicFile import MusicFile


class BaseDecoder:
    """
    Each entry data looks something like (it's the same for CUE & LOOP):

    """
    FMT_VERSION = 'BB'

    def decode(self, music_file: MusicFile) -> list:
        raise NotImplementedError('The decode method of the decoder must be implemented!')

    def encode(self, music_file: MusicFile, entries: list) -> MutagenFile:
        raise NotImplementedError('The encode method of the decoder must be implemented!')
