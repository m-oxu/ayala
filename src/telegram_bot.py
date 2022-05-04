from http.client import BAD_REQUEST
import logging
import os
import psycopg2
from dotenv import load_dotenv
from telegram.ext import CommandHandler, Updater
import pandas as pd

load_dotenv('.env')
PORT = int(os.environ.get('PORT', 5000))
# Enable logging
logging.basicConfig(
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

heroku_uri = os.getenv("HEROKU_URI")
BOT_API_TOKEN = os.environ.get("BOT_API_TOKEN")
heroku_con = psycopg2.connect(heroku_uri, sslmode='require')
heroku_cur = heroku_con.cursor()

supabase_uri = os.environ.get("SUPABASE_URI")
supabase_con = psycopg2.connect(supabase_uri, sslmode='require')
supabase_cur = supabase_con.cursor()


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text("""Bem vinde! Sou a AyalaBot! \n\nComigo você pode adicionar \
queries ao seu projeto ou checar quantos tweets já foram coletados.

Comandos disponíveis :
        /query - Digite /query <sua query> para armazenar uma query na sua base de dados.
        /check - Para saber quantos tweets já existem na sua base de dados.
        /myqueries - Para saber quais queries estão armazenados na sua base de dados.
        /deletequery - Para deletar uma query do seu banco de dados.""")


def query(update, context):
    try:
        sql_query = """
                    INSERT INTO queries (query) VALUES ('%s')
                    """ % (str(context.args).replace("[", "").replace("]", "").replace("'", "").replace(",", "") + ' -is:retweet')


        heroku_cur.execute(sql_query)
        heroku_con.commit()
        update.message.reply_text("Sua query foi armazenada com sucesso! :)")
    except Exception:
        update.message.reply_text("Não conseguimos armazenar sua query :(")

def check(update, context):
    try:
        sql_query = "select count(text) from historical_tweets"
        supabase_cur.execute(sql_query)
        tupples = supabase_cur.fetchall()
        df = pd.DataFrame(tupples, columns=['queries_number'])
        update.message.reply_text(f"Até o momento você tem {df.queries_number.values[0]:,} tweets na sua base de dados.")
    except Exception:
        update.message.reply_text("Não conseguimos conectar com sua base de dados.")

def myqueries(update, context):
    sql = "select query from queries"

    heroku_cur.execute(sql)
    tupples = heroku_cur.fetchall()
    df = pd.DataFrame(tupples, columns=['query'])
    update.message.reply_text(f"As queries disponíveis na sua base de dados são: \n\n {list(df['query'])}")


def deletequery(update, context):
    try:
        input_message = context.args[0]
        sql_query = f"DELETE FROM queries WHERE query LIKE '%{input_message}%'"
        heroku_cur.execute(sql_query)
        heroku_con.commit()
        update.message.reply_text("Sua query foi deletada!")
    except Exception:
        update.message.reply_text("Não entendi seu comando. Quer tentar de novo?")



def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(BOT_API_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("query", query, pass_args=True))
    dp.add_handler(CommandHandler("check", check))
    dp.add_handler(CommandHandler("myqueries", myqueries))
    dp.add_handler(CommandHandler("deletequery", deletequery, pass_args=True))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    heroku_con.close()
    supabase_con.close()


if __name__ == '__main__':
    main()
    