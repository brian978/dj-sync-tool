import importlib
import os

from app.decoders.serato.BaseDecoder import BaseDecoder
from app.models.MusicFile import MusicFile


class DecoderFactory:
    @classmethod
    def __file_extension(cls, file: MusicFile):
        filepath = file.location
        filename, file_extension = os.path.splitext(filepath)

        return file_extension

    @classmethod
    def marker_decoder(cls, file: MusicFile, version: str) -> BaseDecoder:
        match cls.__file_extension(file):
            case '.m4a':
                return importlib.import_module(f'app.decoders.serato.mp4.{version}.Mp4Decoder').Mp4Decoder()

            case '.mp3':
                return importlib.import_module(f'app.decoders.serato.mp3.{version}.Mp3Decoder').Mp3Decoder()
