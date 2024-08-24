import re
import logging


logger = logging.getLogger("Tap")


class TapDialogue:
    def __init__(self, dialogue_line: str):
        parts = dialogue_line.split(",", 9)
        self.start, self.end = parts[1].strip(), parts[2].strip()
        self.text = parts[9].strip()

        pos_match = re.search(r"\\pos\((\d+),(\d+)\)", self.text)
        if pos_match:
            self.pos_x = int(pos_match.group(1))
            self.pos_y = int(pos_match.group(2))
        else:
            self.pos_x = 0
            self.pos_y = 0
            logger.warning("\tCannot find pos tag")

        self.actor = "None"

    def __str__(self) -> str:
        return self.text

    def text_stripped(self, keep_symbols: bool = False) -> str:
        CHARS_TO_DELETE = "《》≪≫<>＜＞｟｠〈〉［］→➡⤵️♬⚟⚞📱☎🔊📺🎤"
        REPLACEMENT_DICT = {
            "\u200e": "",
            "\\N": "",
            "?": "？",
            "!": "！",
            " ": "\u3000",
            "「\u3000": "「",
            "\u3000」": "」",
            "…。": "…",
            "。\u3000": "\u3000",
            "。\n": "\n",
            "。": "\u3000",
            "}・": "}",
            "((": "",
            "))": "",
        }
        text = self.text
        if not keep_symbols:
            for char in CHARS_TO_DELETE:
                text = text.replace(char, "")
        for old, new in REPLACEMENT_DICT.items():
            text = text.replace(old, new)
        return text

    def replace(self, old: str, new: str) -> str:
        return self.text.replace(old, new)
