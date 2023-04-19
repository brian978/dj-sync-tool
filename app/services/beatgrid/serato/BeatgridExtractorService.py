import os

from app.factories.serato.DecoderFactory import DecoderFactory
from app.models.MusicFile import MusicFile
from app.services.BaseExtractorService import BaseExtractorService


class BeatgridExtractorService(BaseExtractorService):
    @classmethod
    def source_name(cls):
        return "Beatgrid"

    def execute(self, file: MusicFile):
        assert isinstance(file, MusicFile)

        decoder = DecoderFactory.beatgrid_decoder(file, 'v1')

        if decoder is None:
            return []

        return decoder.decode(file)
