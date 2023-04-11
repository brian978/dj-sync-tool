from app.models.serato.ColorModel import ColorModel
from .Entry import Entry


class Color(Entry):
    FMT = '>4s'
    FIELDS = ('color',)
    MODEL = ColorModel
