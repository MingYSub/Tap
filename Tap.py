from replace_dict import CUSTOM_REPLACEMENTS, REGULAR_REPLACEMENTS
from tv_ass_process.constants import SCRIPT_VERSION, SUPPORTED_EXTENSIONS, NO_MERGE, AUTO_MERGE, FORCE_MERGE
from tv_ass_process.config import Config
from tv_ass_process.tap_ass_parser import TapAssParser
import re
import os


def display_error(error_str):
    print(f'[ERROR] {error_str}')
    os._exit(1)


def display_warning(error_str):
    print(f'[WARNING] {error_str}')


def display_info(info_str):
    print(f'[INFO] {info_str}')


def argparse_config():
    from argparse import ArgumentParser
    global user_config
    user_config = Config()

    parser = ArgumentParser(
        description=f'Tap {SCRIPT_VERSION} (TV Ass Process) | 处理从 TV 提取的 ASS 字幕')
    parser.add_argument('path', type=str, nargs='+', help='输入路径（支持文件和文件夹）')
    parser.add_argument('--format', dest='output_format',
                        type=str, choices=SUPPORTED_EXTENSIONS, help='指定输出格式')
    parser.add_argument('--output', '-o', dest='output_path',
                        type=str, help='指定输出路径')

    group_actor = parser.add_mutually_exclusive_group(required=False)
    group_actor.add_argument(
        '--actor', '-a', dest='actor', action='store_true', help='输出说话人')
    group_actor.add_argument(
        '--no-actor', '-an', dest='actor', action='store_false', help='不输出说话人')
    group_actor.set_defaults(actor=user_config.actor)

    group_clean = parser.add_mutually_exclusive_group(required=False)
    group_clean.add_argument(
        '--clean', '-c', dest='clean_mode', action='store_true', help='删除语气词')
    group_clean.add_argument(
        '--no-clean', '-cn', dest='clean_mode', action='store_false', help='不删除语气词')
    group_clean.set_defaults(clean_mode=user_config.clean_mode)

    group_merge = parser.add_mutually_exclusive_group(required=False)
    group_merge.add_argument(
        '--merge', '-m', dest='merge', action='store_const', const=AUTO_MERGE, help='合并时间重复行')
    group_merge.add_argument(
        '--no-merge', '-mn', dest='merge', action='store_const', const=NO_MERGE, help='不合并时间重复行')
    group_merge.add_argument(
        '--force-merge', '-mf', dest='merge', action='store_const', const=FORCE_MERGE, help='强制合并时间重复行')
    group_merge.set_defaults(merge=user_config.merge)

    group_space = parser.add_mutually_exclusive_group(required=False)
    group_space.add_argument(
        '--space', '-s', dest='add_spaces', action='store_true', help='中西文之间添加空格')
    group_space.add_argument(
        '--no-space', '-sn', dest='add_spaces', action='store_false', help='中西文之间不添加空格')
    group_space.set_defaults(add_spaces=user_config.add_spaces)

    group_repeated_syllables = parser.add_mutually_exclusive_group(
        required=False)
    group_repeated_syllables.add_argument(
        '--adjust-repeated-syllables', '-rs', dest='adjust_repeated_syllables', action='store_true', help='整理重复音节')
    group_repeated_syllables.add_argument(
        '--no-adjust-repeated-syllables', '-rsn', dest='adjust_repeated_syllables', action='store_false', help='不整理重复音节')
    group_repeated_syllables.set_defaults(
        adjust_repeated_syllables=user_config.adjust_repeated_syllables)

    args = parser.parse_args()
    for key, value in vars(args).items():
        if not value is None:
            setattr(user_config, key, value)


def get_ass_files(path):
    result = []
    for element in path:
        if os.path.isfile(element):
            if element.endswith('.ass'):
                result.append(element)
            else:
                display_warning(f'所选文件非 ass 格式: {element}')
        elif os.path.isdir(element):
            ass_files = [
                element+'\\' + file for file in os.listdir(element) if file.endswith('.ass') and not file.endswith('_processed.ass')]
            if len(ass_files):
                result.extend(ass_files)
            else:
                display_warning(f'该目录下无 ass 文件: {element}')
        else:
            display_warning(f'该路径不存在: {element}')
    return result


def main():
    argparse_config()
    output_format = user_config.output_format
    output_dir_flag = False
    ass_files = get_ass_files(user_config.path)
    if len(ass_files) > 1 and user_config.output_path:
        parts = os.path.splitext(user_config.output_path)
        if parts[1]:
            display_warning(f'输出路径应为目录，将输出到原文件目录下。')
            user_config.output_path = None
        else:
            os.makedirs(user_config.output_path, exist_ok=True)
            output_dir_flag = True
            output_dir = parts[0]
    elif len(ass_files) == 1 and user_config.output_path:
        parts = os.path.splitext(user_config.output_path)
        if parts[1]:
            file_extension = parts[1][1:].lower()
            if os.path.realpath(user_config.output_path) == os.path.realpath(ass_files[0]):
                display_warning(f'输出路径不可与输入路径相同。')
                user_config.output_path = None
            if file_extension in SUPPORTED_EXTENSIONS:
                display_warning(f'将输出为 {file_extension} 格式。')
                output_format = parts[1][1:]
            else:
                display_warning(f'输出路径后缀名不符合要求，将输出为 {output_format} 格式。')
                user_config.output_path = parts[0]+user_config.output_format
        else:
            os.makedirs(user_config.output_path, exist_ok=True)
            output_dir_flag = True
            output_dir = parts[0]

    # display_info('当前配置')
    # for k, v in user_config.__dict__.items():
    #     display_info(f'{k}: {v}')
    for single_file in ass_files:
        if output_dir_flag:
            output_file = os.path.join(output_dir, os.path.basename(single_file))[
                :-4] + f'_processed.{output_format}'
        else:
            output_file = user_config.output_path or f'{single_file[:-4]}_processed.{output_format}'
        subs = TapAssParser(single_file).parse().process(user_config)
        for _, line in subs:
            for old, new in CUSTOM_REPLACEMENTS.items():
                line.text = line.replace(old, new)
            for pattern, replacement in REGULAR_REPLACEMENTS.items():
                line.text = re.sub(pattern, replacement, line.text)
        exec(
            f'subs.write_{output_format}(output_file, user_config.actor, user_config.ending_char)')
        display_info(f'Done: {single_file}')


if __name__ == '__main__':
    main()
