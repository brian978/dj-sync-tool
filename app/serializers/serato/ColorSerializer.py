from app.models.serato.ColorModel import ColorModel
from .EntrySerializer import EntrySerializer


class ColorSerializer(EntrySerializer):
    MODEL = ColorModel
