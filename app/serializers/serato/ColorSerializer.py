from app.models.serato.ColorModel import ColorModel
from .EntrySerializer import EntrySerializer


class ColorSerializer(EntrySerializer):
    FMT = '>4s'
    FIELDS = ('color',)
    MODEL = ColorModel
