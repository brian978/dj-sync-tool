from app.models.serato.v2.CueModel import CueModel
from app.serializers.serato.EntrySerializer import EntrySerializer


class CueSerializer(EntrySerializer):
    MODEL = CueModel
