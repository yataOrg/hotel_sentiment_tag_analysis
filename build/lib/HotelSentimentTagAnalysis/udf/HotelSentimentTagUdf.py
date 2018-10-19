'''
@author liushun
'''

# import pkg_resources
import sys
# sys.path.append(pkg_resources.resource_filename('ParselineWrapper', 'HotelSentimentTagAnalysis.egg'))
sys.path.append(r'./HotelSentimentTagAnalysis.egg-20160308-143006.egg')

import HotelSentimentTagAnalysis.Bootstrap

# f = open('d:/EmotionalTag/WritingContent.txt')
# allLines = f.readlines()

bootstrap = HotelSentimentTagAnalysis.Bootstrap.Bootstrap()
bootstrap.initAnalyzer()

for line in sys.stdin:
    if not line:
        continue

    # print '\n -------------------------------------'
    # print "Writing Content: " + line

    # try:
    line = line.strip()
    splits = line.split(chr(1))
    comment = splits[0]
    BlockedTagsStr = splits[1]
    if len(splits) > 2:
        others = splits[2]
        for i in range(3, len(splits)):
            others = chr(1).join([others, splits[i]])

    resultList = bootstrap.showDemo(bootstrap.analyze(comment), BlockedTagsStr)

    if resultList:
        for tuple in resultList:
            # if tuple[0] == '-1':
            #     break
            result = chr(1).join([tuple[0], tuple[-2], tuple[-1], others])
            print result
    else:
        print chr(1).join(['', '', others])
        # pass
    # except Exception:
    #     pass


if __name__ == '__main__':
    pass
