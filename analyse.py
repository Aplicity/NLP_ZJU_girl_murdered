import pandas as pd
import json
import numpy as np
from os import listdir
import time
import random
import requests
import json
from datetime import datetime
from pyecharts import Bar, Line, Overlap, Map, Geo,WordCloud, Pie
import re
import matplotlib.pyplot as plt
from collections import Counter
import jieba
from snownlp import SnowNLP
import jieba.analyse
import matplotlib as mpl
import seaborn as sns
import nltk
from nltk.draw.dispersion import dispersion_plot


df = pd.read_csv('data.csv')

# 把时间格式换成时间戳
def time2stamp(cmnttime):
    cmnttime = datetime.strptime(cmnttime, '%Y-%m-%d %H:%M:%S')
    stamp = int(datetime.timestamp(cmnttime))
    return stamp

## 对每小时评论数进行统计
df['stamp'] = df['createTimes'].apply(time2stamp)
df['time_mdh'] = df['createTimes'].apply(lambda x:x.split(':')[0][5:])
count_per_hour = df.groupby('time_mdh').count()['commentIds'].to_frame()  # 每小时评论数数据

bar = Bar("每小时评论数")
bar.add("",count_per_hour.index, count_per_hour['commentIds'],
        is_label_show = True ,
        xaxis_rotate = -90, yaxis_interval = 200,yaxis_max = 400,
       is_xaxis_show = True)
bar.render('./images/bar_每小时评论数.html')

line = Line("每小时评论数")
line.add("折线图", count_per_hour.index, count_per_hour['commentIds'],line_opacity=1,line_type='dotted',)
line.render('./images/line_每小时评论数.html')

overlap = Overlap()
overlap.add(bar)
overlap.add(line, is_add_yaxis=True, yaxis_index=1)
overlap.render('./images/overlap_每小时评论数.html') # 使用 render() 渲染生成 .html 文件


## 省份分布统计

def get_pro(area):
    prolist = ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁',
               '吉林', '江苏', '浙江', '安徽', '福建', '江西', '山东',
               '河南', '湖北', '湖南', '广东', '海南', '四川', '贵州',
               '云南', '陕西', '甘肃', '青海', '台湾', '广西', '西藏',
               '宁夏', '新疆', '香港', '澳门', '内蒙古', '黑龙江']
    for pro in prolist:
        if pro in area:
            return pro
    return "海外"
df['pro'] = df['user_locations'].apply(get_pro)
province_count = df.groupby('pro')['pro'].count().sort_values(ascending=False)

bar = Bar("省份分布")
bar.add("省份", province_count.index, province_count.values,
        is_label_show=True, xaxis_interval = 0, xaxis_rotate = 60)
bar.render('./images/bar_省份分布.html')

mapp = Map("省份分布情况", width=1000, height=600)
# mapp.use_theme("macarons") # 换主题
mapp.add("", province_count.index, province_count.values, maptype='china', is_visualmap=True,
         visual_range=[0, 480], is_map_symbol_show=False, visual_text_color='#000', is_label_show=True)
mapp.render('./images/map_省份分布.html')


## 城市分布

prolist = '北京市，天津市，上海市，重庆市，河北省，山西省，辽宁省，吉林省，江苏省，浙江省，安徽省，福建省，\
江西省，山东省，河南省，湖北省，湖南省，广东省，海南省，四川省，贵州省，云南省，陕西省，甘肃省，\
青海省，台湾省，广西，西藏，宁夏，新疆，香港，澳门，内蒙古，黑龙江省'
prolist = prolist.replace('市', '').replace('省', '').split('，')
unchinas = list(set(df[df['pro'] == '海外']['user_locations']))

prolist = ['北京', '天津', '上海', '重庆', '河北', '山西', '辽宁',
           '吉林', '江苏', '浙江', '安徽', '福建', '江西', '山东',
           '河南', '湖北', '湖南', '广东', '海南', '四川', '贵州',
           '云南', '陕西', '甘肃', '青海', '台湾', '广西', '西藏',
           '宁夏', '新疆', '香港', '澳门', '内蒙古', '黑龙江']

df['area'] = df['user_locations'].apply(lambda x: x.replace('省', '').replace('市', ''))

for i in range(len(df)):
    if df.loc[i, 'area'] in unchinas:
        df.loc[i, 'city'] = 'unknow'
    for pro in prolist:
        if pro in df.loc[i, 'area'] and pro not in ['北京', '天津', '上海', '重庆', '香港', '澳门'] and '自治区' not in df.loc[
            i, 'area']:
            df.loc[i, 'city'] = df.loc[i, 'area'][len(pro):]
        if pro in df.loc[i, 'area'] and pro not in ['北京', '天津', '上海', '重庆', '香港', '澳门'] and '自治区' in df.loc[i, 'area']:
            ind = df.loc[i, 'area'].find('自治区') + len('自治区')
            df.loc[i, 'city'] = df.loc[i, 'area'][ind:]

        if pro in df.loc[i, 'area'] and pro in ['北京', '天津', '上海', '重庆', '香港', '澳门']:
            df.loc[i, 'city'] = pro

df['city'] = df['city'].apply(lambda x: 'unknow' if x == '' else x)

