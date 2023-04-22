import math

from app.factories.serato.DecoderFactory import DecoderFactory
from app.models.MusicFile import MusicFile
from app.models.Offset import Offset
from app.models.Tempo import Tempo
from app.models.serato.BpmMarkerModel import BpmMarkerModel
from app.services.BaseExtractorService import BaseExtractorService
from app.utils import finder
from app.utils.serato import calculate_bpm


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
            self.__calculate_bpm_values(data)
            self.__calculate_offsets(data, file)

        return data

    def __calculate_offsets(self, data: list[BpmMarkerModel], file: MusicFile):
        """
        For now, we assume that we only have fixed beat grids and not dynamic

        To calculate the correct offset we need to look for the closest cue or loop to Serato first beat
        """
        master_tempo = file.beatgrid[0]
        serato_tempo = data[0]

        self._logger().debug('')
        self._logger().debug(f'------------------------- START OFFSET / TID: {file.trackID} -------------------------')
        self._logger().debug(f'Calculating offset for file: {file.location}\n')

        # Debug beatgrid tempo markers
        serato_bpm_list = ', '.join(str(marker) for marker in data)
        self._logger().debug(f'{"Serato BPM markers:".rjust(22)} {serato_bpm_list}')

        master_bpm_list = ', '.join(str(marker) for marker in file.beatgrid)
        self._logger().debug(f'Rekordbox BPM markers: {master_bpm_list}')

        self.__log_hot_cues(file)
        self.__log_cue_loops(file)

        self._logger().debug(f'Rekordbox first bar: {master_tempo.get_position()}s')
        self._logger().debug(f'{"Serato start:".rjust(20)} {serato_tempo.get_position()}s')

        # Calculating the beat grids so we can have the offsets
        serato_beatgrid = self.__generate_beatgrid(file, serato_tempo)
        master_beatgrid = self.__generate_beatgrid(file, master_tempo)

        # Find and apply the offsets based on the bars
        offsets = self.__find_offsets(serato_beatgrid, master_beatgrid)
        file.apply_beatgrid_offsets(offsets)

        self.__log_hot_cues(file)
        self.__log_cue_loops(file)

        self._logger().debug('------------------------- END OFFSET / TID: {file.trackID} -------------------------')
        self._logger().debug('')

        return

    @staticmethod
    def __generate_beatgrid(file: MusicFile, tempo: Tempo):
        song_length = file.totalTime
        first_beat = tempo.get_position()
        beat_length = tempo.get_beat_length()

        # Calculate the start times of the first 20 beats in seconds
        num_beats = math.ceil(song_length / beat_length)
        return [first_beat + i * beat_length for i in range(num_beats)]

    def __find_offsets(self, serato_beatgrid: list, master_beatgrid: list) -> list[Offset]:
        offsets = []
        for beat in serato_beatgrid:
            closest_beat = finder.closest(beat, master_beatgrid)
            offset = Offset(closest_beat, beat)

            offsets.append(offset)

        list_offsets = '; '.join(set(str(f'{offset.get_value()}ms') for offset in offsets))
        self._logger().debug(f'{"Offsets:".rjust(20)} {list_offsets}')

        return offsets

    def __log_hot_cues(self, file: MusicFile):
        if len(file.hot_cues) == 0:
            return

        hot_cues = '\n'.join(str(cue) for cue in file.hot_cues)
        self._logger().debug(f'\nHot cues:\n{hot_cues}\n')

    def __log_cue_loops(self, file: MusicFile):
        if len(file.cue_loops) == 0:
            return

        cues = '\n'.join(str(cue) for cue in file.cue_loops)
        self._logger().debug(f'\nLoop cues:\n{cues}\n')

    @staticmethod
    def __calculate_bpm_values(data: list[BpmMarkerModel]):
        for idx, bpm_marker in enumerate(data):
            if bpm_marker.get_bpm() == 0:
                next_marker = data[idx + 1]
                bpm = calculate_bpm(bpm_marker, next_marker)
                bpm_marker.set_bpm(bpm)
