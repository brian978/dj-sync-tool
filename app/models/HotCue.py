from app.utils.colors import rgb_to_hex


class HotCue:
    name = None
    start = None
    end = None
    index = 0
    color = []
    type = None

    def hex_color(self):
        return rgb_to_hex(self.color[0], self.color[1], self.color[2])
