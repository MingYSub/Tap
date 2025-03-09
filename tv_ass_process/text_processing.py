import re

from .config import ConversionStrategy

AN_RANGES = ((0x0021, 0x00B6), (0x00B8, 0x00FF), (0x0370, 0x03FF))
CJK_RANGES = ((0x3040, 0xFAFF),)

HALF_KANA = "ｧｱｨｲｩｳｪｴｫｵｶｷｸｹｺｻｼｽｾｿﾀﾁｯﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓｬﾔｭﾕｮﾖﾗﾘﾙﾚﾛﾜｦﾝｰヮヰヱヵヶヽヾ･｢｣｡､"
FULL_KANA = "ァアィイゥウェエォオカキクケコサシスセソタチッツテトナニヌネノハヒフヘホマミムメモャヤュユョヨラリルレロワヲンーヮヰヱヵヶヽヾ・「」。、"
HALF_DIGIT = "0123456789"
FULL_DIGIT = "０１２３４５６７８９"
HALF_LETTER = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
FULL_LETTER = "ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"


class TransMap:
    HALF_FULL_KATAKANA_MAP = str.maketrans(HALF_KANA, FULL_KANA)
    FULL_HALF_DIGIT_MAP = str.maketrans(FULL_DIGIT, HALF_DIGIT)
    HALF_FULL_DIGIT_MAP = str.maketrans(HALF_DIGIT, FULL_DIGIT)
    FULL_HALF_LETTER_MAP = str.maketrans(FULL_LETTER, HALF_LETTER)
    HALF_FULL_LETTER_MAP = str.maketrans(HALF_LETTER, FULL_LETTER)


def convert_half_katakana(text) -> str:
    text = text.replace('ｶﾞ', 'ガ').replace('ｷﾞ', 'ギ').replace('ｸﾞ', 'グ').replace('ｹﾞ', 'ゲ').replace('ｺﾞ', 'ゴ')
    text = text.replace('ｻﾞ', 'ザ').replace('ｼﾞ', 'ジ').replace('ｽﾞ', 'ズ').replace('ｾﾞ', 'ゼ').replace('ｿﾞ', 'ゾ')
    text = text.replace('ﾀﾞ', 'ダ').replace('ﾁﾞ', 'ヂ').replace('ﾂﾞ', 'ヅ').replace('ﾃﾞ', 'デ').replace('ﾄﾞ', 'ド')
    text = text.replace('ﾊﾞ', 'バ').replace('ﾋﾞ', 'ビ').replace('ﾌﾞ', 'ブ').replace('ﾍﾞ', 'ベ').replace('ﾎﾞ', 'ボ')
    text = text.replace('ﾊﾟ', 'パ').replace('ﾋﾟ', 'ピ').replace('ﾌﾟ', 'プ').replace('ﾍﾟ', 'ペ').replace('ﾎﾟ', 'ポ')
    text = text.replace('ｳﾞ', 'ヴ')
    return text.translate(TransMap.HALF_FULL_KATAKANA_MAP)


def convert_half_full_chars(text, full_half_mapping, half_full_mapping, strategy) -> str:
    if strategy == ConversionStrategy.SKIP:
        return text
    elif strategy == ConversionStrategy.HALF:
        return text.translate(full_half_mapping)
    elif strategy == ConversionStrategy.FULL:
        return text.translate(half_full_mapping)
    elif strategy == ConversionStrategy.SINGLE_FULL:
        text = text.translate(full_half_mapping)
        text = re.sub(r"(?<!\d)(\d)(?!\d)", lambda m: m[1].translate(half_full_mapping), text)
        return text
    raise ValueError(f"Invalid conversion strategy: {strategy}")


def convert_half_full_numbers(text, strategy: ConversionStrategy = ConversionStrategy.HALF) -> str:
    return convert_half_full_chars(text, TransMap.FULL_HALF_DIGIT_MAP, TransMap.HALF_FULL_DIGIT_MAP, strategy)


def convert_half_full_letters(text, strategy: ConversionStrategy = ConversionStrategy.HALF) -> str:
    return convert_half_full_chars(text, TransMap.FULL_HALF_LETTER_MAP, TransMap.HALF_FULL_LETTER_MAP, strategy)


def fix_western_text(text: str) -> str:
    def replace(match):
        western_text = match.group(2).replace("\u3000", " ").replace("！", "!").replace("？", "?")
        return match.group(1) + western_text + match.group(3)

    text = re.sub(r"(^|\u3000)([0-9a-zA-Z？！\u3000]*)($|\u3000)", replace, text)
    return text


