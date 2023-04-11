from app.models.serato.ColorEntry import ColorEntry as ColorModel
from .Entry import Entry


class Color(Entry):
    FMT = '>4s'
    FIELDS = ('color',)

    @classmethod
    def model(cls):
        return ColorModel
