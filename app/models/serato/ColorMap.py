class ColorMap:
    map = {
        "DE44CF": "CE359E",
        "B432FF": "5C3F97",
        "AA72FF": "6823B6",
        "6473FF": "173BA2",
        "305AFF": "16308B",
        "50B4FF": "0F88CA",
        "00E0FF": "1DBEBD",
        "1FA392": "2BB673",
        "10B176": "8DC63F",
        "28E214": "1FAD26",
        "A5E116": "4EB648",
        "B4BE04": "8DC63F",
        "C3AF04": "FAC313",
        "E0641B": "DB4E27",
        "FF8C00": "DB4E27",  # some orange that somehow was not detected by the palette
        "E62828": "C02626",
        "FF127B": "C71136"
    }

    @classmethod
    def from_serato(cls, color: str):
        # list out keys and values separately
        base_colors = list(cls.map.keys())
        serato_colors = list(cls.map.values())

        position = serato_colors.index(color.upper())

        return base_colors[position]

    @classmethod
    def to_serato(cls, color: str):
        return cls.map[color.upper()]
