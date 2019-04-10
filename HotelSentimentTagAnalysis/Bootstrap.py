# encoding=utf-8

import sys, io
import json
import pkg_resources

reload(sys)
sys.setdefaultencoding('utf8')
import analysis.parse_line


class Bootstrap:
    def __init__(self):
        self.saUtil = analysis.parse_line.SaUtil()
        # 获取相应配置 加载字典 和 topic keywords等数据
        self.sentimentAnalysis = analysis.parse_line.SentimentAnalysis()

    def initAnalyzer(self):
        # 获取read.json 的数据  评论词
        json = self.sentimentAnalysis.load_json(pkg_resources.resource_filename('HotelSentimentTagAnalysis', self.sentimentAnalysis.CONFIG.get('data', 'json_file')))
        # print "json---\n"
        # print json.dumps(json1, ensure_ascii=False)
        # eg: {u'\u65e7\u65f6': {'default_value': 0, 'topic_word': '\xe5\xbb\xba\xe7\xad\x91', 'critical_word_set': set([u'\u7279\u8272', u'\u597d', u'\u5dee'])}
        self.sentimentAnalysis.keyword_dict = self.sentimentAnalysis.transform_json(json)

    def analyze(self, line):

        # 比如我想知道 line 的内容
        # print(line)
        return self.sentimentAnalysis.run(line)

    def showDemo(self, dict, BlockedTagsStr = ''):
        #  BlockedTagsStr: '', '1,2,3', '1'
        return self.saUtil.show_demo(dict, BlockedTagsStr )


if __name__ == '__main__':

    # line = u'酒店位置在奥运村附近，离鸟巢、奥林森林公园很近。晚饭后可以到那边三步。出行也很方便，下次还会选择该酒店'
    # line = u'因为走的急，没有来得及拍照。很满意的一次入住，卫生条件不错，早餐也很丰富，服务员态度非常好，好像回到家的感觉，非常满意，下次来还要住这里。有评论说早餐单一，我个人觉得还是很不错的，满意！'
    data = ''
    with io.open('./commentbaseinfo.data', 'r', encoding='utf-8') as f:
        data = f.readlines()

    bootstrap = Bootstrap()
    bootstrap.initAnalyzer()
    for line_data in data:
        commentid, line = line_data.split()
        print('abc')
        print(line)
        resultList = bootstrap.showDemo(bootstrap.analyze(line))
        # print resultList
        # print json.dumps(resultList, ensure_ascii=False)
        print "*******\n"
        for tuple in resultList:
            print commentid + chr(9) + line + chr(9) + tuple[0] + chr(9) + tuple[1] + chr(9) + tuple[2] + chr(9) + tuple[3]
