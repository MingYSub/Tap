# Tap (TV ASS Process)
处理从 TV 提取的 ASS 字幕的脚本。

我们使用到的测试字幕例有 `为美好的世界献上爆焰！（部分集数）`、 `别当欧尼酱了！（部分集数）`，其中无明显错误。

## 特性
- 去除位置、颜色等信息
- 半角片假名转为全角
- 全角英数转为半角
- 合并时间重复行
- 修复 Captain2Ass 可能出现的 Bug（字幕中出现 `[外:xxx]`）
- 支持输出 txt、ass 和 srt
- 支持输出说话人
- 支持去除语气词
- 批量转换单文件夹下的所有 ass 文件

需要注意，去除语气词可能会导致误删，因此您可根据需要选择开启。

处理一个文件耗时约 0.1s。

## 用法
### Windows
可直接将提取出的 ASS 文件拖到脚本上，会自动读取配置文件运行。

### 命令行
```
usage: Tap.py [-h] [--format OUTPUT_FORMAT] [--output OUTPUT] [--actor | --no-actor] [--fix | --no-fix] [--clean | --no-clean]
              [--merge | --no-merge | --force-merge]
              path

positional arguments:
  path                  输入路径（支持文件和文件夹）

optional arguments:
  --format OUTPUT_FORMAT
                        指定输出格式
  --output OUTPUT, -o OUTPUT
                        指定输出路径
  --actor, -a           输出说话人
  --no-actor, -an       不输出说话人
  --fix                 修复 Captain2Ass 可能出现的 Bug（去除中括号）
  --no-fix              不修复 Captain2Ass 可能出现的 Bug
  --clean, -c           删除语气词
  --no-clean, -cn       不删除语气词
  --merge, -m           合并时间重复行
  --no-merge, -mn       不合并时间重复行
  --force-merge, -mf    强制合并时间重复行
```

## 配置文件
```python
config = {
    'merge': 'auto',  # 合并时间重复行，可填: 'none' 'auto' 'force'
    'clean_mode': True,  # 删除语气词
    'fix_mode': True,  # 去除中括号
    'actor': False,  # 输出说话人
    'output_format': 'txt',  # 输出格式，可填: 'txt' 'ass' 'srt'
}
```

## 样例
### 原文
```
Dialogue: 0,0:03:15.15,0:03:17.82,Default,,0,0,0,,{\pos(226,680)}(食べる音)\N
Dialogue: 0,0:03:17.82,0:03:20.32,Default,,0,0,0,,{\pos(520,680)\c&Hffff00&}そ それってつまり…｡\N
Dialogue: 0,0:03:20.32,0:03:22.82,Default,,0,0,0,,{\pos(226,680)\c&H00ffff&}うん 今から行ってくる｡\N
Dialogue: 0,0:03:22.82,0:03:26.33,Default,,0,0,0,,{\pos(600,560)\c&Hffff00&}あわわ… わあ…｡\N
Dialogue: 0,0:03:22.82,0:03:26.33,Default,,0,0,0,,{\pos(360,680)\c&H00ffff&}ふぇ？\N
Dialogue: 0,0:03:26.33,0:03:29.50,Default,,0,0,0,,{\pos(573,680)\c&Hffff00&}お お兄ちゃんが…｡\N
Dialogue: 0,0:03:29.50,0:03:31.50,Default,,0,0,0,,{\pos(466,680)\c&Hffff00&}自主的におでかけ…｡\N
Dialogue: 0,0:03:31.50,0:03:33.83,Default,,0,0,0,,{\pos(493,680)\c&Hffff00&}ぐふっ ううぅ…｡\N
Dialogue: 0,0:03:33.83,0:03:35.94,Default,,0,0,0,,{\pos(226,680)\c&H00ffff&}うわあ！ 泣いてる！\N
Dialogue: 0,0:03:35.94,0:03:38.27,Default,,0,0,0,,{\pos(573,680)\c&Hffff00&}しかも早起きして！\N
Dialogue: 0,0:03:38.27,0:03:40.61,Default,,0,0,0,,{\pos(493,680)\c&Hffff00&}自分で朝ごはんまで～｡\N
Dialogue: 0,0:03:40.61,0:03:44.61,Default,,0,0,0,,{\pos(226,600)\c&H00ffff&}ああ ああ もういい\N
Dialogue: 0,0:03:40.61,0:03:44.61,Default,,0,0,0,,{\pos(253,680)\c&H00ffff&}もういいってば～！\N
```
### 处理后文本（默认设置）
```
そ　それってつまり…
うん　今から行ってくる
わあ…
お　お兄ちゃんが…
自主的におでかけ…
泣いてる！
しかも早起きして！
自分で朝ごはんまで～
ああ　ああ　もういい　もういいってば～
```

## TODO 计划
- GUI（或许？）

## 报错
欢迎提 [Issue](/issues) 或 [PR](/pulls)！