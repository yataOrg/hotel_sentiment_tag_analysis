# encoding=utf-8
__author__ = 'xdyue'

import json
import re
from ConfigParser import SafeConfigParser
from collections import defaultdict

import pkg_resources
import sys
reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append(pkg_resources.resource_filename('HotelSentimentTagAnalysis.lib', 'jieba.egg'))
import jieba as jieba
jieba.set_dictionary(pkg_resources.resource_filename('HotelSentimentTagAnalysis.resource', 'dictHtlBI.txt'))

class SaUtil:
    """ 情感分析文本处理通用类
    """
    def read_file(self, filename):
        """ 读文件
        """
        file_list = []
        with open(filename, 'r') as readfile:
            for line in readfile.readlines():
                line = line.strip()
                file_list.append(line)
        return file_list

    def get_keywords_topic(self):
        """ 获取keyword与topic的对应关系
        """
        keyword_topic_dict = {}
        read_line_list = self.read_file(pkg_resources.resource_filename('HotelSentimentTagAnalysis.resource', 'topic_keyword.txt'))
        for line in read_line_list:
            # print(line)
            topic, keyword = line.strip().split()
            keyword_topic_dict[keyword.decode('utf8')] = topic.decode('utf8')
        return keyword_topic_dict

    def show_demo(self, show_dict, BlockedTagsStr):
        #content :topic, line_sentiment_tag, part, writing_id, writing_content, tagID
        resultList = []
        blockedList = BlockedTagsStr.split(',')
        # blockedSet = set(blockedList)
        # blockedSet.add("-1")
        if not show_dict:
            # print (chr(44) + chr(9)).join(['no tag', json.dumps(resultList)])
            return
        for topic, content in show_dict.items():
            resultDict = {}
            if len(content) < 5 or content[-1] == -1 or (len(blockedList) > 0 and str(content[-1]) in blockedList):
                continue
            resultDict["theme"] = content[-1]
            start = content[3].index(content[2])
            end = len(content[2]) + start
            resultDict["idx"] = str(start)+'-'+str(end)
            resultList.append(resultDict)
        resultJson = json.dumps(resultList)

        returnList = []
        for topic, content in show_dict.items():
            if str(content[-1]) in blockedList:
                continue
            # print (chr(44) + chr(9)).join([str(content[-1]), content[2], resultJson])
            returnList.append(([str(content[-1]), content[0], content[2], resultJson, content[2]]))
        return returnList

    def get_topic_id(self):
        """ 获取topic对应的id
        """
        topic_id_dict = {}
        read_line_list = self.read_file(pkg_resources.resource_filename('HotelSentimentTagAnalysis.resource', 'topic_show.txt'))
        for read_line in read_line_list:
            print('*****'*3)
            print(read_line)
            ID, tag, topic_word = read_line.strip().split()
            topic_id_dict[topic_word.decode('utf8')+str(tag)] = int(ID)
        return topic_id_dict

