import re
from sklearn.feature_extraction.text import CountVectorizer

def preprocessing_data(df, stop_port):
    df = df.apply(lambda x: x.lower())
    df = df.apply(lambda x: re.sub(r"http\S+","", x))
    df = df.apply(lambda x: re.sub(r"www.\S+","", x))
    df = df.apply(lambda x: x.rstrip())
    df = df.apply(lambda x: re.sub("[^a-z0-9]"," ", x))
    df = df.apply(lambda x: x.split())
    df = df.map(lambda x: ' '.join([word for word in x if word not in (stop_port)])) 

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