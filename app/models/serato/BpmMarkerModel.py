from app.models.Tempo import Tempo


class BpmMarkerModel(Tempo):
    FIELDS = (
        'position',
        'bpm'
    )

    def __init__(self, *args):
        super().__init__()
        assert len(args) == len(self.FIELDS)
        for field, value in zip(self.FIELDS, args):
            setattr(self, field, value)

        self.set_position(float(getattr(self, 'position')))
        self.set_bpm(float(getattr(self, 'bpm')))
