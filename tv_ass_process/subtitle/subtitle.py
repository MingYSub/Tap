import logging
import re
from pathlib import Path

from .events import Dialog, Events
from ..config import OutputSettings
from ..constants import ASS_HEADER

__all__ = [
    "Subtitle",
    "load",
    "from_ass_text",
]

logger = logging.getLogger("Tap")


class Subtitle:
    def __init__(self):
        self.res_x = 960
        self.res_y = 540
        self.events = Events()

    @classmethod
    def load(cls, path: Path | str, encoding: str = "utf-8") -> "Subtitle":
        path = Path(path)
        with path.open("r", encoding=encoding) as f:
            return cls.from_ass_text(f.read())

    @classmethod
    def from_ass_text(cls, ass_text: str) -> "Subtitle":
        doc = cls()
        lines = ass_text.splitlines()
        for line in lines:
            if line.startswith("Dialogue:"):
                doc.events.append(Dialog.parse(line))
            elif "ResX:" in line:
                try:
                    doc.res_x = int(re.search(r"ResX: ?(\d+)", line).group(1))
                except ValueError:
                    logger.warning("PlayResX is not a number")
            elif "ResY:" in line:
                try:
                    doc.res_y = int(re.search(r"ResY: ?(\d+)", line).group(1))
                except ValueError:
                    logger.warning("PlayResY is not a number")
        return doc

    def to_ass(self, show_speaker: bool = False, ending_char: str = "") -> str:
        return ASS_HEADER + self.events.to_ass_string(show_speaker, ending_char)

    def to_srt(self, show_speaker: bool = False, ending_char: str = "") -> str:
        return self.events.to_srt_string(show_speaker, ending_char)

    def to_txt(self, show_speaker: bool = False, ending_char: str = "", show_pause_tip: int = 0) -> str:
        result = []
        last_end = 0
        for event in self.events:
            if event.start - last_end >= show_pause_tip * 1000 > 0:
                result.append(f"({(event.start - last_end) // 1000}-second pause)")
            last_end = event.end
            text = event.text.replace("\n", "\u3000")
            result.append(
                f"[{event.name}]\t{text}{ending_char}"
                if show_speaker
                else f"{text}{ending_char}"
            )
        return "\n".join(result)

    def save(self, path: Path | str, config: OutputSettings | None = None) -> None:
        config = config or OutputSettings()
        path = Path(path)
        if path.suffix == ".ass":
            text = self.to_ass(config.show_speaker, config.ending)
        elif path.suffix == ".srt":
            text = self.to_srt(config.show_speaker, config.ending)
        elif path.suffix == ".txt":
            text = self.to_txt(config.show_speaker, config.ending, config.show_pause_tip)
        else:
            raise ValueError(f"Invalid format: {path.suffix}")

        encoding = "utf-8-sig" if path.suffix == ".ass" else "utf-8"
        with open(path, "w", encoding=encoding) as f:
            f.write(text)

    def __repr__(self) -> str:
        return f"Subtitle(with {len(self.events)} events)"


load = Subtitle.load
from_ass_text = Subtitle.from_ass_text
