import math

from app.factories.serato.DecoderFactory import DecoderFactory
from app.models.MusicFile import MusicFile
from app.services.BaseExtractorService import BaseExtractorService
from app.utils import finder


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

    def __calculate_offsets(self, data: list, file: MusicFile):
        """
        For now, we assume that we only have fixed beat grids and not dynamic

        To calculate the correct offset we need to look for the closest cue or loop to Serato first beat
        """
        serato_start = data[0].position
        master_start = self.__calculate_bars(file, serato_start)
        offset = int(round(serato_start - master_start, 3) * 1000)

        file.offset = offset
        file.apply_beatgrid_offset(offset)

        return

    @staticmethod
    def __calculate_bars(file: MusicFile, position: int):
        song_length = float(file.totalTime)  # Length of song in seconds
        bpm = float(file.averageBpm)  # Tempo of song in beats per minute
        first_beat = float(file.beatgrid[0].position)  # Location of first beat in seconds

        # Calculate the length of each beat in seconds
        beat_length = 60 / bpm

        # Calculate the start times of the first 20 beats in seconds
        num_beats = math.ceil(song_length / beat_length)
        beat_starts = [first_beat + i * beat_length for i in range(num_beats)]

        return finder.closest(position, beat_starts)
