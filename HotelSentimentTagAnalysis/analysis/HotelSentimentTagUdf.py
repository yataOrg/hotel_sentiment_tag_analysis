import sys

from HotelSentimentTagAnalysis.analysis import parse_line
import parse_line

f = open('d:/EmotionalTag/WritingContent.txt')
allLines = f.readlines()

# sys.stdin

for line in allLines:
    if not line:
        break

    print '\n -------------------------------------'
    print "Writing Content: " + line

    bootstrap = parse_line.Bootstrap()
    bootstrap.initAnalyzer()
    resultDict = bootstrap.analyze(line)

    if resultDict:
        for topic, content in resultDict.items():
            print content

if __name__ == '__main__':
    pass
