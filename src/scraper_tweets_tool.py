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

heroku_uri = os.environ.get("HEROKU_URI")
supabase_uri = os.environ.get("SUPABASE_URI")

heroku_con = psycopg2.connect(heroku_uri, sslmode='require')
heroku_cur = heroku_con.cursor()

supabase_con = psycopg2.connect(supabase_uri, sslmode='require')
supabase_cur = supabase_con.cursor()

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
                if i>2000:
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
    
    def delete_repeated_results(self):
        sql_query = """DELETE FROM historical_tweets
                        WHERE id IN
                            (SELECT id
                            FROM 
                                (SELECT id,
                                ROW_NUMBER() OVER( PARTITION BY text
                                ORDER BY  id ) AS row_num
                                FROM historical_tweets ) t
                                WHERE t.row_num > 1 );"""
        supabase_cur.execute(sql_query)
        supabase_con.commit()
        supabase_con.close()
