from app.models.serato.EntryModel import EntryModel


class BaseEntryModel(EntryModel):
    def set_hot_cue(self, position: int, color: str):
        raise NotImplementedError("The V2 markers do not support `set_hot_cue`")

    def set_cue_loop(self, position_start: int, position_end: int):
        raise NotImplementedError("The V2 markers do not support `set_cue_loop`")

    def set_name(self, name: str):
        raise NotImplementedError("The `set_name` is not supported by all models")

    def get_index(self):
        return int(getattr(self, "index", -99))

    def get_name(self):
        return getattr(self, "name")
