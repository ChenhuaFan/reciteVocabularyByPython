# reciteVocabularyByPython
一个帮助你背单词的脚本（py2.7）

# 使用方法
```shell
# 先申请有道开放平台账户，会有100元体验金，够用了。
#
# 打开python脚本，修改40，41行的id和key，保存。
#
# 在当前目录下
$ bash go.sh
#
# 使用vi在 wordList 下新建单词表(*.txt)就可以使用啦
```

# 文件结构
1. wordList：存放单词表
2. wordSound:存放单词语音

# 已知Bugs
1. MacOS完美使用；linux无法播放语音其他正常；windows GG。
2. 生成选项时判断有误，可能会存在多个正确选项的问题。
3. 有道返回的释义总是含有人名，很烦。

# TODO：
1. 修复bug2，其他随缘。
2. 整合提醒服务，定时给你发邮件提醒复习。目前只能给我自己发邮件，考完试再完善提醒服务。
