from app.models.serato.PlainEntry import PlainEntry


class ColorEntry(PlainEntry):
    FMT = '>4s'
    FIELDS = ('color',)
