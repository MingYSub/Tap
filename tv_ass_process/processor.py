import logging
from collections import defaultdict
from pathlib import Path
from typing import overload

from .config import ProcessingConfig, MergeStrategy
from .subtitle import Subtitle, Events
from .subtitle.types import Color
from .text_processing import *

logger = logging.getLogger("Tap")

WHITE = Color(255, 255, 255)

AUDIO_MARKERS = ("♪♪", "♪", "♬", "⚟", "⚞", "📱", "☎", "🔊", "📢", "📺", "🎤",
                 "💻", "🎧", "📼", "🖭", "・", "〓", "⎚", "＝", "≫")
PARENTHESIS_START_MARKERS = ("<", "＜", "《", "｟", "≪", "〈", "［", "（（")
PARENTHESIS_END_MARKERS = (">", "＞", "》", "｠", "≫", "〉", "］", "））")
CONTINUOUS_LINE_MARKERS = ("→", "➡", "⤵️", "・")


def remove_line_markers(text: str) -> str:
    for marker in PARENTHESIS_START_MARKERS:
        text = text.removeprefix(marker)
    for marker in PARENTHESIS_END_MARKERS:
        text = text.removesuffix(marker)
    for marker in CONTINUOUS_LINE_MARKERS:
        text = text.removesuffix(marker)
    return text.removeprefix("～")


def guess_same_speaker(event1, event2, x_spacing=60, y_spacing=60) -> bool:
    return (event1.start == event2.start and event1.end == event2.end
            and event1.color == event1.color
            and event1.pos.y and event2.pos.y
            and abs(event1.pos.x - event2.pos.x) <= x_spacing
            and abs(event1.pos.y - event2.pos.y) <= y_spacing)


