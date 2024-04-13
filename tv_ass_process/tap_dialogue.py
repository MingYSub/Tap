import re
from .constants import CHARS_TO_DELETE, REPLACEMENT_DICT
import logging


logger = logging.getLogger('Tap')


class TapDialogue:
    def __init__(self, dialogue_line: str):
        parts = dialogue_line.split(',', 9)
        self.start, self.end = parts[1].strip(), parts[2].strip()
        self.text = parts[9].strip()

        pos_match = re.search(r'\\pos\(\d+,(\d+)\)', self.text)
        if pos_match:
            self.pos_y = int(pos_match.group(1))
        else:
            self.pos_y = 0
            logger.warning('\tCannot find pos tag')

        self.actor = '-1'

    def __str__(self) -> str:
        return self.text

    @property
    def text_stripped(self) -> str:
        text = self.text
        for char in CHARS_TO_DELETE:
            text = text.replace(char, '')
        for old, new in REPLACEMENT_DICT.items():
            text = text.replace(old, new)
        return text

    def replace(self, old: str, new: str) -> str:
        return self.text.replace(old, new)
