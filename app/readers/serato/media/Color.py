from . import Entry


class Color(Entry):
    FMT = '>4s'
    FIELDS = ('color',)
