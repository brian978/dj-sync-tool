from app.models.MusicFile import MusicFile
from app.services.Service import Service


class BaseExtractorService(Service):
    FMT_VERSION = 'BB'

    def source_name(self):
        raise NotImplementedError("Source name method needs to be implemented!")

    def execute(self, file: MusicFile):
        raise NotImplementedError("Source name method needs to be implemented!")
