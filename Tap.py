import re
import json
import os
import sys

script_version = 'v0.01'
GitHub_link = 'https://github.com/MingYSub/Tap'

replace_dict = {
    '\u200e': '',
    '\\N': '',
    ' “': '「',
    '” ': '」',
    '“': '「',
    '”': '」',
    ' ｢': '「',
    '｣ ': '」',
    '｢': '「',
    '｣': '」',
    '「\u3000': '「',
    '\u3000」': '」',
    '!?': '？',
    '!!': '！',
    '?': '？',
    '!': '！',
    '～！': '～',
    '～？': '～',
    ' ': '\u3000',
    '？\u3000': '？',
    '！\u3000': '！',
    '！\u3000': '！',
    '…｡': '…',
    '…。': '…',
    '｡\u3000': '\u3000',
    '。\u3000': '\u3000',
    '｡': '\u3000',
    '。': '\u3000',
    '《': '',
    '》': '',
    ':': '：',
    '<': '',
    '>': '',
    '＜': '',
    '＞': '',
    '→': '',
    '((': '',
    '))': '',
    '♬': '',
    '⚟': '',
    '📱': '',
    '🔊': '',
    '}・': '}',
    'ね？': 'ね',
    'かな？': 'かな',
    'ですか？': 'ですか',
}


class Config:
    def __init__(self, config_file_path: str = ''):
        self._config_file_path = config_file_path or (os.path.join(
            os.path.dirname(os.path.realpath(sys.argv[0])), 'user_config.json'))
        print(self._config_file_path)
        self.default_config = {
            'merge': True,
            'clean_mode': True,
            'fix_mode': True,
            'actor': False,
            'output_format': 'txt',
        }
        self.config = self.load_config(self._config_file_path)

    def load_config(self, config_file_path: str = ''):
        config_file_path = config_file_path or self._config_file_path
        if os.path.exists(config_file_path):
            with open(config_file_path, 'r', encoding='utf-8') as f:
                try:
                    config = json.load(f)
                    for i in [k for k in config.keys() if k not in self.default_config.keys()]:
                        config.pop(i)  # 去除无效配置
                except json.JSONDecodeError:
                    config = {}
        else:
            config = {}

        for k, v in self.default_config.items():
            config.setdefault(k, v)

        self.write_config(config)
        config['replace_dict'] = replace_dict
        for k, v in config.items():
            setattr(self, k, v)
        return config

    def write_config(self, config):
        with open(self._config_file_path, "w", encoding='utf-8') as f:
            json.dump(config, f, indent='\t')


