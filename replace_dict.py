# 示例：'替换前': '替换后'

replace_dict = {
    '\u200e': '',
    '\\N': '',
    '“': '「',
    '”': '」',
    '｢': '「',
    '｣': '」',
    '｡': '。',
    ':': '：',
    '?': '？',
    '!': '！',
    '％': '%',
    ' ': '\u3000',
    '「\u3000': '「',
    '\u3000」': '」',
    '？\u3000': '？',
    '！\u3000': '！',
    '…。': '…',
    '。\u3000': '\u3000',
    '。\n': '\n',
    '。': '\u3000',
    '}・': '}',
    '《': '',
    '》': '',
    '≪': '',
    '≫': '',
    '<': '',
    '>': '',
    '＜': '',
    '＞': '',
    '((': '',
    '))': '',
    '→': '',
    '➡': '',
    '♬': '',
    '⚟': '',
    '📱': '',
    '☎': '',
    '🔊': '',
    '｟': '',
    '｠': '',
    '📺': '',
    '🎤': '',
}

# 正则表达式替换
regular_ex = {
    r'・$': '',
    r'^・': '',
}
