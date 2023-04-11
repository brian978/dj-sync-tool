from app.utils.colors import rgb_to_hex


class HotCue:
    def __init__(self):
        self.name = None
        self.start = None
        self.end = None
        self.index = 0
        self.color = []
        self.type = None

    def hex_color(self):
        return rgb_to_hex(self.color[0], self.color[1], self.color[2])
