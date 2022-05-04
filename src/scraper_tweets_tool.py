# sourcery skip: avoid-builtin-shadow
import tweepy
from dotenv import Any, load_dotenv
import os
import psycopg2
import requests
import pandas as pd
import snscrape.modules.twitter as sntwitter
from datetime import datetime, timedelta
from sqlalchemy import create_engine

# Credentials
load_dotenv('.env') 

access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

api_key = os.environ.get("API_KEY")
api_key_secret = os.environ.get("API_SECRET_KEY")
api_token = os.environ.get("API_TOKEN")

heroku_uri = os.environ.get("HEROKU_URI")
supabase_uri = os.environ.get("SUPABASE_URI")

heroku_con = psycopg2.connect(heroku_uri, sslmode='require')
heroku_cur = heroku_con.cursor()

supabase_con = psycopg2.connect(supabase_uri, sslmode='require')
supabase_cur = supabase_con.cursor()

# authorization of consumer key and consumer secret
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# the ID of the user
id = {"@jairbolsonaro": 128372940, 
      "@verapstu": 634712862, 
      "@leopericlesup": 983340254081048576, 
      "@lulaoficial": 2670726740, 
      "@cirogomes": 33374761, 
      "@lfdavilaoficial": 900831846258413568,
      "@andrejanonesadv": 1198004545}

class TwitterSearch:

    def __init__(self, query_list=None, tweet_fields=None, max_results=100):
        self.query_list = query_list
        self.tweet_fields = tweet_fields
        self.max_results = max_results

    def get_query_list(self) -> list:

        sql = "select * from queries"

        heroku_cur.execute(sql)
        tupples = heroku_cur.fetchall()
        df = pd.DataFrame(tupples, columns=['id', 'query'])
        self.query_list = list(df['query'])
        return self.query_list


    def search_on_twitter(self):
        # Creating list to append tweet data to
        query_list = self.query_list
        self.tweet_list = []
        for query in query_list:
            # Using TwitterSearchScraper to scrape data since yesterday until now and append tweets to list
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(f"""{query} 
                                                                    since:{(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")} 
                                                                    until:{datetime.now().strftime("%Y-%m-%d")}""").get_items()):
                if i>1000:
                    break
                self.tweet_list.append([tweet.date, 
                                        tweet.id, 
                                        tweet.content, 
                                        tweet.user.username, 
                                        tweet.user.verified, 
                                        tweet.user.followersCount, 
                                        tweet.user.location, 
                                        tweet.likeCount, 
                                        tweet.retweetCount])
        return self.tweet_list
    
    def turn_list_in_dataframe(self):
        self.df = pd.DataFrame(self.tweet_list, columns=['datetime', 
                                                    'tweet_id', 
                                                    'text', 
                                                    'username', 
                                                    "verified", 
                                                    "followers", 
                                                    "location", 
                                                    "likes", 
                                                    "retweets"])
        
        self.df.text = self.df.text.astype('str').str.replace("'", "") 
        self.df.location = self.df.location.str.replace("'", "")
        return self.df

    def insert_data_in_postgresql(self):
        for i in self.df.index:
            sql_query = """
                        INSERT INTO historical_tweets (datetime, 
                                                tweet_id, 
                                                text, 
                                                username, 
                                                verified, 
                                                followers, 
                                                location, 
                                                likes, 
                                                retweets) values('%s','%s','%s','%s','%s','%s','%s','%s','%s')
                        ON CONFLICT DO NOTHING;
                    """ % (self.df['datetime'][i],
                            self.df['tweet_id'][i], 
                            self.df['text'][i],
                            self.df['username'][i],
                            self.df['verified'][i],
                            self.df['followers'][i],
                            self.df['location'][i],
                            self.df['likes'][i],
                            self.df['retweets'][i]
                            )


            supabase_cur.execute(sql_query)
        supabase_con.commit()
    
    def followers_count(self):
        for i in id:
            # fetching the user
            user = api.get_user(screen_name=i)

            sql_query = """
                INSERT INTO followers_count (date, 
                                            followers_count, 
                                            id, 
                                            nome) values('%s', '%s', '%s', '%s')
                ON CONFLICT DO NOTHING;
            """ %  (datetime.now(), user.followers_count, user.id, user.screen_name) 
            heroku_cur.execute(sql_query)
        heroku_con.commit()