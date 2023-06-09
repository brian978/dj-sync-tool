from app.models.serato.v2.BaseEntryModel import BaseEntryModel


class FlipModel(BaseEntryModel):
    NAME = 'FLIP'
    FMT1 = 'cB?'
    FMT2 = '>BI'
    FMT3 = '>BI16s'
    FIELDS = ('field1', 'index', 'enabled', 'name', 'loop', 'num_actions', 'actions')

    def dump(self):
        raise NotImplementedError('FLIP entry dumps are not implemented!')
