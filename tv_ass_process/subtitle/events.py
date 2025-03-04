import logging
import re
from collections.abc import Sequence
from dataclasses import dataclass

from .types import Timecode, Position, Color

OVERRIDE_BLOCK_PATTERN = re.compile(r"(?<!\\){([^}]*)}")

logger = logging.getLogger("Tap")


@dataclass
class Dialog(dict):
    start: Timecode
    end: Timecode
    style: str
    text: str
    name: str = ""
    pos: Position = Position(0, 0)
    color: Color = Color(255, 255, 255)

    @classmethod
    def parse(cls, line):
        splits = line.split(",", 9)

        start = Timecode(splits[1].strip())
        end = Timecode(splits[2].strip())
        style = splits[3].strip()
        name = splits[4].strip()
        text = splits[9].strip().removesuffix("\\N")

        if "\\fscx50\\fscy50" in text:
            style = "Rubi"

        pos_match = re.search(r"\\pos\((\d+),(\d+)\)", text)
        if pos_match:
            pos = Position(*map(int, pos_match.groups()))
        else:
            pos = Position(0, 0)
            logger.warning(f"No position found in line: {text}")

        text = re.sub(r"{([^}]*)\\c&[0-9a-fhA-FH]([^}]*)}(\s*{\\c&[0-9a-fhA-FH][^}]*})", r"{\1\2}\3", text)
        color_match = re.search(r"\\c([&hH0-9a-fA-F]+?)(?=[\\}])", text)
        color = Color.parse(color_match.group(1)) if color_match else Color(255, 255, 255)

        text = OVERRIDE_BLOCK_PATTERN.sub("", text)

        return cls(start, end, style, text, name, pos, color)

    def to_ass_string(self, actor: bool = False, ending_char: str = "") -> str:
        return f"Dialogue: 0,{self.start},{self.end},JP,{self.name if actor else ""}" \
               f",0,0,0,,{self.text.replace("\n", "\\N") + ending_char}"


class Events(list[Dialog]):
    def pop(self, index: int | Sequence[int] = -1) -> None:
        if isinstance(index, int):
            index = (index,)
        for i in sorted(index, reverse=True):
            super().pop(i)

    def to_ass_string(self, show_speaker: bool = False, ending_char: str = ""):
        return "\n".join(l.to_ass_string(show_speaker, ending_char) for l in self)

    def to_srt_string(self, show_speaker: bool = False, ending_char: str = ""):
        result = []
        for i, line in enumerate(self):
            result.append(
                "%d\n%s --> %s\n%s%s%s\n"
                % (
                    i + 1,
                    line.start.to_srt_string(),
                    line.end.to_srt_string(),
                    f"{{{line.name}}}" if show_speaker and line.name else "",
                    line.text,
                    ending_char,
                )
            )
        return "\n".join(result)
