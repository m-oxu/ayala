from scraper_tweets_tool import TwitterSearch
from datapane_report import execution_function_dapane
twitter_class = TwitterSearch()
twitter_class.get_query_list()
twitter_class.search_on_twitter()
twitter_class.turn_list_in_dataframe()
twitter_class.insert_data_in_postgresql()
twitter_class.followers_count()

execution_function_dapane()