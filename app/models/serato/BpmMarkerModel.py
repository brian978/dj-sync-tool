class BpmMarkerModel(object):
    FIELDS = (
        'position',
        'bpm'
    )

    def __init__(self, *args):
        assert len(args) == len(self.FIELDS)
        for field, value in zip(self.FIELDS, args):
            setattr(self, field, value)
