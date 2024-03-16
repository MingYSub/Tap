# Tap (TV ASS Process)
处理从 TV 提取的 ASS 字幕的脚本。

## 特性
- 去除位置、颜色等信息
- 半角片假名转为全角
- 全角英数转为半角
- 合并时间重复行
- 删除外字（`[外:xxx]`，可能误伤极少字）
- 输出 txt、ass 和 srt 格式
- 输出说话人
- 去除语气词
- 批量转换单文件夹下的所有 ass 文件
- 中西文之间添加六分之一空格（U+2006）
- 输出时行尾追加字符
- 整理重复音节

## 用法
### Windows
可直接将提取出的 ASS 文件拖到脚本上，会自动读取配置文件运行。

### 命令行
```
usage: Tap.py [-h] [--format {ass,txt,srt}] [--output OUTPUT_PATH]
              [--actor | --no-actor]
              [--clean | --no-clean]
              [--merge | --no-merge | --force-merge]
              [--space | --no-space]
              [--adjust-repeated-syllables | --no-adjust-repeated-syllables]
              path [path ...]

positional arguments:
  path                  输入路径（支持文件和文件夹）

optional arguments:
  -h, --help            show this help message and exit
  --format {ass,txt,srt}
                        指定输出格式
  --output OUTPUT_PATH, -o OUTPUT_PATH
                        指定输出路径
  --actor, -a           输出说话人
  --no-actor, -an       不输出说话人
  --clean, -c           删除语气词
  --no-clean, -cn       不删除语气词
  --merge, -m           合并时间重复行
  --no-merge, -mn       不合并时间重复行
  --force-merge, -mf    强制合并时间重复行
  --space, -s           中西文之间添加空格
  --no-space, -sn       中西文之间不添加空格
  --adjust-repeated-syllables, -rs
                        整理重复音节
  --no-adjust-repeated-syllables, -rsn
                        不整理重复音节
```

## 配置文件
以下为默认配置文件的注释，请不要向文件添加注释。
```json
{
    "actor": false,  // 输出说话人，可填: true false，注意没有引号
    "add_spaces": true,  // 中西文之间添加六分之一空格（U+2006），可填: true false
    "adjust_repeated_syllables": true,  // 整理重复音节，可填: true false
    "clean_mode": true,  // 删除语气词，可填: true false
    "ending_char": "",  // 输出时行尾添加的字符，可填字符（串）
    "merge": "auto",  // 合并时间重复行，可填: "none" "auto" "force"
    "output_format": "txt"  // 输出格式，可填: 'txt' 'ass' 'srt'
}
```

## 样例
### 原文
```
Dialogue: 0,0:00:42.38,0:00:45.55,Default,,0000,0000,0000,,{\pos(172,497)\fscx50}（{\fscx100}叫び声{\fscx50}）
Dialogue: 0,0:00:45.55,0:00:49.88,Default,,0000,0000,0000,,{\pos(252,437)}そんな！
Dialogue: 0,0:00:45.55,0:00:49.88,Default,,0000,0000,0000,,{\pos(272,497)}魔物が向こうから来るとは！
Dialogue: 0,0:00:49.88,0:00:52.39,Default,,0000,0000,0000,,{\pos(192,497)}まだ戦闘準備が整ってないのに！
Dialogue: 0,0:00:52.39,0:00:56.22,Default,,0000,0000,0000,,{\pos(212,407)\c&H0000FFFF}これは{\fscx50}ラッキー{\fscx100}だな{\fscx50}。
Dialogue: 0,0:00:52.39,0:00:56.22,Default,,0000,0000,0000,,{\pos(612,497)}えっ？
Dialogue: 0,0:00:56.22,0:01:00.49,Default,,0000,0000,0000,,{\pos(232,497)\c&H0000FFFF}あと半日{\fscx50}　{\fscx100}歩かずにすんだ{\fscx50}。
Dialogue: 0,0:01:00.49,0:01:03.83,Default,,0000,0000,0000,,{\pos(432,407)\fscx50}グオー{\fscx100}！
Dialogue: 0,0:01:00.49,0:01:03.83,Default,,0000,0000,0000,,{\pos(212,497)}だめだ{\fscx50}コイツ　{\fscx100}情報より強い！
Dialogue: 0,0:01:03.83,0:01:06.00,Default,,0000,0000,0000,,{\pos(292,497)}ち{\fscx50}　{\fscx100}近づくこともできない！
Dialogue: 0,0:01:06.00,0:01:08.17,Default,,0000,0000,0000,,{\pos(272,407)\fscx50}グワーッ{\fscx100}！
Dialogue: 0,0:01:06.00,0:01:08.17,Default,,0000,0000,0000,,{\pos(372,497)\fscx50}（{\fscx100}兵士たち{\fscx50}）ワーッ{\fscx100}！
Dialogue: 0,0:01:08.17,0:01:10.67,Default,,0000,0000,0000,,{\pos(512,497)\fscx50}ウワーッ{\fscx100}！
Dialogue: 0,0:01:10.67,0:01:13.34,Default,,0000,0000,0000,,{\pos(472,497)\fscx50}ウッ{\fscx100}…{\fscx50}　{\fscx100}あっ{\fscx50}。
Dialogue: 0,0:01:13.34,0:01:16.01,Default,,0000,0000,0000,,{\pos(392,407)\fscx50}ウオォ{\fscx100}…{\fscx50}。
Dialogue: 0,0:01:13.34,0:01:16.01,Default,,0000,0000,0000,,{\pos(672,497)\fscx50}ウワーッ{\fscx100}！
Dialogue: 0,0:01:16.01,0:01:23.02,Default,,0000,0000,0000,,{\pos(172,497)}♬～
```

### 处理后文本（默认设置）
```
そんな！
魔物が向こうから来るとは！
まだ戦闘準備が整ってないのに！
これはラッキーだな
えっ？
あと半日　歩かずにすんだ
だめだコイツ　情報より強い！
ち… 近づくこともできない！
```

## TODO 计划
- GUI（或许？）

## 报错
欢迎提 [Issue](/issues) 或 [PR](/pulls)！