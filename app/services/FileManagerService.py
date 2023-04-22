from progress.bar import Bar

from app.models.MusicFile import MusicFile
from app.readers.BaseReader import BaseReader
from app.services.BaseExtractorService import BaseExtractorService
from app.services.BaseWriterService import BaseWriterService
from app.services.Service import Service


class FileManagerService(Service):
    __extractors = []
    __writers = []

    def __init__(self, reader: BaseReader):
        self.__reader = reader

    def add_extractor(self, extractor: BaseExtractorService):
        self.__extractors.append(extractor)

    def add_writer(self, writer: BaseWriterService):
        self.__writers.append(writer)

    def extract_tags(self):
        files = self.__reader.read()
        with Bar('Reading tags', max=len(files)) as bar:
            for file in files:
                assert isinstance(file, MusicFile)
                bar.next()

                # extract tags from the files
                for extractor in self.__extractors:
                    assert isinstance(extractor, BaseExtractorService)
                    file.add_tag_data(extractor.source_name(), extractor.execute(file))

        return files

    def write_tags(self, files: list):
        with Bar('Writing tags', max=len(files)) as bar:
            for file in files:
                assert isinstance(file, MusicFile)
                bar.next()

                self._logger().info(f'Writing tags for file: {file.filename()}')
                for writer in self.__writers:
                    assert isinstance(writer, BaseWriterService)
                    writer.execute(file)
