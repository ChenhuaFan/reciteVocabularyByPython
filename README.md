# reciteVocabularyByPython
A script to help you memorize words (py2.7)

# How to use
```shell
# First apply for a Youdao Open Platform account, you will get 100 RMB experience money, which is enough.
#
# Open the python script, change the id and key in line 40,41, save.
#
# In the current directory
$ bash go.sh
#
# Use vi to create a new word list (*.txt) under wordList and you're ready to use it
```

# File structure
1. wordList: holds the word list
2. wordSound: holds word sounds

# Known Bugs
1. there is an error in judgment when generating options, there may be a problem of multiple correct options.
2. The definition returned by Aritomo always contains the name of a person, which is annoying.

# TODO.
1. fix bug2, others as you like.
2. integrate reminder service to send you emails to remind you to review regularly. At present, I can only send emails to myself, and then improve the reminder service after the exam.
