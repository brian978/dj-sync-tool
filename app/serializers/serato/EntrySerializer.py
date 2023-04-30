from app.models.serato.AbstractModel import AbstractModel
from app.models.serato.EntryData import EntryData
from app.models.serato.EntryModel import EntryModel
from app.models.serato.EntryType import EntryType


class EntrySerializer(object):
    MODEL = EntryModel

    @classmethod
    def deserialize(cls, entry: EntryData):
        model = cls.MODEL

        payload = []
        for field in model.FIELDS:
            value = entry.get(field)
            if field == 'type':
                value = EntryType(value)

            payload.append(value)

        return model(*payload)

    @classmethod
    def serialize(cls, model: AbstractModel):
        entry = EntryData(model.model_type())

        for field in model.FIELDS:
            value = model.get(field)
            if field == 'type':
                continue

            entry.set(field, value)

        return entry
