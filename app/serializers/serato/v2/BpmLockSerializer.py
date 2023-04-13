from app.models.serato.v2.BpmLockModel import BpmLockModel
from app.serializers.serato.EntrySerializer import EntrySerializer


class BpmLockSerializer(EntrySerializer):
    MODEL = BpmLockModel
