from app.models.serato.v2.ColorModel import ColorModel
from app.serializers.serato.EntrySerializer import EntrySerializer


class ColorSerializer(EntrySerializer):
    MODEL = ColorModel
