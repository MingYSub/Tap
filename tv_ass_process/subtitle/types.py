from dataclasses import dataclass
from itertools import takewhile


class Timecode(int):
    def __new__(cls, time: str | int):
        if isinstance(time, str):
            h, m, s = map(float, time.split(':'))
            time = int((h * 3600 + m * 60 + s) * 1000)
        elif not isinstance(time, int):
            raise TypeError("Unsupported type")
        return super().__new__(cls, time)

    def __repr__(self):
        return f"Timecode({int(self)})"

    def __str__(self):
        return self.to_ass_string()

    def to_ass_string(self) -> str:
        ms = max(0, self)
        ms = int(round(ms))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:01d}:{m:02d}:{s:02d}.{ms:03d}"[:-1]

    def to_srt_string(self) -> str:
        ms = max(0, self)
        ms = int(round(ms))
        h, ms = divmod(ms, 3600000)
        m, ms = divmod(ms, 60000)
        s, ms = divmod(ms, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


@dataclass(frozen=True)
class Position:
    x: int
    y: int


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int

    @classmethod
    def parse(cls, color_str: str):
        color_str = color_str.lstrip("&H").lstrip(" \t").upper()
        color_str = "".join(takewhile(lambda x: x in "0123456789ABCDEF", color_str))
        value = int(color_str, 16)
        if value < 0 or value > 0xFFFFFF:
            return 255, 255, 255
        r = value & 0xFF
        g = (value >> 8) & 0xFF
        b = (value >> 16) & 0xFF
        return cls(r, g, b)

    def to_ass_color(self):
        return f"&H{self.b:02X}{self.g:02X}{self.r:02X}&"

    def __repr__(self):
        return f"Color({self.to_ass_color()})"
