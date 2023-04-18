from app.models.MusicFile import MusicFile


class BaseWriterService:
    FMT_VERSION = 'BB'

    def __init__(self, copy_over_loops: bool = True):
        self._copy_over_loops = copy_over_loops  # When True, loops will also have a cue point if the slot is available

    def source_name(self):
        raise NotImplementedError("Source name method needs to be implemented!")

    def execute(self, file: MusicFile):
        raise NotImplementedError("Source name method needs to be implemented!")
