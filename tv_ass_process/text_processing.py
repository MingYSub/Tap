import re

AN_RANGES = [(0x0021, 0x00B6), (0x00B8, 0x00FF), (0x0370, 0x03FF)]
CJK_RANGES = [(0x3040, 0xFAFF)]


def convert_full_half_width_characters(text) -> str:
    RAW = (
        "１２３４５６７８９０ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ"
        "ｧｱｨｲｩｳｪｴｫｵｶｷｸｹｺｻｼｽｾｿﾀﾁｯﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓｬﾔｭﾕｮﾖﾗﾘﾙﾚﾛﾜｦﾝｰ"
        "（）！？．％／＆＋＝"
        "･“”｢｣｡:"
    )
    CONVERTED = (
        "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "ァアィイゥウェエォオカキクケコサシスセソタチッツテトナニヌネノハヒフヘホマミムメモャヤュユョヨラリルレロワヲンー"
        "()!?.%/&+="
        "・「」「」。："
    )
    text = text.translate(str.maketrans(RAW, CONVERTED)).replace("ウﾞ", "ヴ")
    text += " "
    return "".join(
        chr(ord(text[i]) + "ﾞﾟ".find(text[i + 1]) + 1)
        for i in range(len(text) - 1)
        if text[i] not in ["ﾞ", "ﾟ"]
    )


def check_CJK_char(text) -> bool:
    return all(
        any(start <= ord(char) <= end for start, end in CJK_RANGES) for char in text
    )


def check_AN_char(text) -> bool:
    return all(
        any(start <= ord(char) <= end for start, end in AN_RANGES) for char in text
    )


def replace_spaces_between_AN(text) -> str:
    words = text.split("\u3000")

    for i in range(1, len(words)):
        words[i - 1] += (
            " " if check_AN_char(words[i - 1]) and check_AN_char(words[i]) else "\u3000"
        )

    return "".join(words)


def add_spaces(text, whitespace="\u2006") -> str:
    result = []
    last_char_type = "NULL"
    for char in text:
        if check_CJK_char(char):
            if last_char_type == "AN":
                result.append(whitespace)
            last_char_type = "CJK"
        elif check_AN_char(char):
            if last_char_type == "CJK":
                result.append(whitespace)
            last_char_type = "AN"
        else:
            last_char_type = "NULL"
        result.append(char)
    return "".join(result)


def clean_up_text(text) -> str:
    text = re.sub(r"{[^}]+}", "", text)  # 去除tag
    text = re.sub(r"\([^)]+\)", "", text)  # 去除括号
    text = re.sub(r"\[[^]]+\]", "", text)  # 去除外字
    # 去除冒号说话人
    if "：" in text and text.index("：") < 8:
        text = text[text.index("：") + 1 :]
    return text


def clean_trash(text) -> str:
    TRASH_STR = [
        "",
        "\u3000",
        "あん",
        "うえぇん",
        "うっわ",
        "くぅ",
        "くぅん",
        "ぐぬ",
        "ぐぬぅ",
        "ぐふ",
        "すぅ",
        "ぜぇ",
        "ぬぁ",
        "ぬおおお",
        "はぁ",
        "ウーム",
        "ふぐ",
        "・",
        "むふ",
        "ん",
        "んあ",
        "んぐぐ",
        "んはは",
        "んん",
        "んんぃ",
        "ぬあ",
        "クックックッ",
        "ゲコ",
        "どわ",
        "はむ",
    ]

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

    TRASH_SINGLE = [
        "あ",
        "あぁ",
        "う",
        "お",
        "く",
        "ぐ",
        "ぬ",
        "は",
        "ひ",
        "ふ",
        "ぶ",
        "へ",
        "ほ",
        "わ",
        "げ",
        "ひゃ",
        "ウ",
        "ハ",
        "ヒ",
        "フ",
        "ク",
        "ン",
    ]

    text = re.sub(r"(？！|！？|[？！\n])", r"\1　", text).strip("\u3000 ")
    elements = text.split("\u3000")
    test_case = list(re.sub("[！？…～っッ]", "", element) for element in elements)
    trash_flag = [
        (
            1
            if single in TRASH_SINGLE
            else (
                2
                if single in TRASH_STR
                else (
                    3
                    if any(re.fullmatch(pattern, single) for pattern in TRASH_RE)
                    else 0
                )
            )
        )
        for single in test_case
    ]
    if all(trash_flag):
        return ""
    # Filter out interjections at the beginning and end
    del_list = [
        index for index, value in enumerate(trash_flag) if value == 2 or value == 3
    ]
    for index in reversed(
        [
            del_i
            for i, del_i in enumerate(del_list)
            if i == del_i or len(del_list) - i == len(elements) - del_i
        ]
    ):
        elements.pop(index)
    text = re.sub(r"([？！\n])\u3000", r"\1", "\u3000".join(elements))
    return text


def adjust_repeated_syllables(text) -> str:
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

    # text = text.strip("\u3000 ")
    cases = text.strip("\u3000 ").split("\u3000")
    repeated_syllable = ""
    for index, case in enumerate(cases):
        case = case.rstrip("…っッ")
        if index > 0:
            if repeated_syllable:
                if check_repeated_syllable(repeated_syllable, case):
                    cases[index - 1] = cases[index - 1].rstrip("…っッ") + "… "
                else:
                    cases[index] = "\u3000" + cases[index]
            else:
                cases[index] = "\u3000" + cases[index]
        repeated_syllable = has_same_syllables(case)
    text = "".join(cases)
    return text
