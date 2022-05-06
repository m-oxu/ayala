import re
from sklearn.feature_extraction.text import CountVectorizer
import unicodedata2 as unicodedata
import requests
from pandasql import sqldf
from datetime import datetime, timedelta

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

def query_followers(username):
    pysqldf = lambda q: sqldf(q, globals())
    query_bl = f"""SELECT * 
       FROM df_followers 
       WHERE username LIKE "%{username}%" ORDER BY followers_count desc;"""

    return pysqldf(query_bl)

def difference_today_yt(df):
    df['date'] = (pd.to_datetime(df.created_at).dt.date).astype('str')
    today_date = str(pd.to_datetime(datetime.now())).split()[0]
    yesterday_date = str(pd.to_datetime(datetime.now() - timedelta(days=1))).split()[0]
    today_followers = df.query("date == @today_date").followers_count.max()
    difference = df.query("date == @today_date").followers_count.max() - df.query("date == @yesterday_date").followers_count.max()
    return today_followers, difference

def is_positive(value):
    return value > 0