class Processor:
    def __init__(self, config: ProcessingConfig | None = None):
        self.config = config or ProcessingConfig()

    def set_config(self, config: ProcessingConfig) -> None:
        self.config = config

    @overload
    def __call__(self, doc: Subtitle) -> None:
        ...

    @overload
    def __call__(self, path: Path | str) -> None:
        ...

    def __call__(self, doc_or_path: Subtitle | Path | str) -> None:
        if isinstance(doc_or_path, Subtitle):
            self.process_subtitle(doc_or_path)
        else:
            self.process_and_save(doc_or_path)

    def process_and_save(self, path: Path | str) -> None:
        logger.info(f"Starting processing {path}")
        path = Path(path)
        doc = Subtitle.load(path)
        self.process_subtitle(doc)
        output_filename = path.with_name(f"{path.stem}_processed.{self.config.output.format}").name
        output_path = (self.config.output.dir or path.parent) / output_filename
        doc.save(output_path, self.config.output)
        logger.info(f"Finished processing. Saved to {output_path}")

    def process_subtitle(self, doc: Subtitle) -> None:
        logger.info("Starting subtitle processing...")

        del_list = [index for index, event in enumerate(doc.events) if event.style == "Rubi"]
        doc.events.pop(del_list)
        logger.info(f"Removed {len(del_list)} Rubi events")

        raw = "．％／＆＋－＝･“”(): ｡。、"
        converted = ".%/&+-=・「」（）：\u3000\u3000\u3000\u3000"
        trans = str.maketrans(raw, converted)
        for event in doc.events:
            event.text = convert_half_full_numbers(event.text, self.config.full_half_conversion.numbers)
            event.text = convert_half_full_letters(event.text, self.config.full_half_conversion.letters)
            event.text = event.text.translate(trans)
        if self.config.full_half_conversion.convert_half_katakana:
            for event in doc.events:
                event.text = convert_half_katakana(event.text)
        logger.info("Normalized full-width/half-width characters")

        for event in doc.events:
            # remove audio markers
            for marker in AUDIO_MARKERS:
                event.text = event.text.removeprefix(marker)
            event.text = event.text.replace("\u3000\u3000", "\u3000").strip()
            # handle gaiji
            event.text = re.sub(r"\[外：[0-9A-Z]{32}]", "", event.text)
        logger.info("Completed text preprocessing")

        self.set_speakers(doc)
        logger.info("Assigned speakers")

        for event in doc.events:
            event.text = remove_line_markers(event.text).strip()
            for marker in AUDIO_MARKERS:
                event.text = event.text.removeprefix(marker).strip()
            if event.text.startswith("（") and "）" in event.text:
                event.text = event.text[event.text.index("）") + 1:]
            elif not event.name.startswith("Unknown"):
                event.text = event.text.removeprefix(event.name + "：").removeprefix(event.name + "≫")
            for marker in AUDIO_MARKERS:
                event.text = event.text.removeprefix(marker)
            event.text = remove_line_markers(event.text).strip()
        self.filter_empty_lines(doc)
        logger.info("Cleaned up text")

        if self.config.merge_strategy != MergeStrategy.NONE:
            self.merge_duplicate_lines_by_time(doc, self.config.merge_strategy)
            logger.info("Merged duplicate lines based on timing")

        if self.config.filter_interjections:
            for event in doc.events:
                event.text = filter_interjections(event.text)
            self.filter_empty_lines(doc)
            logger.info("Filtered interjections")

        if self.config.cjk_spacing.enabled:
            for event in doc.events:
                event.text = cjk_spacing(event.text, self.config.cjk_spacing.space_char)
            logger.info("Applied CJK spacing adjustments")

        if self.config.repetition_adjustment.enabled:
            for event in doc.events:
                event.text = adjust_repeated_syllables(event.text, self.config.repetition_adjustment.connector)
            logger.info("Adjusted repeated syllables")

        for event in doc.events:
            for key, value in self.config.mapping.text.items():
                event.text = event.text.replace(key, value)
            for pattern, replacement in self.config.mapping.regex.items():
                event.text = re.sub(pattern, replacement, event.text)
        logger.info(f"Finished custom text replacements")

        for event in doc.events:
            event.text = fix_western_text(event.text)
        logger.info("Fixed western text formatting")

        logger.info("Subtitle processing completed successfully")

    @staticmethod
    def set_speakers(doc: Subtitle) -> None:
        speaker_record = defaultdict(set)

        x_spacing = int(60 * doc.res_x / 960)
        y_spacing = int(60 * doc.res_y / 540)

        none_speaker_count = 1
        same_speaker_flag = False

        for index, event in enumerate(doc.events):
            speaker = None
            text_stripped = remove_line_markers(event.text)

            # Find the specific speaker
            if text_stripped.startswith("（") and "）" in text_stripped:
                speaker_tmp = re.search(r"（(.*?)）", text_stripped).group(1)
                if text_stripped[len(speaker_tmp) + 2:].strip() or index + 1 < len(doc.events) and guess_same_speaker(
                        event, doc.events[index + 1], x_spacing, y_spacing):
                    speaker = speaker_tmp.strip().removesuffix("の声")
                    if "：" in speaker:
                        speaker = speaker[speaker.index("："):].strip()
                    same_speaker_flag = False
            elif "：" in text_stripped:
                speaker = text_stripped[:text_stripped.index("：")].strip()
                same_speaker_flag = False
            elif "≫" in text_stripped:
                speaker = text_stripped[:text_stripped.index("≫")].strip()
                same_speaker_flag = False

            if event.color != WHITE:
                # Set the speaker based on the color
                if event.color not in speaker_record or speaker and speaker not in speaker_record[event.color]:
                    logger.debug(f"Speaker found for {event.color}: {speaker}")
                speaker_record[event.color].add(speaker or "")
                speaker = event.color.to_ass_string()
            else:
                # Set the speaker based on parentheses or coordinates
                text = event.text
                if same_speaker_flag or index > 0 and doc.events[index - 1].text.endswith(CONTINUOUS_LINE_MARKERS):
                    speaker = doc.events[index - 1].name
                if text.startswith(PARENTHESIS_START_MARKERS):
                    same_speaker_flag = True
                if text.endswith(PARENTHESIS_END_MARKERS):
                    same_speaker_flag = False
                if not speaker and not same_speaker_flag and index > 0:
                    last_event = doc.events[index - 1]
                    if guess_same_speaker(event, last_event, x_spacing, y_spacing):
                        speaker = last_event.name

            if speaker:
                event.name = speaker
            else:
                event.name = f"Unknown{none_speaker_count}"
                none_speaker_count += 1

        color_speaker_mapping = {
            color: max(speakers, key=len) or f"Protagonist{i + 1}"
            for i, (color, speakers) in enumerate(speaker_record.items())
        }

        for event in doc.events:
            if event.color in color_speaker_mapping:
                event.name = color_speaker_mapping[event.color]

    @staticmethod
    def merge_duplicate_lines_by_time(doc: Subtitle, strategy: MergeStrategy = MergeStrategy.AUTO) -> None:
        if strategy not in MergeStrategy:
            raise ValueError(f"Invalid strategy: {strategy}")

        if strategy == MergeStrategy.NONE:
            return

        del_list = []

        for index in range(len(doc.events) - 1):
            event = doc.events[index]
            next_event = doc.events[index + 1]
            if event.start == next_event.start and event.end == next_event.end:
                if event.name == next_event.name:
                    next_event.text = event.text + "\u3000" + next_event.text
                    del_list.append(index)
                elif strategy == MergeStrategy.FORCE:
                    next_event.name = event.name + "/" + next_event.name
                    next_event.text = event.text + "\n" + next_event.text
                    del_list.append(index)

        doc.events.pop(del_list)

    @staticmethod
    def filter_empty_lines(doc: Subtitle) -> None:
        doc.events = Events(event for event in doc.events if event.text)
