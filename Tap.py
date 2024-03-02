from replace_dict import *
import re
import os

SCRIPT_VERSION = 'v0.4.0'
GITHUB_LINK = 'https://github.com/MingYSub/Tap'

SUPPORTED_EXTENSIONS = ['ass', 'txt', 'srt']

NO_MERGE = 'none'
AUTO_MERGE = 'auto'
FORCE_MERGE = 'force'


def display_error(error_str):
    print(f'[ERROR] {error_str}')
    os._exit(1)


def display_warning(error_str):
    print(f'[WARNING] {error_str}')


def display_info(info_str):
    print(f'[INFO] {info_str}')


class Config:
    def __init__(self):
        import local_config
        self.merge = local_config.config.get('merge', 'auto')
        self.clean_mode = local_config.config.get('clean_mode', True)
        self.actor = local_config.config.get('actor', False)
        self.output_format = local_config.config.get('output_format', 'txt')
        self.add_spaces = local_config.config.get('add_spaces', False)
        self.ending_char = local_config.config.get('ending_char', '')
        self.output_path = None


class TapDialogue:
    def __init__(self, dialogue_line: str):
        parts = dialogue_line.split(',', 9)
        self.start, self.end = parts[1].strip(), parts[2].strip()
        self.text = parts[9].strip()
        self.pos_y = int(re.search(r'\\pos\(\d+,(\d+)\)', self.text).group(1))
        self.actor = '-1'

    def convert_full_half_width_characters(self):
        RAW = '（）！？１２３４５６７８９０ｑｗｅｒｔｙｕｉｏｐａｓｄｆｇｈｊｋｌｚｘｃｖｂｎｍＱＷＥＲＴＹＵＩＯＰＡＳＤＦＧＨＪＫＬＺＸＣＶＢＮＭ'\
            'ｧｱｨｲｩｳｪｴｫｵｶｷｸｹｺｻｼｽｾｿﾀﾁｯﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓｬﾔｭﾕｮﾖﾗﾘﾙﾚﾛﾜｦﾝｰ･'
        CONVERTED = '()!?1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'\
            'ァアィイゥウェエォオカキクケコサシスセソタチッツテトナニヌネノハヒフヘホマミムメモャヤュユョヨラリルレロワヲンー・'
        text = self.text.translate(str.maketrans(
            RAW, CONVERTED)).replace('ウﾞ', 'ヴ')
        self.text = (''.join(chr(ord(text[i]) + 1) if text[i+1] == 'ﾞ' else chr(ord(text[i]) + 2) if text[i+1] == 'ﾟ' else text[i] for i in range(0, len(text)-1)) +
                     text[-1]).replace('ﾞ', '').replace('ﾟ', '')
        return self

    def add_space(self) -> str:
        def is_whitespace(char: str) -> bool:
            return char in [' ', '\u3000', '\u2006']

        AN_PATTERN = r'[\u0021-\u00b6]|[\u00b8-\u00ff]|[\u0370-\u03ff]'
        CJK_PATTERN = r'[\u3040-\ufaff]'
        result = []
        for char in self.text:
            if re.match(CJK_PATTERN, char) and result and re.match(AN_PATTERN, result[-1]) and not is_whitespace(result[-1]):
                result.append('\u2006')
            elif re.match(AN_PATTERN, char) and result and re.match(CJK_PATTERN, result[-1]):
                result.append('\u2006')
            result.append(char)
        return ''.join(result)

    def clean_up_text(self):
        text = re.sub(r'{[^}]+}', '', self.text)  # 去除tag
        text = re.sub(r'\([^)]+\)', '', text)  # 去除括号
        text = re.sub(r'\[[^]]+\]', '', text)  # 去除外字
        # 去除冒号说话人
        if '：' in text and text.index('：') < 8:
            text = text[text.index('：')+1:]
        self.text = text
        return self

    def clean_trash(self):
        trash = ['', '\u3000', 'あわわ', 'あん', 'うぃ', 'うえぇ～ん', 'うお', 'うっわ',
                 'くぅ', 'くぅ～ん', 'ぐぬ', 'ぐぬぅ', 'ぐふ', 'すぅ', 'ぜぇ', 'ぬぁ',
                 'ぬおおお', 'はぁ', 'ひゃ', 'ウーム', 'ひゃあ', 'ふぎゃああ', 'ふぐ', 'ふむ', '・',
                 'へぇ', 'ほ～ぅ', 'むふ', 'わぁぁ', 'ん', 'んあ', 'んぐぐ', 'んはは', 'んん', 'んんぃ',
                 'ぬあ', 'ほふぅ', 'ほふ', 'ふひゃ', 'うりゃ']
        trash_re = [r'[フウ][ウゥフッーン]+', r'ふん(ふん)+', r'[アハワフウ][ッハァー]+', r'[うぐひふ][えぇ]+',
                    r'[ぐうふ][うぅ]+', r'([ぐうふわ]|うわ)[あぁ]+', r'[あは][あぁ][あぁ]+', r'ひ[いぃ]+', r'[エヘ][ヘッ]+',
                    r'ヒ[イィ]+', r'[うふ]ふ+', r'[クウグワ][ワオォァーッ]+', r'[うは]わ+ぁ*']
        trash_single = ['あ', 'あぁ', 'う', 'お', 'く', 'ぬ', 'は', 'ぐ',
                        'ひ', 'ふ', 'ぶ', 'へ', 'ほ', 'わ', 'ウ', 'ハ', 'ヒ', 'フ']
        text = re.sub(r'(？！|！？|？|！|\n)', r'\1　', self.text).strip('\u3000 ')
        elements = text.split('\u3000')
        test_case = list(element.strip('！？…～っッ') for element in elements)
        if all(single in trash or single in trash_single for single in test_case):
            self.text = ''
        else:
            # 筛选语气词，只删除头尾的
            del_list = []
            for del_i, case in enumerate(test_case):
                if case in trash or any(re.fullmatch(pattern, case) for pattern in trash_re):
                    del_list.append(del_i)
            for index in reversed([del_i for i, del_i in enumerate(
                    del_list) if i == del_i or len(del_list)-i == len(elements)-del_i]):
                elements.pop(index)
            self.text = re.sub(r'(？|！|\n)\u3000', r'\1',
                               '\u3000'.join(elements))
        return self


class TapAssParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.events = []
        self.y_spacing = 0
        self.actor_record = {}

    def parse(self):
        with open(self.file_path, 'r', encoding='utf-8_sig') as ass_file:
            for line in ass_file:
                if line.startswith('Dialogue:') and ',Rubi,' not in line:
                    tmp = TapDialogue(
                        line).convert_full_half_width_characters()
                    if tmp.text != '':
                        self.events.append(tmp)
                elif 'ResY:' in line:
                    res_y = int(re.search(r'ResY: ?(\d+)', line).group(1))
                    self.y_spacing = int(60*(res_y/540))
        return self

    def set_actor(self):
        none_actor_index = 1
        same_actor_flag = False
        for index, line in enumerate(self.events):
            # 说话人的三种标记方式：括号、冒号、颜色
            actor = None
            text_stripped = custom_replace(re.sub(r'{[^}]+}', '', line.text))

            # 获取具体说话人
            if text_stripped.startswith('(') and ')' in text_stripped:
                actor = re.search(r"\((.*?)\)", text_stripped).group(1)
            elif '：' in text_stripped and text_stripped.index('：') < 8:
                actor = text_stripped[:text_stripped.index('：')]

            color_match = re.search(
                r'\\pos[^}]+\\c&?([a-fhA-FH0-9]*?)[\\}]', line.text)
            if color_match:  # 根据颜色对应说话人
                color = color_match.group(1)
                if color not in self.actor_record:
                    self.actor_record[color] = actor or str(none_actor_index)
                    none_actor_index += 1
                elif not actor:
                    actor = self.actor_record[color]
            else:  # 根据括号或坐标对应说话人
                if same_actor_flag:
                    actor = self.events[index-1].actor
                text_stripped = re.sub(r'{[^}]+}', '', line.text)
                if text_stripped.startswith(('<', '＜', '《', '｟', '≪')):
                    same_actor_flag = True
                if text_stripped.endswith(('>', '＞', '》', '｠', '≫')):
                    same_actor_flag = False
                if not same_actor_flag and index > 0:
                    last_line = self.events[index-1]
                    if (line.start, line.end) == (last_line.start, last_line.end) and not '\\c&H' in last_line.text and abs(line.pos_y-last_line.pos_y) <= self.y_spacing:
                        actor = last_line.actor
                    else:
                        none_actor_index += 1
                        actor = str(none_actor_index)
                        none_actor_index -= int(text_stripped.endswith(('→', '➡'))
                                                and not same_actor_flag)
            line.actor = str(actor)

    def merge_duplicate_rows_by_time(self, mode=AUTO_MERGE):
        if mode == NO_MERGE:
            return self
        del_list = []
        if mode == FORCE_MERGE:
            for index, line in enumerate(self.events):
                if index == len(self.events)-1:
                    break
                nxt_line = self.events[index+1]
                if line.start == nxt_line.start and line.end == nxt_line.end:
                    if line.actor != nxt_line.actor and line.actor and nxt_line.actor:
                        nxt_line.actor = line.actor + '/' + nxt_line.actor
                        self.events[index +
                                    1].text = (line.text + '\n' + nxt_line.text)
                    else:
                        self.events[index +
                                    1].text = (line.text + '\u3000' + nxt_line.text)
                        nxt_line.actor = line.actor or nxt_line.actor
                    del_list.append(index)
        elif mode == AUTO_MERGE:
            for index, line in enumerate(self.events):
                if index == len(self.events)-1:
                    break
                next_line = self.events[index+1]
                if line.start == next_line.start and line.end == next_line.end:
                    if line.actor == next_line.actor:
                        self.events[index+1].text = (line.text + '\u3000' + next_line.text).replace(
                            '？\u3000', '？').replace('！\u3000', '！')
                        next_line.actor = line.actor
                        del_list.append(index)
        for index in reversed(del_list):
            self.events.pop(index)
        return self

    def write_txt(self, output_path: str, output_actor: bool = False, ending_char: str = ''):
        with open(output_path, 'w', encoding='utf-8') as output_file:
            for line in self.events:
                text = line.text.replace('\n', '\u3000')
                output_file.write(
                    f'[{line.actor}]\t{text}\n' if output_actor else f'{text}{ending_char}\n')

    def write_ass(self, output_path: str, output_actor: bool = False, ending_char: str = ''):
        ASS_HEADER = ('[Script Info]\n'
                      f'; Generated by Tap {SCRIPT_VERSION} (TV ASS Process)\n'
                      f'; GitHub: {GITHUB_LINK}\n'
                      'ScriptType: v4.00+\n'
                      'PlayResX: 1920\n'
                      'PlayResY: 1080\n\n'
                      '[V4+ Styles]\n'
                      'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n'
                      'Style: JP,Sarasa Gothic J Semibold,52,&H00FFFFFF,&H00FFFFFF,&H00141414,&H910E0807,0,0,0,0,100,100,0,0,1,1.6,0,2,30,30,15,1\n\n'
                      '[Events]\n'
                      'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n')
        with open(output_path, 'w', encoding='utf-8_sig') as output_file:
            output_file.write(ASS_HEADER)
            for line in self.events:
                text = line.text.replace('\n', '\\N')
                output_file.write(
                    f'Dialogue: 0,{line.start},{line.end},JP,{line.actor or "" if output_actor else ""},0,0,0,,{text}{ending_char}\n')

    def write_srt(self, output_path: str, output_actor: bool = False, ending_char: str = ''):
        with open(output_path, 'w', encoding='utf-8') as output_file:
            for i, line in enumerate(self.events):
                output_file.write(
                    '%d\n%s --> %s\n%s%s%s\n\n' % (i+1, f'0{line.start.replace(".", ",")}', f'0{line.end.replace(".",",")}',
                                                   f'{{{line.actor}}}' if output_actor and line.actor else '', line.text, ending_char))


