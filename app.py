# coding=utf-8

import urllib
import urllib2
import hashlib
import json
import random
import os
import sys
import inspect
import time

# 实现 switch
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args:  # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False


class App(object):
    # 1. 语音选大意；2. 单词选大意；3. 学习模式；4. 大意选单词
    # 程序输出的带有解释的文本名为： name+md5(file).txt
    # 有道词典相关
    dic_api_http = "http://openapi.youdao.com/api"
    dic_id = ""
    dic_key = ""
    dic_sign = ""
    # 背词程序相关
    ver = "0.7.0"
    name = ""
    modes = []
    word_list = []
    word_list_exp = {}
    word_list_unknown = []
    word_list_review = []
    is_with_exp = True
    root_path = ""
    file_path = "/wordList/"
    file_with_exp = "_with_exp"
    file_md5 = ""
    file_type = ".txt"
    sound_path = "/wordSound/"
    split_mark = '>'
    eroll_name = ''
    start_time = ""
    end_time = ""

    def __init__(self):
        print App.app_text("版本为："+self.ver)
        if self.dic_id == "" or self.dic_key == "":
            print "没有找到有道词典id和key"
            return
        self.name = raw_input(App.app_text("您要加载的单词表是? 输入文件名即可,不需要后缀名: "))
        self.eroll_name = self.name
        # the next function
        print App.app_text("1. 语音选大意；2. 单词选大意；3. 学习模式；4. 解释选单词\n请输入您的学习模式: （输入序号，多重模式可以用空格隔开）")
        self.modes = raw_input().split(' ')
        # 解决str ASCII编码的问题
        filename = inspect.getframeinfo(inspect.currentframe()).filename
        self.root_path = os.path.dirname(os.path.abspath(filename)) #
        print self.root_path
        reload(sys)
        sys.setdefaultencoding('utf8')

    def run(self):
        # 先读取10个大意。初始化完成：随机3个选项，一个正确选项。并读出正确发音
        amount = 10
        # initial
        print App.app_text("初始化中......")
        self.initial_app()
        self.read_list()
        print App.app_text("初始化完成，开始背词")
        self.start_time = int(time.time())
        App.clear_terminal()
        # todo: switch语句实现功能选择 在每种模式之后返回该模式的类型并在复习阶段实现不同模式下的单词分模式复习(temp_wordList_unknown)
        # 1. 语音选大意；2. 语音选单词；3. 拼写模式；4. 仅语音
        for mode in self.modes:
            for case in switch(mode):
                if case("1"):
                    self.listen_meanings(self.word_list)
                    self.review("1")
                    break
                if case("2"):
                    self.listen_words(self.word_list)
                    self.review("2")
                    break
                if case("3"):
                    self.learn_word(self.word_list)
                    self.review("3")
                    break
                if case("4"):
                    self.meanings_word(self.word_list)
                    self.review("4")
                    break
                print App.warning_text("您输入的模式有误！")
        self.end_time = int(time.time())
        during_time = self.end_time - self.start_time
        print('本次背词时间持续： %s秒; 速度约： %s秒/单词' % (during_time, during_time/len(self.word_list)))

    def read_list(self):
        if not os.path.exists(self.root_path + self.file_path + self.name + self.file_type):
            while True:
                pages = raw_input(App.warning_text("OPPs, 文件貌似不存在。请再次输入文件名: "))
                if os.path.exists(self.root_path + self.file_path + pages + self.file_type):
                    # f = open(self.file_path + pages + self.file_type, "r")
                    self.name = pages
                    break
        f = open(self.root_path + self.file_path + self.name + self.file_type, "r")
        while True:
            line = f.readline()
            if line:
                pass  # do something here
                line = line.strip()
                p = line.rfind('.')
                filename = line[0:p]
                # important! 分隔符
                temp_line = line.split(self.split_mark, 1)
                try:
                    self.word_list_exp[temp_line[0]] = temp_line[1].decode("utf-8")
                except(Exception):
                    self.word_list_exp[temp_line[0]] = self.get_explain(temp_line[0])
                    self.is_with_exp = False
            else:
                break
        f.close()
        self.word_list = self.word_list_exp.keys()
        # 不是有语义的单词表？生成一份
        if not self.is_with_exp:
            with open(self.root_path + self.file_path + self.name + self.get_md5() + self.file_type, "w") as f:
                for item in self.word_list:
                    f.write(item + self.split_mark + self.word_list_exp[item] + '\n')
            f.close()
            print App.app_text("已为您生成带有语义的单词表。")
        print self.word_list

    def get_explain(self, word):
        post = {
            "q": word,
            "from": "auto",
            "to": "auto",
            "appKey": self.dic_id,
            "salt": "2",
            "sign": App.calcu_sign(self.dic_id + word + "2" + self.dic_key)
        }
        data = urllib.urlencode(post)
        request = urllib2.Request(self.dic_api_http, data)
        response = urllib2.urlopen(request)
        result_json = response.read()
        result_json = json.loads(result_json, encoding="utf-8")
        # 这是词汇解释部分
        try:
            result_json = result_json["basic"]["explains"]
        except(Exception):
            result_json = result_json["translation"]
        result_json = ",".join(result_json)
        return result_json.encode("UTF-8")

    # 计算有道词典签名
    @staticmethod
    def calcu_sign(text):
        m = hashlib.md5()
        return hashlib.md5(text).hexdigest()

    # 计算文件的MD5
    def get_md5(self):
        file_path = self.root_path + self.file_path + self.name + self.file_type
        if not self.file_md5 == "":
            return self.file_md5
        f = open(file_path, 'rb')
        md5_obj = hashlib.md5()
        md5_obj.update(f.read())
        hash_code = md5_obj.hexdigest()
        f.close()
        self.file_md5 = str(hash_code).lower()
        return self.file_md5

    # 初始化程序
    def initial_app(self):
        # 优先使用带有md5标志的文本
        if os.path.exists(self.root_path + self.file_path + self.name + self.get_md5() + self.file_type):
            print App.app_text("发现带存在语义的单词表版本，程序将使用该表")
            self.name = self.name + self.get_md5()
        return

    # 学习单词
    def learn_word(self, word_list):
        # 计数器
        count = 1
        for word in word_list:
            # 临时答案组
            temp_answer = {}
            print App.app_text("第" + str(count) + ("题：【" + App.normal_text(word) + "】"))
            count += 1
            rd = random.randint(1, len(self.word_list_exp))
            right_answer_position = random.randint(0, 3)
            if self.word_list_exp[word] == "":
                self.word_list_exp[word] = self.get_explain(word)
            temp_exp = self.word_list_exp[word]
            temp_answer[right_answer_position] = temp_exp
            cur_position = right_answer_position
            # print right_answer_position
            # 填充假答案
            for i in range(0, 3):
                cur_position = (cur_position + 1) % 4
                # print self.word_list[cur_position]
                temp_exp = self.word_list_exp[self.word_list[(rd - i * i) % len(self.word_list_exp)]]
                # temp_exp = temp_exp.split(",")
                temp_answer[cur_position] = temp_exp
                # 除去相同答案
                while temp_answer[cur_position] == temp_answer[right_answer_position]:
                    temp_answer[cur_position] = self.word_list_exp[
                        self.word_list[random.randint(0, 999) % len(self.word_list_exp)]]
            # 输出答案
            for j in range(0, 4):
                print App.app_text(str(j)) + ": " + str(temp_answer[j])
            print App.app_text("4") + ": 不认识"
            # 播放读音
            self.get_sound(word)
            # 交互逻辑
            user_answer = raw_input(App.app_text("你的答案是? 输入相应数字: "))
            if str(user_answer) != str(right_answer_position) or str(user_answer) == "4":
                print App.error_text("OOPS! 正确答案是: （" + word + "）" + temp_answer[right_answer_position])
                self.word_list_unknown.append(word)
                print App.app_text("该词已加入复习队列(现有" + str(len(self.word_list_unknown)) + "个需要复习)")
                self.add_to_review_list(word)
                print " "
                # 播放读音
                self.get_sound(word)
                time.sleep(3)
            else:
                print App.right_text("回答正确！（" + App.normal_text(word) + "）\n")
                time.sleep(1)
                try:
                    # 播放读音
                    self.get_sound(word)
                    time.sleep(2)
                    self.word_list_unknown.remove(word)
                    App.clear_terminal()
                except(Exception):
                    pass

    # 看意思选单词
    def meanings_word(self, word_list):
        # 计数器
        count = 1
        for word in word_list:
            # 翻译
            if self.word_list_exp[word] == "":
                self.word_list_exp[word] = self.get_explain(word)
            temp_exp = (self.word_list_exp[word]).split(",")
            # 临时答案组
            temp_answer = {}
            print App.app_text("第" + str(count) + ("题：【" + App.normal_text(temp_exp[random.randint(0, 999) % len(temp_exp)]) + "】"))
            count += 1
            rd = random.randint(1, len(self.word_list))
            right_answer_position = random.randint(0, 3)
            temp_answer[right_answer_position] = word
            cur_position = right_answer_position
            # print right_answer_position
            # 填充假答案
            for i in range(0, 3):
                cur_position = (cur_position + 1) % 4
                # print self.word_list[cur_position]
                temp_answer[cur_position] = self.word_list[random.randint(0, 999) % len(self.word_list_exp)]
                # 除去相同答案
                while temp_answer[cur_position] == temp_answer[right_answer_position]:
                    temp_answer[cur_position] = self.word_list[random.randint(0, 999) % len(self.word_list_exp)]
            print "0: 认识 \n1: 不认识"
            a = raw_input(App.warning_text("认不认识？"))
            if a != "0":
                print App.error_text("OOPS! 正确答案是: （" + word + "）")
                self.word_list_unknown.append(word)
                print App.app_text("该词已加入复习队列(现有" + str(len(self.word_list_unknown)) + "个需要复习)")
                self.add_to_review_list(word)
                print " "
                time.sleep(3)
                continue
            # 输出答案
            for j in range(0, 4):
                print App.app_text(str(j)) + ": " + temp_answer[j]
            print App.app_text("4") + ": 不认识"
            # 交互逻辑
            user_answer = raw_input(App.app_text("你的答案是? 输入相应数字: "))
            if str(user_answer) != str(right_answer_position) or str(user_answer) == "4":
                print App.error_text("OOPS! 正确答案是: （" + word + "）" + temp_answer[right_answer_position])
                self.word_list_unknown.append(word)
                print App.app_text("该词已加入复习队列(现有" + str(len(self.word_list_unknown)) + "个需要复习)")
                self.add_to_review_list(word)
                print " "
                self.get_sound(word)
                time.sleep(3)
            else:
                print App.right_text("回答正确！（" + App.normal_text(word) + "）")
                # 播放读音
                self.get_sound(word)
                time.sleep(2)
                App.clear_terminal()
                try:
                    self.word_list_unknown.remove(word)
                except(Exception):
                    pass

    # 听语音选意思
    def listen_meanings(self, word_list):
        # 计数器
        count = 1
        for word in word_list:
            # 临时答案组
            temp_answer = {}
            print App.app_text("第" + str(count) + ("题："))
            count += 1
            rd = random.randint(1, len(self.word_list_exp))
            right_answer_position = random.randint(0, 3)
            if self.word_list_exp[word] == "":
                self.word_list_exp[word] = self.get_explain(word)
            temp_exp = (self.word_list_exp[word]).split(",")
            if len(temp_exp) == 1:
                temp_answer[right_answer_position] = temp_exp[0]
            else:
                temp_answer[right_answer_position] = temp_exp[random.randint(0, 999) % len(temp_exp)]
            cur_position = right_answer_position
            # print right_answer_position
            # 填充假答案
            for i in range(0, 3):
                cur_position = (cur_position + 1) % 4
                # print self.word_list[cur_position]
                temp_exp = self.word_list_exp[self.word_list[(rd - i * i) % len(self.word_list_exp)]]
                temp_exp = temp_exp.split(",")
                if len(temp_exp) == 1:
                    temp_answer[cur_position] = temp_exp[0]
                else:
                    temp_answer[cur_position] = temp_exp[random.randint(0, 999) % len(temp_exp)]
                # 除去相同答案
                while temp_answer[cur_position] == temp_answer[right_answer_position]:
                    temp_answer[cur_position] = self.word_list_exp[
                        self.word_list[random.randint(0, 999) % len(self.word_list_exp)]]
            # 播放读音
            self.get_sound(word)
            print "0: 认识 \n1: 不认识"
            a = raw_input(App.warning_text("认不认识？"))
            if a != "0":
                print App.error_text("OOPS! 正确答案是: （" + word + "）" + temp_answer[right_answer_position])
                self.word_list_unknown.append(word)
                print App.app_text("该词已加入复习队列(现有" + str(len(self.word_list_unknown)) + "个需要复习)")
                self.add_to_review_list(word)
                print " "
                time.sleep(3)
                continue
            # 输出答案
            for j in range(0, 4):
                print App.app_text(str(j)) + ": " + temp_answer[j]
            print App.app_text("4") + ": 不认识"
            # 交互逻辑
            user_answer = raw_input(App.app_text("你的答案是? 输入相应数字: "))
            if str(user_answer) != str(right_answer_position) or str(user_answer) == "4":
                print App.error_text("OOPS! 正确答案是: （" + word + "）" + temp_answer[right_answer_position])
                self.word_list_unknown.append(word)
                print App.app_text("该词已加入复习队列(现有" + str(len(self.word_list_unknown)) + "个需要复习)")
                self.add_to_review_list(word)
                print " "
                time.sleep(3)
            else:
                print App.right_text("回答正确！（" + App.normal_text(word) + "）")
                time.sleep(1)
                App.clear_terminal()
                try:
                    self.word_list_unknown.remove(word)
                except(Exception):
                    pass

    # 看单词选意思
    def listen_words(self, word_list):
        # 计数器
        count = 1
        for word in word_list:
            # 临时答案组
            temp_answer = {}
            print App.app_text("第" + str(count) + ("题：【"+ App.normal_text(word) +"】"))
            count += 1
            rd = random.randint(1, len(self.word_list_exp))
            right_answer_position = random.randint(0, 3)
            if self.word_list_exp[word] == "":
                self.word_list_exp[word] = self.get_explain(word)
            temp_exp = (self.word_list_exp[word]).split(",")
            if len(temp_exp) == 1:
                temp_answer[right_answer_position] = temp_exp[0]
            else:
                temp_answer[right_answer_position] = temp_exp[random.randint(0, 999) % len(temp_exp)]
            cur_position = right_answer_position
            # print right_answer_position
            # 填充假答案
            for i in range(0, 3):
                cur_position = (cur_position + 1) % 4
                # print self.word_list[cur_position]
                temp_exp = self.word_list_exp[self.word_list[(rd - i * i) % len(self.word_list_exp)]]
                temp_exp = temp_exp.split(",")
                if len(temp_exp) == 1:
                    temp_answer[cur_position] = temp_exp[0]
                else:
                    temp_answer[cur_position] = temp_exp[random.randint(0, 999) % len(temp_exp)]
                # 除去相同答案
                while temp_answer[cur_position] == temp_answer[right_answer_position]:
                    temp_answer[cur_position] = self.word_list_exp[
                        self.word_list[random.randint(0, 999) % len(self.word_list_exp)]]
            print "0: 认识 \n1: 不认识"
            a = raw_input(App.warning_text("认不认识？"))
            if a != "0":
                print App.error_text("OOPS! 正确答案是: （" + word + "）" + temp_answer[right_answer_position])
                self.word_list_unknown.append(word)
                print App.app_text("该词已加入复习队列(现有" + str(len(self.word_list_unknown)) + "个需要复习)")
                self.add_to_review_list(word)
                print " "
                time.sleep(3)
                continue
            # 输出答案
            for j in range(0, 4):
                print App.app_text(str(j)) + ": " + temp_answer[j]
            print App.app_text("4") + ": 不认识"
            # 交互逻辑
            user_answer = raw_input(App.app_text("你的答案是? 输入相应数字: "))
            if str(user_answer) != str(right_answer_position) or str(user_answer) == "4":
                print App.error_text("OOPS! 正确答案是: （" + word + "）" + temp_answer[right_answer_position])
                self.word_list_unknown.append(word)
                print App.app_text("该词已加入复习队列(现有" + str(len(self.word_list_unknown)) + "个需要复习)")
                self.add_to_review_list(word)
                print " "
                self.get_sound(word)
                time.sleep(3)
            else:
                print App.right_text("回答正确！（" + App.normal_text(word) + "）")
                self.get_sound(word)
                time.sleep(2)
                App.clear_terminal()
                try:
                    self.word_list_unknown.remove(word)
                except(Exception):
                    pass

    # 拼写模式
    def spell(self, world_list):
        print "拼写模式，功能开发中"
        pass

    # 仅听语音，认识或不认识
    def listen_only(self, word_list):
        print "仅听语音，功能开发中"
        pass

    # 添加进需要生成复习文件的单词表
    def add_to_review_list(self, word):
        if word in self.word_list_unknown and word not in self.word_list_review:
            self.word_list_review.append(word)

    # 复习
    def review(self, mode):
        print "背词阶段完成。：D"
        while not len(self.word_list_unknown) == 0:
            print "复习阶段开始......"
            for case in switch(mode):
                if case("1"):
                    self.listen_meanings(self.word_list_unknown)
                    break
                if case("2"):
                    self.listen_words(self.word_list_unknown)
                    break
                if case("3"):
                    self.learn_word(self.word_list_unknown)
                    break
                if case("4"):
                    self.meanings_word(self.word_list_unknown)
                    break
        # 生成一份儿经常错的单词表
        if len(self.word_list_review) != 0:
            f = open(self.root_path + self.file_path + self.name + "_review" + self.file_type, 'w')
            for word in self.word_list_review:
                f.write(word + self.split_mark + self.word_list_exp[word] + '\n')
            f.close()
            print "已为您生成了多次错误的单词表，您可以着重复习."

    # 得到语音
    def get_sound(self, word):
        name = str(self.root_path + self.sound_path + word + ".mp3").replace(' ', '_')
        try:
            if not os.path.exists(name):
                headers = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)"}
                url = "http://dict.youdao.com/dictvoice"
                cuntry = "2"  # 美式为2，英式为1
                params = {"audio": word, "type": cuntry}
                data = urllib.urlencode(params)
                request = urllib2.Request(url, data, headers)
                response = urllib2.urlopen(request)
                fs = open(name, 'wb')
                fs.write(response.read())  # response.read()即是返回的音频流，你可以直接发给前台不用保存
                fs.close()
            # 播放音乐
            os.system("open " + name)
        except(Exception):
            print "抱歉，网络原因，单词" + word + "播放失败"

    @staticmethod
    def error_text(str):
        return "\033[31m"+ str + "\033[0m"

    @staticmethod
    def warning_text(str):
        return "\033[33m" + str + "\033[0m"

    @staticmethod
    def right_text(str):
        return "\033[37m" + str + "\033[0m"

    @staticmethod
    def normal_text(str):
        return "\033[37m" + str + "\033[0m"

    @staticmethod
    def app_text(str):
        return "\033[36m" + str + "\033[0m"

    @staticmethod
    def clear_terminal():
        print "\33[2J"

app = App()
app.run()