class SentimentAnalysis:
    """情感分析的主类
    """

    def __init__(self):
        self.keyword_dict = {}
        # self.CONFIG = self.load_config(_get_abs_path('default.conf'))
        self.CONFIG = self.load_config(pkg_resources.resource_filename('HotelSentimentTagAnalysis', 'default.conf'))
        self.evaluate = self.CONFIG.getboolean('run_mode', 'evaluate')
        self.run_console = self.CONFIG.getboolean('run_mode', 'run_console')
        self.run_hotel_demo = self.CONFIG.getboolean('run_mode', 'run_hotel_demo')
        self.show_seg = self.CONFIG.getboolean('run_mode', 'show_seg')
        self.prepare_dict()
        self.keyword_topic_dict = SaUtil().get_keywords_topic()
        self.idTopicDict = SaUtil().get_topic_id( )
        self.columnDelimiter = (chr(44) + chr(9))

    def prepare_dict(self):
        """ 加载词典
        """
        self.degreeWords = set(self.load_dict(pkg_resources.resource_filename('HotelSentimentTagAnalysis.resource', self.CONFIG.get('data', 'degree_file'))))
        self.posWords = set(self.load_dict(pkg_resources.resource_filename('HotelSentimentTagAnalysis.resource', self.CONFIG.get('data', 'pos_file'))))
        self.negWords = set(self.load_dict(pkg_resources.resource_filename('HotelSentimentTagAnalysis.resource', self.CONFIG.get('data', 'neg_file'))))
        self.pos_sentence = set(self.load_dict(pkg_resources.resource_filename('HotelSentimentTagAnalysis.resource', self.CONFIG.get('data', 'pos_sentence'))))
        self.neg_sentence = set(self.load_dict(pkg_resources.resource_filename('HotelSentimentTagAnalysis.resource', self.CONFIG.get('data', 'neg_sentence'))))
        self.unionWords = set(self.load_dict(pkg_resources.resource_filename('HotelSentimentTagAnalysis.resource', self.CONFIG.get('data', 'union_file'))))
        self.Rules = self.load_rule(pkg_resources.resource_filename('HotelSentimentTagAnalysis.resource', self.CONFIG.get('data', 'rule_file')))
        notWords = self.load_dict(pkg_resources.resource_filename('HotelSentimentTagAnalysis.resource', self.CONFIG.get('data', 'not_file')))

        self.not_set = set([x.decode('utf8') for x in notWords])
        self.stop_key = set([line.strip().decode('utf-8') for line in open(pkg_resources.resource_filename('HotelSentimentTagAnalysis.resource', self.CONFIG.get('data', 'stop_file'))).readlines()])

    def load_dict(self, file_name):
        """ 词典加载函数
        """
        dict_words = dict()
        jieba.load_userdict(file_name)
        with open(file_name, 'r') as readFile:
            for line in readFile.readlines():
                line = line.strip()
                if not line:
                    continue
                dict_words[line.decode('utf8')] = ''
        return dict_words

    def load_rule(self, file_name):
        """ 规则加载函数
            不使用
        """
        rule_dict = defaultdict(list)
        with open(file_name, 'r') as readFile:
            for line in readFile.readlines():
                line = line.strip()
                line_part = line.split()
                rule_dict[line_part[0].decode('utf8')] = line_part[1:]
        return rule_dict

    def parse_word(self, keyword, pre_part, post_part):
        """ 对关键字进行情感分析
        """
        keyword = keyword.decode('utf8')
        if keyword in self.posWords:
            sentiment_tag = 1
        elif keyword in self.negWords:
            sentiment_tag = -1
        elif keyword in self.Rules:
            rule_value_list = self.Rules.get(keyword)
            value_index = None
            sentiment_word = None
            for index, word in enumerate(post_part):
                if word in rule_value_list:
                    value_index = index
                    sentiment_word = word
                    break
            not_index = None
            if value_index:
                for index, word in enumerate(post_part[:value_index]):
                    if word in self.not_set:
                        not_index = index+1
                if sentiment_word in self.posWords:
                    if not_index:
                        return 1
                    else:
                        return -1
                elif sentiment_word in self.negWords:
                    if not_index:
                        return -1
                    else:
                        return 1
            else:
                return
        else:
            return
        pre_not_num = len([not_word for not_word in self.not_set if not_word in pre_part])
        #判断否定词个数
        try:
            if pre_not_num % 2 == 0:
                sentiment_tag = sentiment_tag * 1
            else:
                sentiment_tag = sentiment_tag * (-1)
        except:
            return
        return sentiment_tag

    def parse_part_reverse(self, each_part):
        """ 对窗口进行情感分析
        """
        sentiment_tag = None
        last_sentiment_word = None
        last_not = None
        not_only = None
        for word in each_part[::-1]:
            word = word.decode('utf8')
            if word in self.Rules:
                if last_sentiment_word not in self.Rules.get(word):continue
                if last_not:
                    sentiment_tag = sentiment_tag
                else:
                    sentiment_tag = sentiment_tag * (-1)
                break
            if word in self.posWords:
                if sentiment_tag:break
                if last_not:break
                last_sentiment_word = word
                sentiment_tag = 1
            elif word in self.negWords:
                if sentiment_tag:break
                if last_not:break
                last_sentiment_word = word
                sentiment_tag = -1
            elif word in self.not_set:
                if not sentiment_tag:
                    not_only = True
                else:
                    last_not = word
        if sentiment_tag:
            if last_not:
                return sentiment_tag * (-1)
            else:
                return sentiment_tag
        elif not_only:
            return -1
        else:
            return 0

    def further_segment(self, line_list, keyword):
        """ 细分查询，去停用词
        """
        further_word_list = []
        for word in line_list:
            if word in self.stop_key:
                continue
            union_set = set(self.keyword_dict.get(keyword).get('critical_word_set'))
            union_set = union_set.union(self.not_set)
            union_set = union_set.union(self.degreeWords)
            union_set.add(keyword)
            for critical in union_set:
                if critical in word and critical != word and word not in self.unionWords:
                    word = word.replace(critical, ' '+critical+' ')
            if ' ' in word:
                temp_list = word.split(' ')
                temp_list = [x for x in temp_list if x != '']
                word = ' '.join(temp_list)
            further_word_list.append(word)
        result_list = []
        for x_word in further_word_list:
            x_word_list = x_word.strip().split()
            result_list.extend(x_word_list)
        return result_list

    def rule_append(self, input_tag, input_part, input_keyword):
        if input_keyword in self.Rules:
            list_intersection = [i for i in input_part if i.decode('utf8') in self.Rules.get(input_keyword)]
            if len(list_intersection) != 0:
                return input_tag * (-1)
        return input_tag

    def parse_line_hotel(self, each_tuple):
        """ 对点子句进行情感分析
        """
        keyword, word_list, full_part, writing_content = each_tuple[0], each_tuple[1], each_tuple[2], each_tuple[3]
        threshold = 9
        line_sentiment_tag = 0
        target_index = word_list.index(keyword.decode('utf8'))
        first_part = word_list[target_index+1:target_index+threshold]
        start_index = target_index - threshold if target_index - threshold >= 0 else 0
        second_part = word_list[start_index:target_index]
        third_part = word_list[target_index+threshold:target_index+threshold*2]
        for each_part in [first_part, second_part, third_part, keyword]:
            if not each_part:
                continue
            if each_part == keyword:
                line_sentiment_tag = self.parse_word(keyword, second_part, first_part)
            else:
                line_sentiment_tag = self.parse_part_reverse(each_part)
                line_sentiment_tag = self.rule_append(line_sentiment_tag, each_part, keyword)
            if line_sentiment_tag:
                break
        defaultValue = self.keyword_dict.get(keyword).get('default_value')
        if not line_sentiment_tag:
            line_sentiment_tag = defaultValue
        topic = self.keyword_topic_dict.get(keyword)
        # result = self.columnDelimiter.join([topic, str(line_sentiment_tag), full_part.strip()])
        tagId = self.idTopicDict.get(topic+str(line_sentiment_tag), -1)
        result = [topic, str(line_sentiment_tag), full_part.strip(), writing_content, tagId]
        return result

    def add_impression(self, each_tuple):
        keyword, word_list, full_part, writing_content = each_tuple[0], each_tuple[1], each_tuple[2], each_tuple[3]
        topic = self.keyword_topic_dict.get(keyword)
        if keyword == 'good':
            line_sentiment_tag = '1'
        elif keyword == 'bad':
            line_sentiment_tag = '-1'
        tagId = self.idTopicDict.get(topic+line_sentiment_tag, -1)
        result = [topic, line_sentiment_tag, full_part, writing_content, tagId]
        return result

    def get_sub_sentence(self, input_line, console = False):
        """ 分割点评句为子句
        """
        result_list = []
        writing_content = input_line
        comment_part = re.split(r"[ ……。，；！？,.;?!！（）()～~\n\r|、'——]".decode('utf8'), writing_content.decode('utf8'))
        for part in comment_part:
            word_list = [x for x in jieba.cut(part, cut_all=False, HMM=False)]
            for keyword in word_list:
                if keyword in self.keyword_dict.keys():
                    further_list = self.further_segment(word_list, keyword)
                    if keyword not in further_list:
                        further_list = word_list
                    result_list.append((keyword, further_list, part, writing_content))
                elif part in self.pos_sentence:
                    result_list.append(('good', part, part, writing_content))
                elif part in self.neg_sentence:
                    result_list.append(('bad', part, part, writing_content))
        return result_list

    def run(self, line):
        """ 控制台执行程序，因为单独分离出了，所以这里没有用
        """
        tuple_list = self.get_sub_sentence(line, console=True)
        if not tuple_list:
            # print 'no label: no tag found in topic_keyword.txt'
            return

        resultDict = {}
        for each_tuple in tuple_list:
            keyword = each_tuple[0]
            topic = self.keyword_topic_dict.get(keyword)
            if topic and topic not in resultDict and topic and topic not in ['good', 'bad']:
                resultDict[topic] = self.parse_line_hotel(each_tuple)
            if topic in ['good', 'bad']:
                resultDict[topic] = self.add_impression(each_tuple)

        return resultDict

    def load_json(self, json_file):
        """ 加载json文件
        """
        with open(json_file) as read_file:
            json_list = []
            for line in read_file.readlines():
                json_line = json.loads(str(line))
                json_list.append(json_line)
        return json_list

    def load_config(self, conf_file):
        """ 加载配置文件
        """
        config = SafeConfigParser()
        with open(conf_file, 'rb') as conf_file_fp:
            config.readfp(conf_file_fp)
        return config

    def get_topic_keyword(self, filename):
        """ 获得topic与keywords的对应关系
        """
        topic_word_dict = defaultdict(list)
        with open(filename, 'r') as read_file:
            for line in read_file.readlines():
                topic, key = line.strip().split()
                key_word_list = topic_word_dict.get(topic, [])
                key_word_list.append(key)
                topic_word_dict[topic] = key_word_list
        return topic_word_dict

    def transform_json(self, json_content):
        """ 将json存储为字典
        """
        result_dict = {}
        topic_keyword_dict = self.get_topic_keyword(pkg_resources.resource_filename('HotelSentimentTagAnalysis.resource', 'topic_keyword.txt'))
        for json_line in json_content:
            for topic_word, keyword_critical_reverse in json_line.items():
                topic_word = topic_word.encode('utf8')
                keywords = set(topic_keyword_dict.get(topic_word, []))
                critical_word_set = set(keyword_critical_reverse.get('critical_words', []))
                defaultValue = int(keyword_critical_reverse.get('default', 0))
                for each_keyword in keywords:
                    jieba.suggest_freq(each_keyword, True)
                    result_dict[each_keyword.decode('utf8')] = {'topic_word':topic_word, 'default_value':defaultValue, 'critical_word_set':critical_word_set}
        return result_dict

# class Bootstrap():
#     def __init__(self):
#         self.saUtil = SaUtil()
#         self.sentimentAnalysis = SentimentAnalysis()
#
#     def initAnalyzer(self):
#         json = self.sentimentAnalysis.load_json(os.path.join(os.path.dirname(__file__), '..', self.sentimentAnalysis.CONFIG.get('data', 'json_file')))
#         self.sentimentAnalysis.keyword_dict = self.sentimentAnalysis.transform_json(json)
#
#     def analyze(self, line):
#         return self.sentimentAnalysis.run(line)
#
#     def showDemo(self, dict):
#         self.saUtil.show_demo(dict)


# if __name__ == '__main__':
# #     line = u'交通好，房间好'
#     line = u'很好 很干净 很好 很干净 很好 很干净'
#     print line
#
#     bootstrap = Bootstrap()
#     bootstrap.initAnalyzer()
#     bootstrap.showDemo(bootstrap.analyze(line))
#
#     sa = SaUtil()
#     print sa.read_file('resource', 'neg.txt')

