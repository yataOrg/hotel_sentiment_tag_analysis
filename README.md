情感分析使用说明文档

功能：
对点评子句分析情感倾向

目前效果：
平均准确率95%

资源说明：
resource/topic_keyword.txt 标签与关键字映射关系
resource/topic_show.txt 标签与ID映射关系
resource/pos.txt 情感词表
resource/neg.txt 情感词表
resource/rule.txt 情感规则表
resource/degree_file.txt 程度副词表
resource/union_file.txt 固定搭配表
resource/stopword.dic 停用此表
resource/not_dict.txt 否定词表

配置说明：
read.json 标签配置表（标签种子情感词）
default.conf 系统配置表（内含注释）

系统说明：
实现效果：输入一句话，输出该句中的标签ID，标签子句，JSON片段

执行脚本
Boostrap.py
输入：line
输出：tagID Tag 句子片段 JSON片段

示例：
input：
因为走的急，没有来得及拍照。很满意的一次入住，卫生条件不错，早餐也很丰富，服务员态度非常好，好像回到家的感觉，非常满意，下次来还要住这里。有评论说早餐单一，我个人觉得还是很不错的，满意！
output：
116	早餐	有评论说早餐单一	[{"theme": 116, "idx": "69-77"}]
-1	家的感觉	好像回到家的感觉	[{"theme": 116, "idx": "69-77"}]
-1	卫生	卫生条件不错	[{"theme": 116, "idx": "69-77"}]
