from app.models.serato.AbstractModel import AbstractModel


class BaseEntryModel(AbstractModel):
    def set_hot_cue(self, position: int, color: str):
        raise NotImplementedError("The V2 markers do not support `set_hot_cue`")

    def set_cue_loop(self, position_start: int, position_end: int):
        raise NotImplementedError("The V2 markers do not support `set_cue_loop`")

    def set_name(self, name: str):
        pass

    def get_index(self):
        return int(getattr(self, "index", -99))

    def get_name(self):
        return getattr(self, "name")