class TapDialogue:
    def __init__(self, dialogue_line: str, subs_parser):
        data = dialogue_line.split(',', 9)
        self.start, self.end = data[1].strip(), data[2].strip()
        self.text = data[9].strip()
        self.actor = None
        self._speaker_record = subs_parser.speaker_record
        self._config = subs_parser.config
        self.text_process()

    def text_process(self):
        def character_convert(raw_text: str) -> str:  # 处理全半角
            RAW = '（）！？１２３４５６７８９０ｑｗｅｒｔｙｕｉｏｐａｓｄｆｇｈｊｋｌｚｘｃｖｂｎｍＱＷＥＲＴＹＵＩＯＰＡＳＤＦＧＨＪＫＬＺＸＣＶＢＮＭ'\
                'ｧｱｨｲｩｳｪｴｫｵｶｷｸｹｺｻｼｽｾｿﾀﾁｯﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓｬﾔｭﾕｮﾖﾗﾘﾙﾚﾛﾜｦﾝｰ･'
            CONVERTED = '()!?1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'\
                'ァアィイゥウェエォオカキクケコサシスセソタチッツテトナニヌネノハヒフヘホマミムメモャヤュユョヨラリルレロワヲンー・'
            text = raw_text.translate(str.maketrans(
                RAW, CONVERTED)).replace('ウﾞ', 'ヴ')
            return (''.join(chr(ord(text[i]) + 1) if text[i+1] == 'ﾞ' else chr(ord(text[i]) + 2) if text[i+1] == 'ﾟ' else text[i] for i in range(0, len(text)-1)) +
                    text[-1]).replace('ﾞ', '').replace('ﾟ', '')

        self.text = character_convert(self.text)
        if self._config['fix_mode']:
            self.text = re.sub(r'\[[^]]+\]', '', self.text)

        self.set_actor()
        self.clean_up()

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
                '\c&H')+4:self.text.index('\c&H')+10]
            if color not in self._speaker_record:
                self._speaker_record[color] = speaker or len(
                    self._speaker_record)
            elif not speaker:
                speaker = self._speaker_record[color]

        self.actor = speaker

    def clean_up(self) -> str:
        def del_actor(raw_text: str):
            if '：' in raw_text and raw_text.index('：') < 8:
                return raw_text[raw_text.index('：')+1:]
            return raw_text

        def del_trash(raw_text: str) -> str:  # 清理语气词
            trash = ['', '・', '\u3000', 'あん', 'あああ', 'あわわ', 'アハ', 'アハハ', 'アッハハ', 'ワッハッハ', 'アッハッハハ',
                     'うあ', 'うぃ', 'うぅ', 'ううぅ', 'うう', 'うぇ', 'うああ', 'うわあ', 'うえぇ', 'うぇえ', 'うえ', 'うわ', 'うわぁ', 'うっわ',
                     'うえぇ～ん', 'うお', 'エヘ', 'エヘヘ', 'ウフ', 'ウフフ', 'ウフフン', 'ヘッヘッヘッヘッヘ',
                     'くぅ', 'クフフ', 'くぅ～ん', 'ぐぅ', 'ぐぁ', 'ぐえぇ', 'ぐえ', 'ぐふ', 'ぐぬ', 'ぐぬぅ',
                     'すぅ', 'ぜぇ', 'ハハ', 'ハハハ',
                     'フン', 'フフ', 'フッフ', 'フフフ', 'フッフフ', 'フフッフ', 'フフン', 'フフフフ', 'フッフフフフ',
                     'ハァ', 'ハァハァ', 'はぁ', 'ひぃ', 'ひゃあ', 'ひゃ', 'ひいいぃ',
                     'ふぁ', 'ふぅ', 'ふえ', 'ふぇ', 'ふう', 'ふぐ', 'ふむ', 'ふふ', 'へぇ',
                     'ぬおおお', 'ふんふん', 'ふんふん', 'ふんふんふん', 'ふんふんふんふん',
                     'ワン', 'ワッハッハッハ', 'むふ', 'ふぎゃああ',
                     'ん', 'んあ', 'んはは', 'んぐぐ', 'んん', 'んんぃ']
            trash_single = ['う', 'フ', 'く', 'ぶ', 'お', 'あ',
                            'ふ', 'へ', 'ほ', 'わ', 'ぬ', 'ハ', 'は', 'ひ']
            # raw_text = re.sub(r'[？！]', lambda x: x.group() + '\u3000', raw_text).strip('\u3000 ')
            raw_text = custom_replace(
                raw_text, {'？': '？\u3000', '！': '！\u3000'})
            elements = raw_text.split('\u3000')
            test_case = list(element.strip('！？…～っッ') for element in elements)

            if all(single in trash or single in trash_single for single in test_case):
                return ''
            # 筛选语气词，只删除头尾的
            del_list = [del_i for del_i, case in enumerate(
                test_case) if case in trash]
            for index in reversed([del_i for i, del_i in enumerate(
                    del_list) if i == del_i or len(del_list)-i == len(elements)-del_i]):
                elements.pop(index)

            return custom_replace('\u3000'.join(elements), {'？\u3000': '？', '！\u3000': '！'})

        raw_text = re.sub(r'{[^}]+}', '', self.text)  # 去除tag
        raw_text = custom_replace(raw_text).strip('\u3000 ')
        raw_text = re.sub(r'\([^)]+\)', '', raw_text)  # 去除括号
        raw_text = del_actor(raw_text)

        self.text = del_trash(
            raw_text) if self._config['clean_mode'] else raw_text


