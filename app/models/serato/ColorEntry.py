from app.models.serato.Entry import Entry


class ColorEntry(Entry):
    FMT = '>4s'
    FIELDS = ('color',)
