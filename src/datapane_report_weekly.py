
from requirements_install import install_packages
requirement_list = ["python-dotenv==0.20.0",
"psycopg2-binary==2.9.3",
"pandas==1.4.2",
"sqlalchemy==1.4.36",
"datapane==0.14.0",
"unidecode==1.3.4",
"wordcloud==1.8.1",
"yellowbrick==1.4",
"scikit-learn==1.0.2",
"plotly==5.7.0",
"unicodedata2==14.0.0",
"pandasql==0.7.3"]

install_packages(requirement_list)

import datapane as dp
from utils import preprocessing_data, get_top_n_bigram, get_top_n_trigram, get_top_n_words, difference_today_yt, is_positive, growth_rate
from datetime import datetime, timedelta, date
import pandas as pd
import psycopg2
import re
from unidecode import unidecode
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.feature_extraction.text import CountVectorizer
from yellowbrick.text import FreqDistVisualizer
import datapane as dp
from dotenv import Any, load_dotenv
import os
from datapane.client.api.report.blocks import BigNumber
import requests
from pandasql import sqldf

load_dotenv('.env')
supabase_uri = os.environ.get("SUPABASE_URI")
con = psycopg2.connect(supabase_uri, sslmode='require')
cur = con.cursor()

sql = "select * from historical_tweets"

cur.execute(sql)
tupples = cur.fetchall()
con.close()
df = pd.DataFrame(tupples, columns=['datetime', 
                                    'tweet_id', 
                                    'text', 
                                    'username', 
                                    "verified", 
                                    "followers", 
                                    "location", 
                                    "likes", 
                                    "retweets", 
                                    "id"])

#########################################################################################################################
################################################## Data Pre-processing ##################################################
#########################################################################################################################
df.datetime = pd.to_datetime(df.datetime)
df['date'] = df.datetime.dt.date

today_date = date.today() - timedelta(days=1)
last_week_date = date.today() - timedelta(days=8)
df = df.query("date <= @today_date and date >= @last_week_date")

df.datetime = pd.to_datetime(df.datetime)
# Importing stopwords from src
      
stop_port = requests.get("https://raw.githubusercontent.com/m-oxu/ayala/main/src/stopwords-pt.txt").text.split()
stop_port = [unidecode(i) for i in stop_port]

df['clean_text'] = df.text.apply(preprocessing_data)

#########################################################################################################################
################################################## Data Enrichment ######################################################
#########################################################################################################################

# Extracting mentions from tweets
df['mentions'] = df.text.apply(lambda x: re.findall(f'.*(@\S+).*', 
                                    x.lower())).apply(lambda x: x[0] if x else None)

# Extracting hastags from tweets
df['hashtags'] = df.text.apply(lambda x: re.findall(f'.*(#\S+).*', 
                                    x.lower())).apply(lambda x: x[0] if x else None)


# Extracting the number of letters and words from each tweet
df['tweet_len'] = df['text'].astype(str).apply(len)
df['word_count'] = df['text'].apply(lambda x: len(str(x).split()))

#########################################################################################################################
################################################## Data Visualizations ##################################################
#########################################################################################################################

# Generating a wordcloud
text = " ".join(review for review in df.clean_text)
max = len(text)
wordcloud = WordCloud(max_font_size = 50, 
                  max_words = max, 
                  stopwords = stop_port,
                  background_color='white').generate(text)

wordcloud_figure = plt.figure(figsize=(15, 10))
plt.imshow(wordcloud, interpolation = "bilinear")
plt.axis("off")

# Hashtags
hashtags_df = df.hashtags.value_counts().reset_index().rename(columns={'index':'hashtags', 'hashtags':'count'})
plot_hashtags = px.histogram(data_frame=hashtags_df[:30], x='hashtags', y='count', 
                             template='plotly_white', 
                             title="As 30 Maiores Hashtags", 
                             width=900, height=600)
plot_hashtags.update_xaxes(categoryorder='total descending', title='Hashtags').update_yaxes(title='Count')

# Mentions
mentions_df = df.mentions.value_counts().reset_index().rename(columns={'index':'mentions', 'mentions':'count'})
plot_mentions = px.histogram(data_frame=mentions_df[:30], x='mentions', y='count', 
                             template='plotly_white', 
                             title="As 30 Maiores Men????es", 
                             width=900, height=600)
plot_mentions.update_xaxes(categoryorder='total descending', title='Mentions').update_yaxes(title='Count')

# Unigram counts
common_words = get_top_n_words(df['clean_text'], 30)    
df1 = pd.DataFrame(common_words, columns = ['review', 'count'])
plot_unigram_words = px.histogram(data_frame=df1, x='review', y='count', 
                                  template='plotly_white', 
                                  title="Quantidade de Ocorr??ncias de Unigramas", 
                                  width=900, height=600)
plot_unigram_words.update_xaxes(categoryorder='total descending', title='Unigram Words').update_yaxes(title='Count')