city_count = df.groupby('city')['city'].count().sort_values(ascending=False)
city_name = list(city_count.index)
city_values = city_count.values

bar = Bar("城市分布")
bar.add("城市", city_count.index[:30], city_count.values[:30], is_label_show=True, xaxis_interval=0, xaxis_rotate=-45)
bar.render('./images/bar_城市分布.html')

city_data = list(zip(city_count.index, city_count.values))

geo = Geo("城市分布情况", "data from SinaNews", title_color="#fff",
          width=900, height=700, background_color='#404a59')

working_city = []
working_value = []
attrs, values = geo.cast(city_data)
for attr, value in zip(attrs, values):
    name_list = ['上海']
    name_list.append(attr)

    value_list = [169]
    value_list.append(value)
    try:
        geo.add("城市分布情况", name_list, value_list, visual_range=[0, 360], visual_text_color="#fff",
                symbol_size=10, is_visualmap=True)
        working_city.append(attr)
        working_value.append(value)
    except:
        pass

geo.add("城市分布情况", working_city, working_value, visual_range=[0, 180], visual_text_color="#fff",
        symbol_size=10, is_visualmap=True)

geo.render('./images/geo_城市分布情况.html')

## 删帖情况统计
isDels_count = df.groupby('isDels')['isDels'].count()
pie = Pie('被发布者删去的评论占比',title_pos='center')
pie.add('只有0.4%的评论被删', isDels_count.index , isDels_count.values , is_label_show = True,
       lrosetype = 'radius', radius=[40, 75], rosetype="area",is_legend_show = True ,
       is_random=True, legend_orient="vertical")
pie.render('./images/pie_被发布者删去的评论占比.html')

## 匿名情况
is_anonymous_count = df.groupby('is_anonymous')['isDels'].count()
pie = Pie('匿名评论占比',title_pos='center')
pie.add('', is_anonymous_count.index , is_anonymous_count.values , is_label_show = True,
       lrosetype = 'radius' ,is_legend_show = True ,
       is_random=True, legend_orient="vertical")
pie.render('./images/pie_匿名评论占比.html')

## 通过正则提取表情emojo,表情统计
def get_emoji(content):
    pattern =re.compile(u"\[[a-zA-Z\u4e00-\u9fa5]+\]")
    result=re.findall(pattern,content)
    return result
df['emojis_list'] = df['contents'].apply(get_emoji)

emojis = df['emojis_list'].values.tolist()
emojis_list = sum(emojis, [])
emojis_set = list(set(emojis_list))
counter = Counter(emojis_list)
y_emojis, x_counts = zip(*counter.most_common())

bar = Bar("表情使用情况")
bar.add("", y_emojis[:20], x_counts[:20],
        is_stack = True, is_label_show = True,
        xaxis_interval = 0, xaxis_rotate = 45, xaxis_margin = 8)
bar.render('./images/bar_表情使用情况.html')

## NLTK 分布图谱
cmnts_list = df['contents'].values.tolist()
cmnts = ' '.join(cmnts_list)
emoji_drop = []
for emojis in y_emojis:
    emoji = emojis[1:-1] # 去掉括号
    jieba.add_word(emoji) # 读者可将上一行注释掉，看看分词结果
    emoji_drop.append(emoji) # 将去掉括号后的emoji单独保存
words = list(jieba.cut(cmnts))

plt.rcParams['font.sans-serif'] = ['SimHei']
ntext = nltk.Text(words)
ntext.dispersion_plot(emoji_drop[:15])


## 评论情感分析
def sentiment(content):
    s = SnowNLP(content)
    return s.sentiments

# sentiment的值越接近1，说明评论越友好，0为最不友好
df['sentiment'] = df.contents.apply(sentiment)
df_sent = df[['contents', 'sentiment','votes','againsts']]
# 把结果保存为 csv文件
df_sent.sort_values(by=['sentiment'],ascending=False).to_csv('emotion_analy_result.csv', index = None)
df_sent.sort_values(by=['sentiment'],ascending=False).head()

# 评论的情感评分、点赞数、反对数的相关分析-- 热力图
fig, ax = plt.subplots(figsize = (7,7))
corr_mat = df_sent.corr()
sns.heatmap(corr_mat ,cmap="YlGnBu", xticklabels= True, yticklabels= True, square=True, annot=True)

## 基于 TF-IDF 算法的关键词抽取，并做成词云图
all_content = df['contents'].values.tolist()
extract_tags = "  ".join(jieba.analyse.extract_tags(' '.join(all_content), topK=200, withWeight=False, allowPOS=('ns', 'n')))

segment = []
for line in all_content:
    try:
        segs = jieba.lcut(line)
        for seg in segs:
            if len(seg)>1 and seg != '\r\n':
                segment.append(seg)
    except:
        print(line)
        continue
# 去停用词
words_df = pd.DataFrame({"segment": segment})

words_stat = words_df.groupby(by=['segment'])['segment'].agg({"计数": np.size})
words_stat = words_stat.reset_index().sort_values(by=["计数"], ascending=False)

wordcloud = WordCloud(width=800, height=520)
wordcloud.add("评论词云", words_stat['segment'], words_stat['计数'], word_size_range=[20, 100])
wordcloud.render('./images/wc_评论词云.html')

plt.show()
sns.plt.show()

print('done')

