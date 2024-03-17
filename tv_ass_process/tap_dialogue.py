import re
from .constants import CHARS_TO_DELETE, REPLACEMENT_DICT, REPEATED_SYLLABLES
from .constants import TRASH_STR, TRASH_RE, TRASH_SINGLE


class TapDialogue:
    def __init__(self, dialogue_line: str):
        parts = dialogue_line.split(',', 9)
        self.start, self.end = parts[1].strip(), parts[2].strip()
        self.text = parts[9].strip()

        pos_match = re.search(r'\\pos\(\d+,(\d+)\)', self.text)
        self.pos_y = int(pos_match.group(1)) if pos_match else 0

        self.actor = '-1'

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

    def convert_full_half_width_characters(self) -> 'TapDialogue':
        RAW = '（）！？１２３４５６７８９０ｑｗｅｒｔｙｕｉｏｐａｓｄｆｇｈｊｋｌｚｘｃｖｂｎｍＱＷＥＲＴＹＵＩＯＰＡＳＤＦＧＨＪＫＬＺＸＣＶＢＮＭ'\
            'ｧｱｨｲｩｳｪｴｫｵｶｷｸｹｺｻｼｽｾｿﾀﾁｯﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓｬﾔｭﾕｮﾖﾗﾘﾙﾚﾛﾜｦﾝｰ･'
        CONVERTED = '()!?1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'\
            'ァアィイゥウェエォオカキクケコサシスセソタチッツテトナニヌネノハヒフヘホマミムメモャヤュユョヨラリルレロワヲンー・'
        text = self.text.translate(str.maketrans(
            RAW, CONVERTED)).replace('ウﾞ', 'ヴ')
        result = ''
        for i in range(len(text)-1):
            if text[i+1] == 'ﾞ':
                result += chr(ord(text[i]) + 1)
            elif text[i+1] == 'ﾟ':
                result += chr(ord(text[i]) + 2)
            elif text[i] not in ['ﾞ', 'ﾟ']:
                result += text[i]
        self.text = result + text[-1]
        return self

    def add_space(self, whitespace='\u2006') -> 'TapDialogue':
        import unicodedata

        result = []
        last_char_type = 'NULL'

        for char in self.text:
            char_name = unicodedata.name(char)
            if char_name.startswith(('CJK', 'HIRAGANA', 'KATAKANA')):
                if last_char_type == 'AN':
                    result.append(whitespace)
                last_char_type = 'CJK'
            elif char_name.startswith(('LATIN', 'DIGIT')):
                if last_char_type == 'CJK':
                    result.append(whitespace)
                last_char_type = 'AN'
            else:
                last_char_type = 'NULL'
            result.append(char)

        self.text = ''.join(result)

        return self

    def clean_up_text(self) -> 'TapDialogue':
        text = re.sub(r'{[^}]+}', '', self.text)  # 去除tag
        text = re.sub(r'\([^)]+\)', '', text)  # 去除括号
        text = re.sub(r'\[[^]]+\]', '', text)  # 去除外字
        # 去除冒号说话人
        text = text.replace(':', '：')
        if '：' in text and text.index('：') < 8:
            text = text[text.index('：')+1:]
        self.text = text
        return self

    def clean_trash(self) -> 'TapDialogue':
        text = re.sub(r'(？！|！？|？|！|\n)', r'\1　', self.text).strip('\u3000 ')
        elements = text.split('\u3000')
        test_case = list(element.strip('！？…～っッ') for element in elements)

        trash_flag = [1 if single in TRASH_SINGLE else
                      2 if single in TRASH_STR else
                      3 if any(re.fullmatch(pattern, single) for pattern in TRASH_RE) else
                      0 for single in test_case]

        if all(trash_flag):
            self.text = ''
        else:
            # Filter out interjections at the beginning and end
            del_list = [index for index, value in enumerate(
                trash_flag) if value == 2 or value == 3]
            for index in reversed([del_i for i, del_i in enumerate(del_list) if i == del_i or len(del_list)-i == len(elements)-del_i]):
                elements.pop(index)
            self.text = re.sub(r'(？|！|\n)\u3000', r'\1',
                               '\u3000'.join(elements))

        return self

    def adjust_repeated_syllables(self) -> 'TapDialogue':
        def extract_kana(text: str) -> list:
            return re.findall(r'[あ-んア-ヴ][ゃゅょァィゥェォャュョ]?', text)

        def has_same_syllables(text: str) -> str:
            syllables = extract_kana(text)
            if not syllables or ''.join(syllables) != text:
                return ''
            if all(kana == syllables[0] for kana in syllables):
                return syllables[0]
            return ''

        def check_repeated_syllable(syllable: str, text: str) -> bool:
            if text.startswith(syllable):
                return True
            if syllable in REPEATED_SYLLABLES:
                return any(text.startswith(kanji) for kanji in REPEATED_SYLLABLES[syllable])
            return False

        text = re.sub(r'(？！|！？|？|！|\n)', r'\1　', self.text).strip('\u3000 ')
        cases = text.split('\u3000')
        repeated_syllable = ''

        for index, case in enumerate(cases):
            case = case.rstrip('…っッ')
            if index > 0:
                if repeated_syllable:
                    if check_repeated_syllable(repeated_syllable, case):
                        cases[index-1] = cases[index-1].rstrip('…っッ') + '… '
                    else:
                        cases[index] = '\u3000'+cases[index]
                else:
                    cases[index] = '\u3000'+cases[index]

            repeated_syllable = has_same_syllables(case)

        self.text = re.sub(r'(？|！)\u3000', r'\1', ''.join(cases))
        return self