# Bigram counts
common_words2 = get_top_n_bigram(df['clean_text'], 30)
df2 = pd.DataFrame(common_words2, columns=['review', "count"])
plot_bigram_words = px.histogram(data_frame=df2, x='review', y='count', 
                                 template='plotly_white', title="Quantidade de Ocorr??ncias de Bigramas", 
                                 width=900, height=600)
plot_bigram_words.update_xaxes(categoryorder='total descending', title='Bigram Words').update_yaxes(title='Count')

# Trigram counts
common_words3 = get_top_n_trigram(df['clean_text'], 30)
df3 = pd.DataFrame(common_words3, columns = ['review' , 'count'])
plot_trigram_words = px.histogram(data_frame=df3, template='plotly_white', x='review', y='count', 
                                  title="Quantidade de Ocorr??ncias de Trigramas", 
                                  width=900, height=600)
plot_trigram_words.update_xaxes(categoryorder='total descending', title='Trigram Words').update_yaxes(title='Count')

# Number of tweets per word count
fig_quantidade_de_palavras = px.histogram(df, x='word_count', 
                                          template='plotly_white', 
                                          title='N??mero de tweets por quantidade de palavras', 
                                          width=900, height=600)
fig_quantidade_de_palavras.update_xaxes(categoryorder='total descending', title='N??mero de palavras').update_yaxes(title='N??mero de tweets')

# Number of tweets added since last week
tweets_last_week = (df.datetime.dt.date > pd.to_datetime(str(pd.to_datetime(datetime.today() - timedelta(days=7))).split()[0])).value_counts().iloc[1]

# Followers x likes
followers_x_likes_plot = px.scatter(data_frame=df, x='followers', y='likes', 
                                    template='plotly_white', 
                                    title='Quantidade de Seguidores X Likes em Tweets', 
                                    width=900, height=600)

# Followers x retweets
followers_x_retweets_plot = px.scatter(data_frame=df, x='followers', y='retweets', 
                                       template='plotly_white', 
                                       title='Quantidade de Seguidores X Retweets', 
                                       width=900, height=600)
followers_x_retweets_plot


# Username
username_df = df.groupby('username').text.count().reset_index().sort_values('text', ascending=False)
username_plot = px.histogram(data_frame=username_df[:30], template='plotly_white', x='username', y='text', title='Os 30 Usu??rios mais Engajados')
username_plot.update_xaxes(categoryorder='total descending', title='Usu??rios').update_yaxes(title='N??mero de tweets')


# Followers plot 
con = psycopg2.connect(supabase_uri, sslmode='require')
cur = con.cursor()

sql = "select * from followers_candidate"

cur.execute(sql)
tupples = cur.fetchall()
con.close()
df_followers = pd.DataFrame(tupples, columns=['id', 'tweet_id', 'created_at', 'username', 'followers_count'])
plot_followers = px.line(data_frame=df_followers, x='created_at', y='followers_count', 
                         color='username', template='plotly_white', 
                         title='Quantidade de Seguidores por Pessoa Pr??-Candidata', 
                         width=900, height=600)
plot_followers.update_xaxes(title='Quantidade de Seguidores').update_yaxes(title='Data')

def query_followers(username):
    pysqldf = lambda q: sqldf(q, globals())
    query_bl = f"""SELECT * 
       FROM df_followers 
       WHERE username LIKE "%{username}%" ORDER BY followers_count desc;"""

    return pysqldf(query_bl)

# N??mero de seguidores por pr??-candidato
jairbolsonaro = query_followers('jairbolsonaro')
veralucia = query_followers('verapstu')
leopericles = query_followers('LeoPericlesUP')
lula = query_followers('LulaOficial')
ajanones = query_followers('AndreJanonesAdv')
cirogomes = query_followers('cirogomes')
lfdavila = query_followers('lfdavilaoficial')

jairbolsonaro_today_fol, jairbolsonaro_seg_diff = difference_today_yt(jairbolsonaro)
veralucia_today_fol, veralucia_seg_diff = difference_today_yt(veralucia)
leopericles_today_fol, leopericles_seg_diff = difference_today_yt(leopericles)
lula_today_fol, lula_seg_diff = difference_today_yt(lula)
ajanones_today_fol, ajanones_seg_diff = difference_today_yt(ajanones)
lfdavila_today_fol, lfdavila_seg_diff = difference_today_yt(lfdavila)
cirogomes_today_fol, cirogomes_seg_diff = difference_today_yt(cirogomes)

# Percentual de men????es

gr_jair, jairbolsonaro_mentions = growth_rate('@jairbolsonaro', df)
gr_lula, lula_mentions = growth_rate('@lulaoficial', df)
gr_vera, vera_mentions = growth_rate('@verapstu', df)
gr_janones, janones_mentions = growth_rate('@andrejanonesadv', df)
gr_leo, leo_mentions = growth_rate('@leopericlesup', df)
gr_ciro, cirogomes_mentions = growth_rate('@cirogomes', df)
gr_davila, davila_mentions = growth_rate('@lfdavilaoficial', df)

