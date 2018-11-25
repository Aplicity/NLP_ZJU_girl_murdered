import json
import requests
import pandas as pd
import time
import random

url = 'https://comment.news.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/E0RR7QHH0001899O/comments/newList?offset='

commentIds = []  # 评论ID
is_anonymous = []  # 是否匿名
contents = []  # 评论
createTimes = []  # 评论时间
favCounts = []  # 收藏数
IPs = []  # ip
shareCounts = []  # 分享数
againsts = []  # 反对数
votes = []  # 赞成数
sources = []
isDels = []  # 是否删帖
siteNames = []
buildLevels = []  # 评论的层数

user_locations = []  # 用户的位置
user_IDs = []  # 用户ID

pages = []
inds = []

try:
    for page in range(2000):
        URL = url + str(page)
        r = requests.get(URL).text
        json_dict = json.loads(r)
        cmt_dict = json_dict['comments']
        for ind, Id in enumerate(cmt_dict.keys()):
            pages.append(page)
            inds.append(ind)
            commentIds.append(Id)  # 评论ID
            user_IDs.append(cmt_dict[Id]['user']['userId'])  # 用户ID
            is_anonymous.append(cmt_dict[Id]['anonymous'])  # 是否匿名
            contents.append(cmt_dict[Id]['content'])  # 评论
            createTimes.append(cmt_dict[Id]['createTime'])  # 评论时间
            favCounts.append(cmt_dict[Id]['favCount'])  # 喜欢数
            IPs.append(cmt_dict[Id]['ip'])  # ip
            shareCounts.append(cmt_dict[Id]['shareCount'])  # 分享数
            againsts.append(cmt_dict[Id]['against'])  # 反对数
            votes.append(cmt_dict[Id]['vote'])  # 赞成数
            sources.append(cmt_dict[Id]['source'])
            isDels.append(cmt_dict[Id]['isDel'])  # 是否删帖
            siteNames.append(cmt_dict[Id]['siteName'])
            buildLevels.append(cmt_dict[Id]['buildLevel'])  # 评论的层数
            user_locations.append(cmt_dict[Id]['user']['location'])  # 用户的位置

        if page % 100 == 0:
            time.sleep(random.random())  # 每怕一页随机休眠1或2秒，避免对服务器造型干扰
            print('正在爬取第{}页的数据'.format(page))
except:
    pass
print('Done')


df = pd.DataFrame({'commentIds':commentIds, 'user_IDs':user_IDs,
                  'is_anonymous':is_anonymous, 'contents':contents, 'createTimes':createTimes,
                  'favCounts':favCounts, 'IPs':IPs, 'shareCounts':shareCounts, 'againsts':againsts,
                  'votes':votes, 'sources':sources, 'isDels':isDels, 'siteNames':siteNames,
                  'buildLevels':buildLevels, 'user_locations':user_locations })

data = df.drop_duplicates()
data.to_csv('data.csv', index = None)