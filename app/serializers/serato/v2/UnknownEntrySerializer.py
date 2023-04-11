from app.models.serato.v2.UnknownModel import UnknownModel
from app.serializers.serato.EntrySerializer import EntrySerializer


class UnknownEntrySerializer(EntrySerializer):
    NAME = None
    FIELDS = ('data',)
    MODEL = UnknownModel
