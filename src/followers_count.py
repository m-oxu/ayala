from dotenv import Any, load_dotenv
import os
import psycopg2
import requests
import pandas as pd
import snscrape.modules.twitter as sntwitter
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import tweepy

# Credentials
load_dotenv('.env') 

access_token = os.environ.get("ACCESS_TOKEN")
access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")

api_key = os.environ.get("API_KEY")
api_key_secret = os.environ.get("API_SECRET_KEY")
api_token = os.environ.get("API_TOKEN")
supabase_uri = os.environ.get("SUPABASE_URI")

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

def followers_count(self):
    followers_list = []
    for i in id:
        # fetching the user
        user = api.get_user(screen_name=i)
        followers_list.append([datetime.now(), user.followers_count, user.id, user.screen_name])
    followers_list_df = pd.DataFrame(followers_list, columns=['created_at', 'followers_count', 'id', 'username'])
    for i in followers_list_df.index:

        sql_query = """
            INSERT INTO followers_candidate (created_at, 
                                        followers_count, 
                                        id, 
                                        username) values('%s', '%s', '%s', '%s')
            ON CONFLICT DO NOTHING;
        """ %  (followers_list_df['created_at'][i], 
                followers_list_df['followers_count'][i], 
                followers_list_df['id'][i], 
                followers_list_df['username'][i]) 

        supabase_cur.execute(sql_query)
    supabase_con.commit()
