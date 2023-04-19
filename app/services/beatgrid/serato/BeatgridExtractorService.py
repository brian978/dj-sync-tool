import os

from app.models.MusicFile import MusicFile
from app.services.BaseExtractorService import BaseExtractorService


class BeatgridExtractorService(BaseExtractorService):
    @classmethod
    def source_name(cls):
        return "Beatgrid"

    def execute(self, file: MusicFile):
        assert isinstance(file, MusicFile)

        filepath = file.location
        filename, file_extension = os.path.splitext(filepath)

        match file_extension:
            case '.m4a':
                decoder = Mp4Decoder()
                data = decoder.decode(music_file=file)

            case '.mp3':
                decoder = Mp3Decoder()
                data = decoder.decode(music_file=file)

            case _:
                print(f"Marker v1 extraction for extension {file_extension} is not yet supported! File: {filepath}")
                return entries