def custom_replace(raw_text: str) -> str:
    for key, value in replace_dict.items():
        raw_text = raw_text.replace(key, value)
    for key, value in regular_ex.items():
        raw_text = re.sub(key, value, raw_text)
    return raw_text


def process_file(path: str):
    subs = TapAssParser(path).parse()
    subs.set_actor()
    subs.merge_duplicate_rows_by_time(local_config.merge)
    del_list = []
    for index, line in enumerate(subs.events):
        line.text = custom_replace(line.clean_up_text().text)
        if local_config.clean_mode:
            line.clean_trash()
        if line.text == '':
            del_list.append(index)
        elif local_config.add_spaces:
            line.add_space()
    for index in reversed(del_list):
        subs.events.pop(index)
    return subs


def argparse_config():
    from argparse import ArgumentParser
    global local_config
    local_config = Config()

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
    group_actor.set_defaults(actor=local_config.actor)

    group_clean = parser.add_mutually_exclusive_group(required=False)
    group_clean.add_argument(
        '--clean', '-c', dest='clean_mode', action='store_true', help='删除语气词')
    group_clean.add_argument(
        '--no-clean', '-cn', dest='clean_mode', action='store_false', help='不删除语气词')
    group_clean.set_defaults(clean_mode=local_config.clean_mode)

    group_merge = parser.add_mutually_exclusive_group(required=False)
    group_merge.add_argument(
        '--merge', '-m', dest='merge', action='store_const', const=AUTO_MERGE, help='合并时间重复行')
    group_merge.add_argument(
        '--no-merge', '-mn', dest='merge', action='store_const', const=NO_MERGE, help='不合并时间重复行')
    group_merge.add_argument(
        '--force-merge', '-mf', dest='merge', action='store_const', const=FORCE_MERGE, help='强制合并时间重复行')
    group_merge.set_defaults(merge=local_config.merge)

    group_space = parser.add_mutually_exclusive_group(required=False)
    group_space.add_argument(
        '--space', '-s', dest='add_space', action='store_true', help='中西文之间添加空格')
    group_space.add_argument(
        '--no-space', '-sn', dest='add_space', action='store_false', help='中西文之间不添加空格')
    group_space.set_defaults(add_space=local_config.add_spaces)

    args = parser.parse_args()
    for k, v in vars(args).items():
        if v != None:
            setattr(local_config, k, v)