class TapAssParser:
    def __init__(self, file_path: str, config: dict):
        self.file_path = file_path
        self.events = []
        self.speaker_record = {}
        self.config = config

    def parse(self):
        with open(self.file_path, 'r', encoding='utf-8_sig') as ass_file:
            self.events = [x for x in [TapDialogue(l, self) for l in ass_file if l.startswith(
                'Dialogue:') and ',Rubi,' not in l] if x.text != '']
        return self.events

    def write_txt(self, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as output_file:
            for line in self.events:
                output_file.write(
                    f'[{line.actor}]\t{line.text}\n' if self.config['actor'] else f'{line.text}\n')

    def write_ass(self, output_path: str):
        ass_header = ('[Script Info]\n'
                      f'; Generated by TAP {script_version} (TV ASS Process)\n'
                      f'; GitHub: {GitHub_link}\n'
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
                    f'Dialogue: 0,{line.start},{line.end},JP,{line.actor or "" if self.config["actor"] else ""},0,0,0,,{line.text}\n')

    def write_srt(self, output_path: str):
        # line_template = ('start_time --> end_time\n')
        with open(output_path, 'w', encoding='utf-8') as output_file:
            # output_file.write('\n\n'.join(
            #     f'{index+1}\n' +
            #     custom_replace(line_template, {'start_time': f'0{x.start.replace(".", ",")}',
            #                                    'end_time': f'0{x.end.replace(".",",")}'}) +
            #     (f'{{{x.actor}}}' if self.config['actor'] and x.actor else '') + x.text for index, x in enumerate(self.events)))
            for i, line in enumerate(self.events):
                output_file.write(
                    '%d\n%s --> %s\n%s%s\n\n' % (i+1, f'0{line.start.replace(".", ",")}', f'0{line.end.replace(".",",")}',
                                                 f'{{{line.actor}}}' if self.config['actor'] and line.actor else '', line.text))


def custom_replace(raw_text: str, replace_dict: dict = replace_dict) -> str:  # 自定义替换
    for key, value in replace_dict.items():
        raw_text = raw_text.replace(key, value)
    regular_ex = {
        r'・$': '',
        r'^・': '',
    }
    for key, value in regular_ex.items():
        raw_text = re.sub(key, value, raw_text)
    return raw_text


def process_file(path: str, config: dict):
    subs = TapAssParser(path, config)
    events = subs.parse()
    if config['merge']:  # 合并
        del_list = []
        for index, line in enumerate(events):
            if index == len(events)-1:
                break
            next_line = events[index+1]
            if line.actor == None or next_line.actor == None:
                continue
            if line.start == next_line.start and line.end == next_line.end and line.actor == next_line.actor:
                events[index+1].text = (line.text + '\u3000' + next_line.text).replace(
                    '？\u3000', '？').replace('！\u3000', '！')
                del_list.append(index)
        for index in reversed(del_list):
            events.pop(index)
    return subs


def argparse_config() -> dict:
    from argparse import ArgumentParser
    json_config = Config()

    parser = ArgumentParser(
        description=f'Tap {script_version} (TV Ass Process) | 处理从 TV 提取的 ASS 字幕')
    parser.add_argument('path', type=str, help='输入路径（支持文件和文件夹）')
    parser.add_argument('--format', dest='output_format',
                        type=str, help='指定输出格式')
    parser.add_argument('--output', '-o', type=str, help='指定输出路径')

    group_actor = parser.add_mutually_exclusive_group(required=False)
    group_actor.add_argument(
        '--actor', '-a', dest='actor', action='store_true', help='输出说话人')
    group_actor.add_argument(
        '--no-actor', '-an', dest='actor', action='store_false', help='不输出说话人')
    group_actor.set_defaults(actor=json_config.actor)

    group_fix = parser.add_mutually_exclusive_group(required=False)
    group_fix.add_argument('--fix', dest='fix_mode',
                           action='store_true', help='修复 Captain2Ass 可能出现的 Bug（去除中括号）')
    group_fix.add_argument('--no-fix', dest='fix_mode',
                           action='store_false', help='不修复 Captain2Ass 可能出现的 Bug')
    group_fix.set_defaults(fix_mode=json_config.fix_mode)

    group_clean = parser.add_mutually_exclusive_group(required=False)
    group_clean.add_argument(
        '--clean', '-c', dest='clean_mode', action='store_true', help='删除语气词')
    group_clean.add_argument(
        '--no-clean', '-cn', dest='clean_mode', action='store_false', help='不删除语气词')
    group_clean.set_defaults(clean_mode=json_config.clean_mode)

    group_clean = parser.add_mutually_exclusive_group(required=False)
    group_clean.add_argument(
        '--merge', '-m', dest='merge', action='store_true', help='合并时间重复行')
    group_clean.add_argument(
        '--no-merge', '-mn', dest='merge', action='store_false', help='不合并时间重复行')
    group_clean.set_defaults(merge=json_config.merge)

    args = parser.parse_args()
    if os.path.isfile(args.path) and not args.output_format and args.output and args.output.split('.')[-1].lower() in ['ass', 'txt', 'srt']:
        args.output_format = args.output.split('.')[-1].lower()
    elif not args.output_format:
        args.output_format = json_config.config['output_format']

    return {**json_config.config, **vars(args)}


def main():
    def get_ass_files(path: str) -> list:
        if os.path.isfile(path):
            if path.endswith('.ass'):
                return [path]
            else:
                raise Exception('所选文件不是 ass 文件。\nNot an .ass file.')
        elif os.path.isdir(path):
            ass_files = [
                path+'\\' + file for file in os.listdir(path) if file.endswith('.ass') and not file.endswith('_processed.ass')]
            return ass_files
        else:
            raise Exception('输入路径的路径无效。\nThe path is not a file or directory.')

    local_config = argparse_config()
    output_format = local_config['output_format'].lower().strip('\'" ')
    if output_format not in ['ass', 'txt', 'srt']:
        raise Exception(
            '指定输出格式错误，目前仅支持ass、txt 和 srt。\nUnsupported output format. Only support ass, txt or srt now.')
    if os.path.isdir(local_config['path']) and local_config['output']:
        raise Exception('当前仅支持处理单文件时指定输出路径。')

    for single_file in get_ass_files(local_config['path'].strip('\'" ')):
        output_file = local_config['output'] or f'{single_file[:-4]}_processed.{output_format}'
        subs = process_file(single_file, local_config)
        exec(f'subs.write_{output_format}(output_file)')
        print(f'Done: {single_file}')


if __name__ == '__main__':
    main()
