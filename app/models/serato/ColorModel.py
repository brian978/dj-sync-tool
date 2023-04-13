from app.models.serato.EntryModel import EntryModel


class ColorModel(EntryModel):
    FMT = '>4s'
    FIELDS = ('color', 'type')
