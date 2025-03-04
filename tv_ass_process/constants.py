SCRIPT_VERSION = "v1.0.0"
GITHUB_LINK = "https://github.com/MingYSub/Tap"

ASS_HEADER = (
    "[Script Info]\n"
    f"; Generated by Tap {SCRIPT_VERSION} (TV ASS Processor)\n"
    f"; GitHub: {GITHUB_LINK}\n"
    "ScriptType: v4.00+\n"
    "PlayResX: 1920\n"
    "PlayResY: 1080\n\n"
    "[V4+ Styles]\n"
    "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
    "Style: JP,Sarasa Gothic J Semibold,52,&H00FFFFFF,&H00FFFFFF,&H00141414,&H910E0807,0,0,0,0,100,100,0,0,1,1.6,0,2,30,30,15,1\n\n"
    "[Events]\n"
    "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
)

REPEATED_SYLLABLES = {
    "あ": (
        "危", "遊", "後", "阿呆", "当", "朝", "明", "足", "熱", "頭", "甘", "青", "蒼", "秋", "杏", "東", "飛", "愛",
        "安",
        "葵", "有", "茜", "新", "天"
    ),
    "い": ("1", "一", "5", "五", "今", "行", "痛", "言", "嫌", "伊", "幾", "井"),
    "う": ("嬉", "旨", "上手", "美味", "歌", "嘘", "後", "诗", "宇"),
    "え": ("笑顔",),
    "お": ("同", "美味", "思", "想", "遅", "俺", "温", "重", "起", "落", "大", "終", "男", "女", "面白",),
    "か": (
    "彼", "可", "格", "母", "体", "身体", "完", "構", "必", "風", "顔", "考", "軽", "帰", "川", "加", "佳", "華"),
    "き": ("貴", "君", "聞", "気", "来", "緊", "切", "昨日", "奇", "決", "喜", "木"),
    "く": ("暗", "食", "熊", "国", "口", "悔", "黒", "久", "狂", "空"),
    "け": ("結", "決"),
    "こ": ("怖", "此", "子", "今", "心", "高", "言葉", "告", "答", "校", "恋", "小", "後",),
    "さ": ("3", "三", "最", "流石", "先", "寂", "更", "早速", "寒", "探", "捜", "桜", "坂", "佐", "崎"),
    "し": ("4", "四", "幸", "心", "死", "新", "真", "知", "失", "師", "白", "志", "椎"),
    "す": ("好", "凄", "少", "素", "墨"),
    "せ": ("世", "背", "先", "正"),
    "そ": ("空", "其", "素", "祖"),
    "た": ("楽", "確か", "食", "高", "例", "助", "多", "大", "度", "小鳥遊", "贵"),
    "ち": ("違", "父", "近", "千"),
    "つ": ("次", "月", "潰", "強", "使"),
    "て": ("手", "天", "店"),
    "と": ("友", "父", "隣", "特", "当", "時", "智"),
    "な": ("7", "七", "何", "泣", "内", "夏", "中", "奈", "長", "名", "菜"),
    "に": ("2", "二", "兄", "虹", "仁", "西"),
    "ぬ": ("温", "抜"),
    "ね": ("寝", "猫", "姉"),
    "の": ("乗", "飲"),
    "は": ("8", "八", "二", "初", "早", "速", "母", "話", "離", "放", "始", "花", "春", "遥", "羽"),
    "ひ": ("1", "一", "姫", "久", "引", "光", "日", "必", "非", "火", "秘", "冷", "平", "阳"),
    "ふ": ("2", "二", "普", "不", "冬", "藤"),
    "へ": ("変", "返"),
    "ほ": ("服", "本", "他", "歩", "放", "欲", "星"),
    "ま": ("万", "待", "魔", "毎", "真", "間", "街", "迷", "前", "松", "漫", "舞", "町"),
    "み": ("皆", "水", "見", "三", "美", "耳", "未", "宮"),
    "む": ("無", "胸", "向", "夢"),
    "め": ("滅茶", "目", "迷", "珍", "恵"),
    "も": ("桃", "申", "問", "持", "戻"),
    "や": ("優", "安", "奴", "山", "宿", "八"),
    "ゆ": ("夢", "雪", "由", "有", "優", "唯", "結"),
    "よ": ("4", "四", "良", "弱", "宜", "夜"),
    "ら": ("来", "楽", "良", "羅", "裸"),
    "り": ("理", "利", "梨", "六"),
    "る": ("瑠",),
    "れ": ("連", "礼", "恋", "例", "麗"),
    "ろ": ("6", "六"),
    "わ": ("私", "我", "分", "悪", "忘", "笑"),
    "が": ("我慢", "頑", "学"),
    "ぎ": ("義", "技"),
    "ぐ": ("愚", "具"),
    "げ": ("下", "限"),
    "ご": ("5", "五", "御", "後"),
    "ざ": ("雑", "罪"),
    "じ": ("時", "爺", "次", "実", "地", "自"),
    "ず": ("狡", "随"),
    "ぜ": ("絶", "全", "是非"),
    "ぞ": (),
    "だ": ("大", "駄", "誰"),
    "ぢ": (),
    "づ": (),
    "で": ("出",),
    "ど": (),
    "ば": ("馬鹿",),
    "び": (),
    "ぶ": (),
    "べ": ("別",),
    "ぼ": ("僕",),
    "ぱ": (),
    "ぴ": (),
    "ぷ": (),
    "ぺ": (),
    "ぽ": (),
    "きゃ": ("客",),
    "きゅ": ("9", "九", "急"),
    "きょ": ("今日", "京"),
    "しゃ": ("喋",),
    "しゅ": (),
    "しょ": ("正直", "小", "初"),
    "じゃ": (),
    "じゅ": ("1", "十"),
    "じょ": ("女", "上手"),
    "ちゃ": (),
    "ちゅ": ("中",),
    "ちょ": ("超",),
    "にゃ": (),
    "にゅ": ("入",),
    "にょ": (),
    "ひゃ": ("1", "百"),
    "ひょ": (),
    "みょ": (),
    "りゃ": (),
    "りゅ": (),
    "りょ": ("了解",),
}
