# 示例：'aaa': 'bbb'

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
    '｡': '。',
    '「\u3000': '「',
    '\u3000」': '」',
    '?': '？',
    '!': '！',
    ' ': '\u3000',
    '？\u3000': '？',
    '！\u3000': '！',
    '…。': '…',
    '。\u3000': '\u3000',
    '。': '\u3000',
    '《': '',
    '》': '',
    '≪': '',
    '<': '',
    '>': '',
    '＜': '',
    '＞': '',
    ':': '：',
    '→': '',
    '((': '',
    '))': '',
    '♬': '',
    '⚟': '',
    '➡': '',
    '📱': '',
    '☎': '',
    '🔊': '',
    '｟': '',
    '｠': '',
    '}・': '}',
}

# 正则表达式替换
regular_ex = {
    r'・$': '',
    r'^・': '',
}