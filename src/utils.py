import re
from sklearn.feature_extraction.text import CountVectorizer
import unicodedata2 as unicodedata
import requests
from pandasql import sqldf
from datetime import datetime, timedelta, date
import pandas as pd

stop_port = requests.get("https://raw.githubusercontent.com/m-oxu/ayala/main/src/stopwords-pt.txt").text.split()
def preprocessing_data(df):
    nfkd = unicodedata.normalize('NFKD', df)
    df = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    df = df.lower()
    df = re.sub(r"http\S+","", df)
    df = re.sub(r"www.\S+","", df)
    df = re.sub(r"@[A-Za-z0-9_]+","", df)
    df = re.sub(r"#[A-Za-z0-9_]+","", df)
    df = df.rstrip()
    df = re.sub("[^a-z0-9]"," ", df)
    df = df.split()
    df = ' '.join([word for word in df if word not in (stop_port)])

    return df

def get_top_n_words(corpus, n=None):
    vec=CountVectorizer().fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq = sorted(words_freq, key = lambda x: x[1], reverse=True)
    return words_freq[:n]

def get_top_n_bigram(corpus, n=None):
    vec = CountVectorizer(ngram_range=(2,2)).fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True)
    return words_freq[:n]

def get_top_n_trigram(corpus, n=None):
    vec = CountVectorizer(ngram_range=(3, 3), stop_words='english').fit(corpus)
    bag_of_words = vec.transform(corpus)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    words_freq =sorted(words_freq, key = lambda x: x[1], reverse=True)
    return words_freq[:n]

def difference_today_yt(df):
    df['date'] = pd.to_datetime(df.created_at).dt.date
    today_date = date.today() - timedelta(days=1)
    last_week_date = date.today() - timedelta(days=7)
    today_followers = df.query("date == @today_date").followers_count.max()
    last_week_followers = df.query("date == @last_week_date").followers_count.max()
    difference = today_followers - last_week_followers
    return today_followers, round(100 * (difference / last_week_followers), 4)

def growth_rate(username, df):
    df['date'] = pd.to_datetime(df.datetime).dt.date
    today_date = date.today() - timedelta(days=1)
    last_week_date = date.today() - timedelta(days=7)

    df_username = df.query('mentions == @username')
    mention_today = len(df_username.query('date == @today_date'))
    mention_last_week = len(df_username.query('date == @last_week_date'))
    total_mentions_week = len(df_username.query('date <= @today_date and date >= @last_week_date'))
    
    if mention_last_week != 0:
        difference_td_lw = mention_today - mention_last_week
        rate_percentual = 100 * (difference_td_lw/mention_last_week)
        return rate_percentual, total_mentions_week
    else:
        return 0, total_mentions_week
    
    

def is_positive(value):
    return value > 0
