from replace_dict import *
import re
import os

SCRIPT_VERSION = 'v0.2.1'
GITHUB_LINK = 'https://github.com/MingYSub/Tap'

SUPPORTED_EXTENSIONS = ['ass', 'txt', 'srt']


def display_error(error_str):
    print(f'[ERROR] {error_str}')
    os._exit()


def display_warning(error_str):
    print(f'[WARNING] {error_str}')


def display_info(info_str):
    print(f'[INFO] {info_str}')


def add_space(text) -> str:
    def is_whitespace(char: str) -> bool:
        return char in [' ', '\u3000', '\u2006']

    AN_pattern = r'[\u0021-\u00b6]|[\u00b8-\u00ff]|[\u0370-\u03ff]'
    CJK_pattern = r'[\u3040-\ufaff]'
    result = []
    for char in text:
        if re.match(CJK_pattern, char) and result and re.match(AN_pattern, result[-1]) and not is_whitespace(result[-1]):
            result.append('\u2006')
        elif re.match(AN_pattern, char) and result and re.match(CJK_pattern, result[-1]):
            result.append('\u2006')
        result.append(char)
    return ''.join(result)


def text_process(text) -> str:
    # 处理全半角
    RAW = '（）！？１２３４５６７８９０ｑｗｅｒｔｙｕｉｏｐａｓｄｆｇｈｊｋｌｚｘｃｖｂｎｍＱＷＥＲＴＹＵＩＯＰＡＳＤＦＧＨＪＫＬＺＸＣＶＢＮＭ'\
        'ｧｱｨｲｩｳｪｴｫｵｶｷｸｹｺｻｼｽｾｿﾀﾁｯﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓｬﾔｭﾕｮﾖﾗﾘﾙﾚﾛﾜｦﾝｰ･'
    CONVERTED = '()!?1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'\
        'ァアィイゥウェエォオカキクケコサシスセソタチッツテトナニヌネノハヒフヘホマミムメモャヤュユョヨラリルレロワヲンー・'
    text = text.translate(str.maketrans(RAW, CONVERTED)).replace('ウﾞ', 'ヴ')
    text = (''.join(chr(ord(text[i]) + 1) if text[i+1] == 'ﾞ' else chr(ord(text[i]) + 2) if text[i+1] == 'ﾟ' else text[i] for i in range(0, len(text)-1)) +
            text[-1]).replace('ﾞ', '').replace('ﾟ', '')
    text = re.sub(r'\[[^]]+\]', '', text)
    return text


class Config:
    def __init__(self):
        import local_config
        for k, v in local_config.config.items():
            setattr(self, k, v)


