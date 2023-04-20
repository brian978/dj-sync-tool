import os
from importlib import import_module

from app.decoders.serato.BaseDecoder import BaseDecoder
from app.models.MusicFile import MusicFile


class DecoderFactory:
    __NAMESPACE = 'app.decoders.serato'

    @classmethod
    def __file_extension(cls, file: MusicFile):
        filepath = file.location
        filename, file_extension = os.path.splitext(filepath)

        return file_extension

    @classmethod
    def marker_decoder(cls, file: MusicFile, version: str) -> BaseDecoder:
        match cls.__file_extension(file):
            case '.m4a':
                return import_module(f'{cls.__NAMESPACE}.mp4.{version}.Mp4Decoder').Mp4Decoder()

            case '.mp3':
                return import_module(f'{cls.__NAMESPACE}.mp3.{version}.Mp3Decoder').Mp3Decoder()

            case '.aif' | '.aiff':
                return import_module(f'{cls.__NAMESPACE}.aif.{version}.AifDecoder').AifDecoder()

    @classmethod
    def beatgrid_decoder(cls, file: MusicFile, version: str):
        match cls.__file_extension(file):
            case '.m4a':
                return import_module(f'{cls.__NAMESPACE}.mp4.{version}.Mp4BeatgridDecoder').Mp4BeatgridDecoder()

            case '.mp3':
                return import_module(f'{cls.__NAMESPACE}.mp3.{version}.Mp3BeatgridDecoder').Mp3BeatgridDecoder()

            case '.aif' | '.aiff':
                return import_module(f'{cls.__NAMESPACE}.aif.{version}.AifBeatgridDecoder').AifBeatgridDecoder()
