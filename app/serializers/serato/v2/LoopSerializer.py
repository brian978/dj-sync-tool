from app.models.serato.v2.LoopModel import LoopModel
from app.serializers.serato.v2.CueSerializer import CueSerializer


class LoopSerializer(CueSerializer):
    MODEL = LoopModel
