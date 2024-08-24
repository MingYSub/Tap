# Tap (TV ASS Process)
处理从 TV 提取的 ASS 字幕的脚本。

## 功能
- 文字处理
  - 半角片假名转为全角
  - 全角英数转为半角
  - 中西文之间添加六分之一空格（U+2006）
- 删除多余信息
  - 去除位置、颜色等信息
  - 删除外字（`[外:xxx]`，可能误伤极少字）
  - 去除语气词
- 其余调整
  - 合并时间重复行
  - 整理重复音节
- 多格式输出
  - 输出 txt、ass 和 srt 格式
  - 可输出说话人
  - 输出时行尾追加字符
- 批量转换文件夹下的所有 ass 文件

## 用法

### 命令行

```
usage: Tap.py [-h] [--conf CONF_PATH] [--format {ass,txt,srt}] [--output OUTPUT_PATH] [--suffix ENDING_CHAR] [--actor | --no-actor] [--clean | --no-clean]
              [--merge | --no-merge | --force-merge] [--space | --no-space] [--adjust-repeated-syllables | --no-adjust-repeated-syllables]
              path [path ...]

positional arguments:
  path                  Input path (supports files and directories)

options:
  -h, --help            show this help message and exit
  --conf CONF_PATH      Specify configuration file
  --format {ass,txt,srt}
                        Specify output format
  --output OUTPUT_PATH, -o OUTPUT_PATH
                        Specify output path
  --suffix ENDING_CHAR, -x ENDING_CHAR
                        Char(s) appended to the end of each line
  --actor, -a           Output speaker
  --no-actor, -an       Do not output speaker
  --clean, -c           Remove interjections
  --no-clean, -cn       Do not remove interjections
  --merge, -m           Automatically merge lines with overlapping times
  --no-merge, -mn       Do not merge lines with overlapping times
  --force-merge, -mf    Force merge lines with overlapping times
  --space, -s           Add space between CJK and AN characters
  --no-space, -sn       Do not add space between CJK and AN characters
  --adjust-repeated-syllables, -rs
                        Adjust repeated syllables
  --no-adjust-repeated-syllables, -rsn
                        Do not adjust repeated syllables
```

### Windows GUI

Release 里提供了 GUI 程序。

## 配置文件

如下为默认配置文件的注释，请不要向文件添加注释。
```
{
    "actor": false,  // 输出说话人，可填: true false，注意没有引号
    "add_spaces": true,  // 中西文之间添加六分之一空格（U+2006），可填: true false
    "adjust_repeated_syllables": true,  // 整理重复音节，可填: true false
    "clean_mode": true,  // 删除语气词，可填: true false
    "ending_char": "",  // 输出时行尾添加的字符
    "merge": "auto",  // 合并时间重复行，可填: "none" "auto" "force"
    "output_format": "txt"  // 输出格式，可填: "txt" "ass" "srt"
}
```

## 样例
### 原文
```
Dialogue: 0,0:15:50.85,0:15:55.15,Default,,0000,0000,0000,,{\pos(440,600)\c&H00ffff&}ﾁｰｽﾞも ｻﾞ･燻製ﾁｰｽﾞって\N
Dialogue: 0,0:15:50.85,0:15:55.15,Default,,0000,0000,0000,,{\pos(466,680)\c&H00ffff&}色になってて いいねぃ｡\N
Dialogue: 0,0:16:00.02,0:16:04.19,Default,,0000,0000,0000,,{\pos(253,680)}燻製には ﾋﾞｰﾙが合うんでゃ…｡\N
Dialogue: 0,0:16:04.19,0:16:07.20,Default,,0000,0000,0000,,{\pos(253,600)}(恵那)先生も\N
Dialogue: 0,0:16:04.19,0:16:07.20,Default,,0000,0000,0000,,{\pos(306,680)}気に入ってくれたみたいだね｡\N
Dialogue: 0,0:16:07.20,0:16:09.90,Default,,0000,0000,0000,,{\pos(306,440)}(千明)そして… お待ちかね｡\N
Dialogue: 0,0:16:15.70,0:16:20.38,Default,,0000,0000,0000,,{\pos(226,560)}ﾃﾞ ﾃﾞｽ･ｿｰｾｰｼﾞｱﾀｯｸや！\N
Dialogue: 0,0:16:15.70,0:16:20.38,Default,,0000,0000,0000,,{\pos(626,680)}わ 忘れてた～！\N
Dialogue: 0,0:16:20.38,0:16:22.88,Default,,0000,0000,0000,,{\pos(226,680)}あ あき うちらは ええから～｡\N
Dialogue: 0,0:16:22.88,0:16:26.21,Default,,0000,0000,0000,,{\pos(360,680)}いや 人数分ちゃんとあるし｡\N
Dialogue: 0,0:16:26.21,0:16:28.72,Default,,0000,0000,0000,,{\pos(466,680)}(２人)あぁ…｡\N
Dialogue: 0,0:16:28.72,0:16:31.72,Default,,0000,0000,0000,,{\pos(573,680)}まぁ 食え食え｡\N
Dialogue: 0,0:16:35.66,0:16:37.99,Default,,0000,0000,0000,,{\pos(573,560)}はむっ！\N
Dialogue: 0,0:16:35.66,0:16:37.99,Default,,0000,0000,0000,,{\pos(440,680)}《恵那ちゃん！》\N
Dialogue: 0,0:16:37.99,0:16:40.16,Default,,0000,0000,0000,,{\pos(546,680)}んっ… んっ…｡\N
Dialogue: 0,0:16:40.16,0:16:42.33,Default,,0000,0000,0000,,{\pos(546,680)}あっ… あぁ…｡\N
Dialogue: 0,0:16:42.33,0:16:45.83,Default,,0000,0000,0000,,{\pos(520,680)}ﾌﾝﾌﾝﾌﾝ…｡\N
```

### 处理后文本（默认设置）
```
チーズも　ザ・燻製チーズって　色になってて　いいねぃ
燻製には　ビールが合うんでゃ…
先生も　気に入ってくれたみたいだね
そして…　お待ちかね
デ… デス・ソーセージアタックや！
わ… 忘れてた～！
あ… あき　うちらは　ええから～
いや　人数分ちゃんとあるし
まぁ　食え食え
恵那ちゃん！
```

## 报错
欢迎提 Issue 或 PR！
