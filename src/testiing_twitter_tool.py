import tweepy
from dotenv import load_dotenv
import os
import psycopg2
from datetime import datetime, timedelta, timezone

# Credentials
load_dotenv('.env') 

access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

api_key = os.getenv("API_KEY")
api_key_secret = os.getenv("API_SECRET_KEY")
api_token = os.getenv("API_TOKEN")



database_host = os.getenv("HOST")
database_user = os.getenv("USER")
database_password = os.getenv("PASSWORD")
database_name = os.getenv("DATABASE")
database_uri = os.getenv("URI")

con = psycopg2.connect(database_uri, sslmode='require')
cur = con.cursor()

auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth, wait_on_rate_limit=True)

querys = ['#Lula2022 OR #LulaLadrao -filter:retweets','bolsonaro desonesto -filter:retweets']

tweets_per_query = 1
maxId = -1
tweetCount = 0

for i in querys:
    newTweets = tweepy.Cursor(api.search_tweets, q=i, count=tweets_per_query, lang='pt', tweet_mode="extended")

    val = []
    quote_count = 0
    retweeted = 0
    for tweet in newTweets.items():
        id = tweet.id
        id = str(id)
        created_at = tweet.created_at
        text = tweet.full_text.encode('utf-8')
        source = tweet.source
        in_reply_to_status_id = tweet.in_reply_to_status_id_str
        in_reply_to_user_id = tweet.in_reply_to_user_id_str
        username = tweet.user.name
        user_verified_str = tweet.user.verified
        user_verified = 0
        if user_verified_str == True:
            user_verified = 1
        user_followers_count = tweet.user.followers_count
        user_created_at = tweet.user.created_at
        user_id = tweet.user.id

        if tweet.is_quote_status == True:
            quoted_status_id = tweet.quoted_status_id
        else:
            quoted_status_id = None
            retweeted_status = None
        try:
            reply_count = tweet.reply_count
        except:
            reply_count = 0
        retweet_count = tweet.retweet_count
        favorite_count = tweet.favorite_count
        retweeted_txt = tweet.retweeted
        if retweeted_txt == True:
            retweeeted = 1
        lang = tweet.lang
        tweet_tuple = (
            i,
            created_at,
            id,
            text,
            source,
            in_reply_to_user_id,
            username,
            user_verified,
            user_followers_count,
            user_created_at,
            user_id,
            quote_count,
            reply_count,
            retweet_count,
            retweeted
        )
        #print(f'{id}:{str(text)}' + "\n\n")
        #print(tweet_tuple)
        val.append(tweet_tuple)
        #print(val)
    
    sql = '''
        INSERT INTO tweet (search_val, created_at, tweet_id, text, source, in_reply_to_user_id,
        user_name, user_verified,
        user_followers_count, user_created_at, user_id,
        quote_count, reply_count, retweet_count, retweeted) 
        VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
        '%s','%s','%s','%s','%s'
        )''' % (val[0],
                val[1],
                val[2],
                val[3],
                val[4],
                val[5],
                val[6],
                val[7],
                val[8],
                val[9],
                val[10],
                val[11],
                val[12],
                val[13],
                val[14])

cur.execute(sql)
con.commit()
con.close()
#tweetCount += len(newTweets)
#maxId = newTweets[-1].id