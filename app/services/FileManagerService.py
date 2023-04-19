from app.models.MusicFile import MusicFile
from app.readers.ReaderInterface import ReaderInterface
from app.services.BaseExtractorService import BaseExtractorService
from app.services.BaseWriterService import BaseWriterService


class FileManagerService:
    __extractors = []
    __writers = []

    def __init__(self, reader: ReaderInterface):
        self.__reader = reader

    def add_extractor(self, extractor: BaseExtractorService):
        self.__extractors.append(extractor)

    def add_writer(self, writer: BaseWriterService):
        self.__writers.append(writer)

    def find_all(self):
        files = self.__reader.read()
        for file in files:
            assert isinstance(file, MusicFile)

            # extract tags from the files
            for extractor in self.__extractors:
                assert isinstance(extractor, BaseExtractorService)
                file.add_tag_data(extractor.source_name(), extractor.execute(file))

        return files

    def write_tags(self, files: list):
        for file in files:
            assert isinstance(file, MusicFile)
            for writer in self.__writers:
                assert isinstance(writer, BaseWriterService)
                writer.execute(file)

