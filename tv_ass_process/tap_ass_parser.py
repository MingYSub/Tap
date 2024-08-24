import io
import logging
import os
from typing import Optional, Union, List, Sequence

from .config import Config
from .constants import ASS_HEADER, MergeMode
from .tap_dialogue import TapDialogue
from .text_processing import *

logger = logging.getLogger("Tap")


class TapAssParser:
    def __init__(self, doc: Union[io.TextIOBase, str]):
        self.actor_record = {}
        self.events = []
        self.y_spacing = 0

        if isinstance(doc, io.TextIOBase):
            self.parse_file(doc)
        elif isinstance(doc, str):
            if os.path.isfile(doc):
                with open(doc, "r", encoding="utf-8_sig") as fp:
                    self.parse_file(fp)
            else:
                self.parse_str(doc)
        else:
            raise TypeError("doc must be a file or a string")

    def __iter__(self):
        return self.iterate_events()

    def iterate_events(self):
        for index, event in enumerate(self.events):
            yield index, event

    def parse_file(self, fp: io.TextIOBase):
        self.parse_str(fp.readlines())

    def parse_str(self, lines: Union[List[str], str]):
        def is_ruby(line: str):
            return ",Rubi," in line or "\\fscx50\\fscy50" in line

        if isinstance(lines, str):
            lines = lines.splitlines()
        for line in lines:
            if line.startswith("Dialogue:") and not is_ruby(line):
                event = TapDialogue(line)
                event.text = convert_full_half_width_characters(event.text)
                self.events.append(event)
            elif "ResX:" in line:
                try:
                    res_x = int(re.search(r"ResX: ?(\d+)", line).group(1))
                    self.x_spacing = int(180 * res_x / 540)
                except ValueError:
                    logger.warning("  PlayResX is not a number")
            elif "ResY:" in line:
                try:
                    res_y = int(re.search(r"ResY: ?(\d+)", line).group(1))
                    self.y_spacing = int(60 * res_y / 540)
                except ValueError:
                    logger.warning("  PlayResY is not a number")

    def process(self, user_config: Config) -> "TapAssParser":
        self.set_actor()
        logger.info("  set actor done")
        self.merge_duplicate_lines_by_time(user_config.merge)
        logger.info("  merge duplicate lines done")
        del_list = []

        for index, line in self:
            line.text = clean_up_text(line.text)
            text = line.text_stripped()
            if user_config.clean_mode:
                text = clean_trash(text)
            if text == "":
                del_list.append(index)
                continue

            if user_config.add_spaces:
                text = add_spaces(text)
            if user_config.adjust_repeated_syllables:
                text = adjust_repeated_syllables(text)

            text = replace_spaces_between_AN(text)

            line.text = text

        logger.info("  line process done")

        self.remove_lines(del_list)
        return self

    def set_actor(self) -> "TapAssParser":
        parenthesis_start_symbols = ("<", "＜", "《", "｟", "≪", "〈", "［")
        parenthesis_end_symbols = (">", "＞", "》", "｠", "≫", "〉", "］")
        continuous_line_symbols = ("→", "➡", "⤵️", "・")

        none_actor_index = 1
        same_actor_flag = False

        for index, line in self:
            # Three types of actor: parentheses, colon, color
            actor = None
            text_stripped = re.sub(r"{[^}]+}", "", line.text_stripped())

            # Find the specific speaker
            if text_stripped.startswith("(") and ")" in text_stripped:
                actor_tmp = re.search(r"\((.*?)\)", text_stripped).group(1)
                if text_stripped.replace(f"({actor_tmp})", "", 1) != "":
                    actor = actor_tmp
                    same_actor_flag = False
            elif "：" in text_stripped and text_stripped.index("：") < 8:
                actor = text_stripped[: text_stripped.index("：")]
                same_actor_flag = False

            if "\\c&" in line.text:  # Set the speaker based on the color
                text = re.sub(
                    r"{\\c&[0-9a-fhA-FH][^}]*}[　 ]*{\\c&H00FFFFFF[^}]*}", "", line.text
                )
                if "\\c&" in text:
                    color_index = line.text.find("\\c&")
                    color = line.text[color_index + 4 : color_index + 4 + 8]
                    if color not in self.actor_record:
                        self.actor_record[color] = actor or str(none_actor_index)
                    elif not actor:
                        actor = self.actor_record[color]
            else:  # Set the speaker based on parentheses or coordinates
                text_stripped = re.sub(
                    r"{[^}]+}", "", line.text_stripped(keep_symbols=True)
                )
                if (
                    same_actor_flag
                    or index > 0
                    and self.events[index - 1].text.endswith(continuous_line_symbols)
                ):
                    actor = self.events[index - 1].actor
                if text_stripped.startswith(parenthesis_start_symbols):
                    same_actor_flag = True
                if text_stripped.endswith(parenthesis_end_symbols):
                    same_actor_flag = False
                if not actor and not same_actor_flag and index > 0:
                    last_line = self.events[index - 1]
                    if (
                        (line.start, line.end) == (last_line.start, last_line.end)
                        and "\\c&" not in last_line.text
                        and (line.pos_x and last_line.pos_x)
                        and abs(line.pos_x - last_line.pos_x) <= self.x_spacing
                        and abs(line.pos_y - last_line.pos_y) <= self.y_spacing
                        and 1
                    ):
                        actor = last_line.actor
            if actor:
                line.actor = actor
            else:
                line.actor = str(none_actor_index)
                none_actor_index += 1

            logger.debug(
                f'{line.actor}: {re.sub(r"{[^}]+}", "", line.text_stripped())}'
            )

        return self

    def remove_lines(self, indexes_to_remove: Sequence[int]) -> "TapAssParser":
        for index in sorted(indexes_to_remove, reverse=True):
            self.events.pop(index)
        return self

    def merge_duplicate_lines_by_time(
        self, mode: MergeMode = MergeMode.AUTO_MERGE
    ) -> "TapAssParser":
        if mode not in [
            MergeMode.AUTO_MERGE,
            MergeMode.NO_MERGE,
            MergeMode.FORCE_MERGE,
        ]:
            raise ValueError(f"Invalid mode.")

        if mode == MergeMode.NO_MERGE:
            return self

        del_list = []

        for index in range(len(self.events) - 1):
            event = self.events[index]
            next_event = self.events[index + 1]
            if event.start == next_event.start and event.end == next_event.end:
                if event.actor == next_event.actor:
                    next_event.text = event.text + "\u3000" + next_event.text
                    if mode == MergeMode.AUTO_MERGE:
                        next_event.text = next_event.text.replace(
                            "？\u3000", "？"
                        ).replace("！\u3000", "！")
                    del_list.append(index)
                elif mode == MergeMode.FORCE_MERGE:
                    next_event.actor = event.actor + "/" + next_event.actor
                    next_event.text = event.text + "\n" + next_event.text
                    del_list.append(index)

        self.remove_lines(del_list)

        return self

    def save(
        self,
        path,
        format_: Optional[str] = None,
        actor: bool = False,
        ending_char: str = "",
    ):
        if format_ is None:
            format_ = path[-3:]
        if format_ not in ["txt", "ass", "srt"]:
            raise ValueError(f"Invalid format: {format_}")

        mapping = {
            "txt": self.to_txt,
            "ass": self.to_ass,
            "srt": self.to_srt,
        }
        with open(
            path, "w", encoding="utf-8_sig" if format_ == "ass" else "utf-8"
        ) as f:
            f.write(mapping[format_](actor, ending_char))

    def to_txt(self, actor: bool = False, ending_char: str = ""):
        res = []
        for line in self.events:
            text = line.replace("\n", "\u3000")
            res.append(
                f"[{line.actor}]\t{text}{ending_char}"
                if actor
                else f"{text}{ending_char}"
            )
        return "\n".join(res)

    def to_ass(self, actor: bool = False, ending_char: str = ""):
        res = [ASS_HEADER]
        for line in self.events:
            text = line.replace("\n", "\\N")
            res.append(
                f'Dialogue: 0,{line.start},{line.end},JP,{line.actor or "" if actor else ""},0,0,0,,{text}{ending_char}'
            )
        return "\n".join(res)

    def to_srt(self, actor: bool = False, ending_char: str = ""):
        res = []
        for i, line in self:
            res.append(
                "%d\n%s --> %s\n%s%s%s\n"
                % (
                    i + 1,
                    f'0{line.start.replace(".", ",")}',
                    f'0{line.end.replace(".", ",")}',
                    f"{{{line.actor}}}" if actor and line.actor else "",
                    line.text,
                    ending_char,
                )
            )
        return "\n".join(res)
