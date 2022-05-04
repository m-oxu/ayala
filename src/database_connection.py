import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('.env')
database_uri = os.getenv("HEROKU_URI")

con = psycopg2.connect(database_uri, sslmode='require')
cur = con.cursor()

sql = """DROP TABLE historical_tweets
    """

cur.execute(sql)
con.commit()
con.close()