from app.models.serato.ColorEntry import ColorEntry
from .Entry import Entry


class Color(Entry):
    FMT = '>4s'
    FIELDS = ('color',)
    MODEL = ColorEntry
