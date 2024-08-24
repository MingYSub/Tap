import logging
import os
import re

from tv_ass_process import (
    TapAssParser,
    MergeMode,
    Config,
    SCRIPT_VERSION,
    SUPPORTED_EXTENSIONS,
)
from replace_dict import CUSTOM_REPLACEMENTS, REGULAR_REPLACEMENTS

logger = logging.getLogger("Tap")
logger.setLevel(logging.INFO)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(consoleHandler)


def argparse_config():
    from argparse import ArgumentParser

    parser = ArgumentParser(
        description=f"Tap {SCRIPT_VERSION} (TV Ass Process) | Processing ASS subtitles extracted from ts files"
    )
    parser.add_argument(
        "path", type=str, nargs="+", help="Input path (supports files and directories)"
    )
    parser.add_argument(
        "--conf", dest="conf_path", type=str, help="Specify configuration file"
    )
    parser.add_argument(
        "--format",
        dest="output_format",
        type=str,
        choices=SUPPORTED_EXTENSIONS,
        help="Specify output format",
    )
    parser.add_argument(
        "--output", "-o", dest="output_path", type=str, help="Specify output path"
    )
    parser.add_argument(
        "--suffix",
        "-x",
        dest="ending_char",
        type=str,
        help="Char(s) appended to the end of each line",
    )

    group_actor = parser.add_mutually_exclusive_group(required=False)
    group_actor.add_argument(
        "--actor", "-a", dest="actor", action="store_true", help="Output speaker"
    )
    group_actor.add_argument(
        "--no-actor",
        "-an",
        dest="actor",
        action="store_false",
        help="Do not output speaker",
    )
    group_actor.set_defaults(actor=None)

    group_clean = parser.add_mutually_exclusive_group(required=False)
    group_clean.add_argument(
        "--clean",
        "-c",
        dest="clean_mode",
        action="store_true",
        help="Remove interjections",
    )
    group_clean.add_argument(
        "--no-clean",
        "-cn",
        dest="clean_mode",
        action="store_false",
        help="Do not remove interjections",
    )
    group_clean.set_defaults(clean_mode=None)

    group_merge = parser.add_mutually_exclusive_group(required=False)
    group_merge.add_argument(
        "--merge",
        "-m",
        dest="merge",
        action="store_const",
        const=MergeMode.AUTO_MERGE,
        help="Automatically merge lines with overlapping times",
    )
    group_merge.add_argument(
        "--no-merge",
        "-mn",
        dest="merge",
        action="store_const",
        const=MergeMode.NO_MERGE,
        help="Do not merge lines with overlapping times",
    )
    group_merge.add_argument(
        "--force-merge",
        "-mf",
        dest="merge",
        action="store_const",
        const=MergeMode.FORCE_MERGE,
        help="Force merge lines with overlapping times",
    )
    group_merge.set_defaults(merge=None)

    group_space = parser.add_mutually_exclusive_group(required=False)
    group_space.add_argument(
        "--space",
        "-s",
        dest="add_spaces",
        action="store_true",
        help="Add space between CJK and AN characters",
    )
    group_space.add_argument(
        "--no-space",
        "-sn",
        dest="add_spaces",
        action="store_false",
        help="Do not add space between CJK and AN characters",
    )
    group_space.set_defaults(add_spaces=None)

    group_repeated_syllables = parser.add_mutually_exclusive_group(required=False)
    group_repeated_syllables.add_argument(
        "--adjust-repeated-syllables",
        "-rs",
        dest="adjust_repeated_syllables",
        action="store_true",
        help="Adjust repeated syllables",
    )
    group_repeated_syllables.add_argument(
        "--no-adjust-repeated-syllables",
        "-rsn",
        dest="adjust_repeated_syllables",
        action="store_false",
        help="Do not adjust repeated syllables",
    )

    group_repeated_syllables.set_defaults(adjust_repeated_syllables=None)

    args = parser.parse_args()
    if args.conf_path:
        if os.path.isfile(args.conf_path):
            conf_path = args.conf_path
        else:
            logger.warning("Configuration file does not exist, skipping.")
            conf_path = os.path.join(os.path.dirname(__file__), "user_config.json")
    else:
        conf_path = os.path.join(os.path.dirname(__file__), "user_config.json")

    user_config = Config(conf_path)
    for key, value in vars(args).items():
        if value is not None:
            setattr(user_config, key, value)
    return user_config


def get_ass_files(paths):
    result = []
    for element in paths:
        if os.path.isfile(element):
            if element.endswith(".ass"):
                result.append(element)
            else:
                logger.warning(f"The file is not in ASS format: {element}")
        elif os.path.isdir(element):
            ass_files = [
                os.path.join(element, file)
                for file in os.listdir(element)
                if file.endswith(".ass") and not file.endswith("_processed.ass")
            ]
            if len(ass_files):
                result.extend(ass_files)
            else:
                logger.warning(f"No ASS files found in the directory: {element}")
        else:
            logger.warning(f"The path does not exist: {element}")
    return result


def main():
    user_config = argparse_config()
    output_format = user_config.output_format
    output_dir = None
    ass_files = get_ass_files(user_config.path)
    if len(ass_files) > 1 and user_config.output_path:
        parts = os.path.splitext(user_config.output_path)
        if parts[1]:
            logger.warning(
                f"Output path should be a directory; output will be saved to the original file's directory."
            )
            user_config.output_path = None
        else:
            os.makedirs(user_config.output_path, exist_ok=True)
            output_dir = parts[0]
    elif len(ass_files) == 1 and user_config.output_path:
        parts = os.path.splitext(user_config.output_path)
        if parts[1]:
            file_extension = parts[1][1:].lower()
            if os.path.realpath(user_config.output_path) == os.path.realpath(
                ass_files[0]
            ):
                logger.warning(f"The output path cannot be the same as the input path.")
                user_config.output_path = None
            if file_extension in SUPPORTED_EXTENSIONS:
                logger.warning(f"Output will be in {file_extension} format.")
                output_format = parts[1][1:]
            else:
                logger.warning(
                    f"The output path extension is invalid; output will be in {output_format} format."
                )
                user_config.output_path = parts[0] + "." + user_config.output_format
        else:
            os.makedirs(user_config.output_path, exist_ok=True)
            output_dir = parts[0]

    logger.info("Config")
    for k, v in vars(user_config).items():
        if k == "path":
            continue
        logger.info(f"  {k}: {v}")
    for single_file in ass_files:
        if output_dir is not None:
            output_file = (
                os.path.join(output_dir, os.path.basename(single_file))[:-4]
                + f"_processed.{output_format}"
            )
        else:
            output_file = (
                user_config.output_path
                or f"{single_file[:-4]}_processed.{output_format}"
            )

        logger.info(f"Start: {single_file}")
        subs = TapAssParser(single_file).process(user_config)
        for _, line in subs:
            for old, new in CUSTOM_REPLACEMENTS.items():
                line.text = line.replace(old, new)
            for pattern, replacement in REGULAR_REPLACEMENTS.items():
                line.text = re.sub(pattern, replacement, line.text)
        subs.save(
            output_file, output_format, user_config.actor, user_config.ending_char
        )
        logger.info(f"Done: {single_file}")


if __name__ == "__main__":
    main()