class TapDialogue:
    def __init__(self, dialogue_line: str, speaker_record: list):
        data = dialogue_line.split(',', 9)
        self.start, self.end = data[1].strip(), data[2].strip()
        self.text = text_process(data[9].strip())
        self.actor = None
        self._speaker_record = speaker_record
        self.set_actor()
        self.clean_up()
        global local_config

    def set_actor(self):
        # 说话人的三种标记方式：括号、冒号、颜色
        speaker = None
        text_stripped = custom_replace(re.sub(r'{[^}]+}', '', self.text))

        if text_stripped.startswith('(') and ')' in text_stripped:
            speaker = re.findall(re.compile(
                r"[(](.*?)[)]", re.S), text_stripped)[0]
        elif '：' in text_stripped and text_stripped.index('：') < 8:
            speaker = text_stripped[:text_stripped.index('：')]

        if '\c&H' in self.text:  # 根据颜色对应说话人
            color = self.text[self.text.index(
                '\c&H')+6:self.text.index('\c&H')+12]
            if color not in self._speaker_record:
                self._speaker_record[color] = speaker or len(
                    self._speaker_record)
            elif not speaker:
                speaker = self._speaker_record[color]

        self.actor = speaker

    def clean_up(self):
        text = re.sub(r'{[^}]+}', '', self.text)  # 去除tag
        text = custom_replace(text).strip('\u3000 ')
        text = re.sub(r'\([^)]+\)', '', text)  # 去除括号
        # 去除冒号说话人
        if '：' in text and text.index('：') < 8:
            text = text[text.index('：')+1:]
        self.text = text
        if local_config.clean_mode:
            trash = ['', '\u3000', 'あぁぁ', 'あああ', 'あわわ', 'あん', 'うあ', 'うああ', 'うぃ', 'うぅ', 'うぅぅ',
                     'うう', 'ううぅ', 'うぇ', 'うぇえ', 'うえ', 'うえぇ', 'うえぇ～ん', 'うお', 'うっわ', 'うわ',
                     'うわぁ', 'うわあ', 'くぅ', 'くぅ～ん', 'ぐぁ', 'ぐあ', 'ぐぅ', 'ぐえ', 'ぐえぇ', 'ぐぬ',
                     'ぐぬぅ', 'ぐふ', 'すぅ', 'ぜぇ', 'ぬぁ', 'ぬおおお', 'はぁ', 'ひぃ', 'ひいいぃ', 'ひゃ',
                     'ひゃあ', 'ふぁ', 'ふぅ', 'ふう', 'ふぇ', 'ふえ', 'ふぎゃああ', 'ふぐ', 'ふふ', 'ふむ', 'ふんふん',
                     'ふんふん', 'ふんふんふん', 'ふんふんふんふん', 'へぇ', 'ほ～ぅ', 'むふ', 'わぁぁ', 'ん', 'んあ',
                     'んぐぐ', 'んはは', 'んん', 'んんぃ', 'アッハッハハ', 'アッハハ', 'アハ', 'アハハ', 'アハハハ',
                     'ウゥ', 'ウウ', 'ウォー', 'ウオ', 'ウフ', 'ウフフ', 'ウフフン', 'ウワー', 'ウーム', 'ウーン',
                     'エヘ', 'エヘヘ', 'クフフ', 'ハァ', 'ハァァ', 'ハァハァ', 'ハハ', 'ハハハ', 'ヒィ', 'ヒィィ',
                     'フゥ', 'フッフ', 'フッフフ', 'フッフフフフ', 'フフ', 'フフッフ', 'フフフ', 'フフフフ', 'フフン',
                     'フフーン', 'フン', 'フーン', 'ヘッヘッヘッヘッヘ', 'ワッハッハ', 'ワッハッハッハ', 'ワン', '・',
                     'ぬあ']
            trash_single = ['あ', 'あぁ', 'う', 'お', 'く', 'ぬ', 'は', 'ぐ',
                            'ひ', 'ふ', 'ぶ', 'へ', 'ほ', 'わ', 'ウ', 'ハ', 'ヒ', 'フ']
            text = re.sub(r'(？！|！？|？|！)', r'\1　', text).strip('\u3000 ')
            elements = text.split('\u3000')
            test_case = list(element.strip('！？…～っッ') for element in elements)
            if all(single in trash or single in trash_single for single in test_case):
                self.text = ''
            else:
                # 筛选语气词，只删除头尾的
                del_list = [del_i for del_i, case in enumerate(
                    test_case) if case in trash]
                for index in reversed([del_i for i, del_i in enumerate(
                        del_list) if i == del_i or len(del_list)-i == len(elements)-del_i]):
                    elements.pop(index)
                self.text = re.sub(r'(？|！)\u3000', r'\1',
                                   '\u3000'.join(elements))
        if local_config.add_spaces:
            self.text = add_space(self.text)


class TapAssParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.events = []
        self.speaker_record = {}
        global local_config

    def parse(self):
        with open(self.file_path, 'r', encoding='utf-8_sig') as ass_file:
            self.events = [x for x in [TapDialogue(l, self.speaker_record) for l in ass_file if l.startswith(
                'Dialogue:') and ',Rubi,' not in l] if x.text != '']
        return self.events

    def write_txt(self, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as output_file:
            for line in self.events:
                output_file.write(
                    f'[{line.actor}]\t{line.text}\n' if local_config.actor else f'{line.text}\n')

    def write_ass(self, output_path: str):
        ass_header = ('[Script Info]\n'
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
            output_file.write(ass_header)
            for line in self.events:
                output_file.write(
                    f'Dialogue: 0,{line.start},{line.end},JP,{line.actor or "" if local_config.actor else ""},0,0,0,,{line.text}\n')

    def write_srt(self, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as output_file:
            for i, line in enumerate(self.events):
                output_file.write(
                    '%d\n%s --> %s\n%s%s\n\n' % (i+1, f'0{line.start.replace(".", ",")}', f'0{line.end.replace(".",",")}',
                                                 f'{{{line.actor}}}' if local_config.actor and line.actor else '', line.text))


def custom_replace(raw_text: str) -> str:
    for key, value in replace_dict.items():
        raw_text = raw_text.replace(key, value)
    for key, value in regular_ex.items():
        raw_text = re.sub(key, value, raw_text)
    return raw_text


def process_file(path: str):
    subs = TapAssParser(path)
    events = subs.parse()
    if local_config.merge:  # 合并
        del_list = []
        for index, line in enumerate(events):
            if index == len(events)-1:
                break
            next_line = events[index+1]
            if local_config.merge != 'force' and (line.actor == None or next_line.actor == None):
                continue
            if line.start == next_line.start and line.end == next_line.end and (line.actor == next_line.actor or local_config.merge == 'force'):
                events[index+1].text = (line.text + '\u3000' + next_line.text).replace(
                    '？\u3000', '？').replace('！\u3000', '！')
                del_list.append(index)
        for index in reversed(del_list):
            events.pop(index)
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
    parser.add_argument('--output', '-o', type=str, help='指定输出路径')

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
        '--merge', '-m', dest='merge', action='store_const', const='auto', help='合并时间重复行')
    group_merge.add_argument(
        '--no-merge', '-mn', dest='merge', action='store_const', const='none', help='不合并时间重复行')
    group_merge.add_argument(
        '--force-merge', '-mf', dest='merge', action='store_const', const='force', help='强制合并时间重复行')
    group_merge.set_defaults(merge=local_config.merge)

    group_space = parser.add_mutually_exclusive_group(required=False)
    group_space.add_argument(
        '--space', '-s', dest='add_space', action='store_true', help='中西文之间添加空格')
    group_space.add_argument(
        '--no-space', '-sn', dest='add_space', action='store_false', help='中西文之间不添加空格')
    group_space.set_defaults(add_space=local_config.add_spaces)

    args = parser.parse_args()
    if len(args.path) == 1 and os.path.isfile(args.path[0]) and not args.output_format and args.output and args.output.split('.')[-1].lower() in SUPPORTED_EXTENSIONS:
        args.output_format = args.output.split('.')[-1].lower()
    elif not args.output_format:
        args.output_format = local_config.output_format

    for k, v in vars(args).items():
        setattr(local_config, k, v)


def main():
    def get_ass_files(path: list) -> list:
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
                result.append(ass_files)
            else:
                display_warning(f'该路径不存在: {element}')
        return result

    argparse_config()
    # display_info('当前配置')
    # for k, v in local_config.__dict__.items():
    #     display_info(f'{k}: {v}')
    output_format = local_config.output_format.lower().strip('\'" ')
    if not (len(local_config.path) == 1 and os.path.isfile(local_config.path[0])) and local_config.output:
        display_warning('当前仅支持处理单文件时指定输出路径。')
        local_config.output = None

    for single_file in get_ass_files(local_config.path):
        output_file = local_config.output or f'{single_file[:-4]}_processed.{output_format}'
        subs = process_file(single_file)
        exec(f'subs.write_{output_format}(output_file)')
        display_info(f'Done: {single_file}')


if __name__ == '__main__':
    main()