df['date'] = pd.to_datetime(df.datetime).dt.date
today_date_tweet = date.today()
yesterday_date_tweet = today_date_tweet - timedelta(days=7)
difference_tweets = len(df.query("date == @today_date_tweet")) - len(df.query("date == @yesterday_date_tweet"))


report = dp.Report(
    dp.BigNumber(
        heading="N??mero de Tweets Armazenados essa Semana", 
        value=f"{len(df):,}",
        change=f"{(difference_tweets * -1):,}",
        is_upward_change=is_positive(difference_tweets)),
    dp.Group(
        dp.BigNumber(heading="Seguidores de @jairbolsonaro",
                    value=f"{jairbolsonaro_today_fol:,}",
                    change=f"{jairbolsonaro_seg_diff}%",
                    is_upward_change=is_positive(jairbolsonaro_seg_diff),
                    name='jairfollowers'),
        dp.BigNumber(heading="Seguidores de @LulaOficial",
                    value=f"{lula_today_fol:,}",
                    change=f"{lula_seg_diff}%",
                    is_upward_change=is_positive(lula_seg_diff),
                    name='lulafollowers'),
        dp.BigNumber(heading="Seguidores de @cirogomes",
                    value=f"{cirogomes_today_fol:,}",
                    change=f"{cirogomes_seg_diff}%",
                    is_upward_change=is_positive(cirogomes_seg_diff),
                    name='cirofollowers'), columns=3),
    dp.Group(
        dp.BigNumber(heading="Seguidores de Jair @LeoPericlesUP",
                    value=f"{leopericles_today_fol:,}",
                    change=f"{leopericles_seg_diff}%",
                    is_upward_change=is_positive(leopericles_seg_diff),
                    name='leofollowers'),
        dp.BigNumber(heading="Seguidores de @AndreJanonesAdv",
                    value=f"{ajanones_today_fol:,}",
                    change=f"{ajanones_seg_diff}%",
                    is_upward_change=is_positive(ajanones_seg_diff),
                    name='janonesfollowers'),
        dp.BigNumber(heading="Seguidores de @verapstu",
                    value=f"{veralucia_today_fol:,}",
                    change=f"{veralucia_seg_diff}%",
                    is_upward_change=is_positive(veralucia_seg_diff),
                    name='verafollowers'),
        dp.BigNumber(heading="Seguidores de @lfdavilaoficial",
                    value=f"{lfdavila_today_fol:,}",
                    change=f"{lfdavila_seg_diff}%",
                    is_upward_change=is_positive(lfdavila_seg_diff),
                    name='felipefollowers'), columns=4
    ),
   dp.Plot(plot_followers),
    dp.Plot(wordcloud_figure),
  dp.Group(
  dp.BigNumber(heading="Men????es Totais dessa Semana de @jairbolsonaro",
              value=f"{jairbolsonaro_mentions:,}",
              change=f"{round(gr_jair, 6)}%",
              is_upward_change=is_positive(gr_jair)),
  dp.BigNumber(heading="Men????es Totais dessa Semana de @lulaoficial",
              value=f"{lula_mentions:,}",
              change=f"{round(gr_lula, 6)}%",
              is_upward_change=is_positive(gr_lula)),
  dp.BigNumber(heading="Men????es Totais dessa Semana de @cirogomes",
              value=f"{cirogomes_mentions:,}",
              change=f"{round(gr_ciro, 6)}%",
              is_upward_change=is_positive(gr_ciro)),
  columns=3),
  dp.Group(
    dp.BigNumber(heading="Men????es Totais dessa Semana de @leopericlesup",
              value=f"{leo_mentions:,}",
              change=f"{round(gr_leo, 6)}%",
              is_upward_change=is_positive(gr_leo)),
  dp.BigNumber(heading="Men????es Totais dessa Semana de @veralucia",
              value=f"{vera_mentions:,}",
              change=f"{round(gr_vera, 6)}%",
              is_upward_change=is_positive(gr_vera)),
  dp.BigNumber(heading="Men????es Totais dessa Semana de @andrejanonesadv",
              value=f"{janones_mentions:,}",
              change=f"{round(gr_janones, 6)}%",
              is_upward_change=is_positive(gr_janones)),
  dp.BigNumber(heading="Men????es Totais dessa Semana de @dfdavilaoficial",
              value=f"{davila_mentions:,}",
              change=f"{round(gr_davila, 6)}%",
              is_upward_change=is_positive(gr_davila)),
  columns=4),
    dp.Plot(plot_mentions),
    dp.Plot(plot_hashtags),
   dp.Group(
       dp.Plot(followers_x_likes_plot),
       dp.Plot(followers_x_retweets_plot), columns=2
   ),
    dp.Group(
        dp.Plot(plot_unigram_words),
        dp.Plot(plot_bigram_words), columns=2),
    dp.Plot(plot_trigram_words),
    dp.Plot(fig_quantidade_de_palavras),
    dp.DataTable(df.sample(1000))
)

report.upload(name=f"Ayala Project - Political Report Weekly ({today_date})", 
              publicly_visible=True)
