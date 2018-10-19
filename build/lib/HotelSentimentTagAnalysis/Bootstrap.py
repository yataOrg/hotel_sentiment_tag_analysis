# encoding=utf-8

import sys

import pkg_resources

reload(sys)
sys.setdefaultencoding('utf8')
import analysis.parse_line


class Bootstrap:
    def __init__(self):
        self.saUtil = analysis.parse_line.SaUtil()
        self.sentimentAnalysis = analysis.parse_line.SentimentAnalysis()

    def initAnalyzer(self):
        json = self.sentimentAnalysis.load_json(pkg_resources.resource_filename('HotelSentimentTagAnalysis', self.sentimentAnalysis.CONFIG.get('data', 'json_file')))
        self.sentimentAnalysis.keyword_dict = self.sentimentAnalysis.transform_json(json)

    def analyze(self, line):
        return self.sentimentAnalysis.run(line)

    def showDemo(self, dict, BlockedTagsStr = ''):
        #  BlockedTagsStr: '', '1,2,3', '1'
        return self.saUtil.show_demo(dict, BlockedTagsStr )


if __name__ == '__main__':
    # line = u'酒店位置在奥运村附近，离鸟巢、奥林森林公园很近。晚饭后可以到那边三步。出行也很方便，下次还会选择该酒店'
    line = u'因为走的急，没有来得及拍照。很满意的一次入住，卫生条件不错，早餐也很丰富，服务员态度非常好，好像回到家的感觉，非常满意，下次来还要住这里。有评论说早餐单一，我个人觉得还是很不错的，满意！'
    print line

    bootstrap = Bootstrap()
    bootstrap.initAnalyzer()
    resultList = bootstrap.showDemo(bootstrap.analyze(line))
    for tuple in resultList:
        print tuple[0] + chr(9) + tuple[1] + chr(9) + tuple[2] + chr(9) + tuple[3]
