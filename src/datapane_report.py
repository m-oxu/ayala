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
"unicodedata2==14.0.0"]

install_packages(requirement_list)

import datapane as dp
from utils import preprocessing_data, get_top_n_bigram, get_top_n_trigram, get_top_n_words
from datetime import datetime, timedelta
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

supabase_uri = os.environ.get("SUPABASE_URI")
con = psycopg2.connect(supabase_uri, sslmode='require')
cur = con.cursor()

sql = "select * from historical_tweets"

cur.execute(sql)
tupples = cur.fetchall()
con.close()
df = pd.DataFrame(tupples, columns=['datetime', 'tweet_id', 'text', 'username', "verified", "followers", "location", "likes", "retweets", "id"])

#########################################################################################################################
################################################## Data Pre-processing ##################################################
#########################################################################################################################

df.datetime = pd.to_datetime(df.datetime)
# Importing stopwords from assets/data
      
stop_port = requests.get("https://raw.githubusercontent.com/m-oxu/ayala/main/src/stopwords-pt.txt").text.split()

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
plot_hashtags = px.histogram(data_frame=hashtags_df[:30], x='hashtags', y='count', template='plotly_white', title="As 30 Maiores Hashtags", width=900, height=600)
plot_hashtags.update_xaxes(categoryorder='total descending', title='Hashtags').update_yaxes(title='Count')

# Mentions
mentions_df = df.mentions.value_counts().reset_index().rename(columns={'index':'mentions', 'mentions':'count'})
plot_mentions = px.histogram(data_frame=mentions_df[:30], x='mentions', y='count', template='plotly_white', title="As 30 Maiores Menções", width=900, height=600)
plot_mentions.update_xaxes(categoryorder='total descending', title='Mentions').update_yaxes(title='Count')

# Unigram counts
common_words = get_top_n_words(df['clean_text'], 30)    
df1 = pd.DataFrame(common_words, columns = ['review', 'count'])
plot_unigram_words = px.histogram(data_frame=df1, x='review', y='count', template='plotly_white', title="Quantidade de Ocorrências de Unigramas", width=900, height=600)
plot_unigram_words.update_xaxes(categoryorder='total descending', title='Unigram Words').update_yaxes(title='Count')

# Bigram counts
common_words2 = get_top_n_bigram(df['clean_text'], 30)
df2 = pd.DataFrame(common_words2, columns=['review', "count"])
plot_bigram_words = px.histogram(data_frame=df2, x='review', y='count', template='plotly_white', title="Quantidade de Ocorrências de Bigramas", width=900, height=600)
plot_bigram_words.update_xaxes(categoryorder='total descending', title='Bigram Words').update_yaxes(title='Count')

# Trigram counts
common_words3 = get_top_n_trigram(df['clean_text'], 30)
df3 = pd.DataFrame(common_words3, columns = ['review' , 'count'])
plot_trigram_words = px.histogram(data_frame=df3, template='plotly_white', x='review', y='count', title="Quantidade de Ocorrências de Trigramas", width=900, height=600)
plot_trigram_words.update_xaxes(categoryorder='total descending', title='Trigram Words').update_yaxes(title='Count')

# Number of tweets per date
fig_tweets_por_data = px.histogram(df, x='datetime', template='plotly_white', title='Número de tweets por Data', width=900, height=600)
fig_tweets_por_data.update_xaxes(categoryorder='category descending', title='Date').update_yaxes(title='Número de tweets')

# Number of tweets per word count
fig_quantidade_de_palavras = px.histogram(df, x='word_count', template='plotly_white', title='Número de tweets por quantidade de palavras', width=900, height=600)
fig_quantidade_de_palavras.update_xaxes(categoryorder='total descending', title='Número de palavras').update_yaxes(title='Número de tweets')

# Number of tweets added since last week
tweets_last_week = (df.datetime.dt.date > pd.to_datetime(str(pd.to_datetime(datetime.today() - timedelta(days=7))).split()[0])).value_counts().iloc[1]

# Likes in time
date_x_likes_plot = px.histogram(df, x='datetime', y='likes', template='plotly_white', width=900, height=600, title='Quantidade de Likes no Tempo')
date_x_likes_plot.update_xaxes(categoryorder='category descending', title='Date').update_yaxes(title='Número de Likes')

# Verified count
verified_df = df.verified.value_counts().reset_index().rename(columns={'index':'verified', 'verified':'count'})

# Followers x likes
followers_x_likes_plot = px.scatter(data_frame=df, x='followers', y='likes', template='plotly_white', title='Quantidade de Seguidores X Likes em Tweets', width=900, height=600)

# Followers x retweets
followers_x_retweets_plot = px.scatter(data_frame=df, x='followers', y='retweets', template='plotly_white', title='Quantidade de Seguidores X Retweets', width=900, height=600)
followers_x_retweets_plot

# Retweets in time
date_x_retweets_plot = px.histogram(df, x='datetime', y='retweets', template='plotly_white', width=900, height=600, title='Quantidade de Retweets no Tempo')
date_x_retweets_plot.update_xaxes(categoryorder='category descending', title='Date').update_yaxes(title='Número de Retweets')

# Username
username_df = df.username.value_counts().reset_index().rename(columns={'index':'username', 'username':'count'})
username_plot = px.histogram(data_frame=username_df[:30], template='plotly_white', x='username', y='count', title='Quantidade de Usuários')
username_plot.update_xaxes(categoryorder='total descending', title='Mentions').update_yaxes(title='Count')

# Location plot

location_df = df.location.value_counts().reset_index().rename(columns={'index':'location','location':'count'})
location_plot = px.histogram(data_frame=location_df[:30], template='plotly_white', x='location', y='count', title='Localizações')
location_plot.update_xaxes(categoryorder='total descending', title='Location').update_yaxes(title='Count')

# Building report in Datapane
report = dp.Report(
   dp.Group(
      dp.BigNumber(
         heading="Número de Tweets Armazenados", 
         value=f"{len(df):,}",
         change=f"{tweets_last_week:,} since last week",
         is_upward_change=True
      ),
      dp.BigNumber(
        heading='Usuários Verificados',
        value=f"{verified_df.values[1][1]:,}"
      ),
      dp.BigNumber(
          heading='Usuários Não-Verificados',
          value=f"{verified_df.values[0][1]:,}"
      ), columns=3
   ),
   dp.Plot(wordcloud_figure),
    dp.Plot(fig_tweets_por_data),
    dp.Plot(plot_mentions),
    dp.Plot(plot_hashtags),
   dp.Group(
       dp.Plot(date_x_likes_plot),
       dp.Plot(date_x_retweets_plot), columns=2
   ),
   dp.Group(
       dp.Plot(followers_x_likes_plot),
       dp.Plot(followers_x_likes_plot), columns=2
   ),
   dp.Plot(location_plot),
    dp.Group(
        dp.Plot(plot_unigram_words),
        dp.Plot(plot_bigram_words), columns=2),
    dp.Plot(plot_trigram_words),
    dp.Plot(fig_quantidade_de_palavras),
    dp.DataTable(df.sample(1000))
)

report.upload(name="Ayala Project Report", 
              publicly_visible=True)