def main():
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

    argparse_config()
    output_format = local_config.output_format
    output_dir_flag = False
    ass_files = get_ass_files(local_config.path)
    if len(ass_files) > 1 and local_config.output_path:
        parts = os.path.splitext(local_config.output_path)
        if parts[1]:
            display_warning(f'输出路径应为目录，将输出到原文件目录下。')
            local_config.output_path = None
        else:
            os.makedirs(local_config.output_path, exist_ok=True)
            output_dir_flag = True
            output_dir = parts[0]
    elif len(ass_files) == 1 and local_config.output_path:
        parts = os.path.splitext(local_config.output_path)
        if parts[1]:
            file_extension = parts[1][1:].lower()
            if os.path.realpath(local_config.output_path) == os.path.realpath(ass_files[0]):
                display_warning(f'输出路径不可与输入路径相同。')
                local_config.output_path = None
            if file_extension in SUPPORTED_EXTENSIONS:
                display_warning(f'将输出为 {file_extension} 格式。')
                output_format = parts[1][1:]
            else:
                display_warning(f'输出路径后缀名不符合要求，将输出为 {output_format} 格式。')
                local_config.output_path = parts[0]+local_config.output_format
        else:
            os.makedirs(local_config.output_path, exist_ok=True)
            output_dir_flag = True
            output_dir = parts[0]

    # display_info('当前配置')
    # for k, v in local_config.__dict__.items():
    #     display_info(f'{k}: {v}')
    for single_file in ass_files:
        if output_dir_flag:
            output_file = os.path.join(output_dir, os.path.basename(single_file))[
                :-4] + f'_processed.{output_format}'
        else:
            output_file = local_config.output_path or f'{single_file[:-4]}_processed.{output_format}'
        subs = process_file(single_file)
        exec(
            f'subs.write_{output_format}(output_file, local_config.actor, local_config.ending_char)')
        display_info(f'Done: {single_file}')


if __name__ == '__main__':
    main()