def cjk_spacing(text, space="\u2006") -> str:
    def is_cjk_char(text: str) -> bool:
        return all(any(start <= ord(char) <= end for start, end in CJK_RANGES) for char in text)

    def is_an_char(text: str) -> bool:
        return all(any(start <= ord(char) <= end for start, end in AN_RANGES) for char in text)

    result = []
    last_char_type = "NULL"
    for char in text:
        if is_cjk_char(char):
            if last_char_type == "AN":
                result.append(space)
            last_char_type = "CJK"
        elif is_an_char(char):
            if last_char_type == "CJK":
                result.append(space)
            last_char_type = "AN"
        else:
            last_char_type = "NULL"
        result.append(char)
    return "".join(result)


def clean_up_text(text) -> str:
    text = re.sub(r"{[^}]+}", "", text)  # 去除tag
    text = re.sub(r"\([^)]+\)", "", text)  # 去除括号
    text = re.sub(r"\[[^]]+]", "", text)  # 去除外字
    # 去除冒号说话人
    if "：" in text and text.index("：") < 8:
        text = text[text.index("：") + 1:]
    return text


def filter_interjections(text) -> str:
    TRASH_STR = ["", "\u3000", "あん", "うえぇん", "うっわ", "くぅ", "くぅん", "ぐぬ", "ぐぬぅ", "ぐふ", "すぅ", "ぜぇ",
                 "ぬぁ", "ぬおおお", "はぁ", "ウーム", "ふぐ", "むふ", "ん", "んあ", "んぐぐ", "んはは", "んん",
                 "んんぃ", "ぬあ", "クックックッ", "ゲコ", "どわ", "はむ", ]

    TRASH_RE = [
        r"[ウフブ][ゥウッフプンー]+",
        r"ふん(ふん)+",
        r"[アウハフワ][ァアウッハワ]+",
        r"[うぐひふ][ぇえ]+",
        r"[うぐふ][ぅうお]+",
        r"([うぐふ]|う)わ?[ぁあ]+",
        r"[あは][ぁあ][ぁあ]+",
        r"[うひ][ぃい]+",
        r"[エヘ][ッヘー]+",
        r"ヒ[ィイッヒー]+",
        r"[うふ]ふ+",
        r"[ウクグワ][ァォオグッワー]+",
        r"[うはほ][はわぁ]+",
        r"ン[ンフッ]+",
        r"ギ[イィ]+",
        r"(ふぎゃ|ぎゃあ|ひゃ|うりゃ|ふひゃ)[ぁあ]*",
        r"あ?わわ+[ぁあ]*",
        r"[ほホ](ふ[ぅゥ]*|[ぅゥ]+)",
    ]

    TRASH_SINGLE = ["あ", "あぁ", "う", "お", "く", "ぐ", "ぬ", "は", "ひ", "ふ", "ぶ", "へ", "ほ", "わ", "げ", "ひゃ",
                    "ウ", "ハ", "ヒ", "フ", "ク", "ン", ]

    text = re.sub(r"(？！|！？|[？！\n])", r"\1　", text).strip("\u3000 ")
    elements = text.split("\u3000")
    test_case = list(re.sub("[！？…～っッ]", "", element) for element in elements)
    trash_flag = [
        (
            1 if single in TRASH_SINGLE
            else 2 if single in TRASH_STR
            else 3 if any(re.fullmatch(pattern, single) for pattern in TRASH_RE)
            else 0
        )
        for single in test_case
    ]

    if all(trash_flag):
        return ""

    # Filter interjections at the beginning and end
    del_list = [index for index, value in enumerate(trash_flag) if value == 2 or value == 3]
    for index in reversed(
            [del_i for i, del_i in enumerate(del_list) if i == del_i or len(del_list) - i == len(elements) - del_i]):
        elements.pop(index)
    text = re.sub(r"([？！\n])\u3000", r"\1", "\u3000".join(elements))
    return text


def adjust_repeated_syllables(text, connector: str = "… ") -> str:
    def has_same_syllables(text: str) -> str:
        syllables = re.findall(r"[あ-んア-ヴ][ゃゅょァィゥェォャュョ]?", text)
        if not syllables or "".join(syllables) != text:
            return ""
        if all(kana == syllables[0] for kana in syllables):
            return syllables[0]
        return ""

    def check_repeated_syllable(syllable: str, text: str) -> bool:
        from .constants import REPEATED_SYLLABLES

        if text.startswith(syllable):
            return True
        if syllable in REPEATED_SYLLABLES:
            return any(text.startswith(kanji) for kanji in REPEATED_SYLLABLES[syllable])
        return False

    cases = text.split("\u3000")
    repeated_syllable = ""
    for index, case in enumerate(cases):
        case = case.rstrip("…っッ")
        if index > 0:
            if repeated_syllable:
                if check_repeated_syllable(repeated_syllable, case):
                    cases[index - 1] = cases[index - 1].rstrip("…っッ") + connector
                else:
                    cases[index] = "\u3000" + cases[index]
            else:
                cases[index] = "\u3000" + cases[index]
        repeated_syllable = has_same_syllables(case)
    text = "".join(cases)
    return text
