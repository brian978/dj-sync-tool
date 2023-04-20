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

        data = decoder.decode(file)

        if len(data):
            self.__calculate_offsets(data, file)

        return data

    @staticmethod
    def __calculate_offsets(data: list, file: MusicFile):
        """
        For now we assume that we only have fixed beat grids and not dynamic
        """
        master_start = float(file.beatgrid[0].position)
        serato_start = round(data[0].position, 3)
        offset = int(round(serato_start - master_start, 3) * 1000)

        file.offset = offset
        file.apply_beatgrid_offset(offset)

        return
