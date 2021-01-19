
import cfg
import argparse
import tweepy
import sqlite3
import datetime

class StdOutListener(tweepy.StreamListener):
	def __init__(self):
		self.connection = sqlite3.connect("twitter.db")
		self.cursor = self.connection.cursor()
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS tweets (
									created_at VARCHAR(255),
									text VARCHAR(1000),
									user_id VARCHAR(255),
									user_screen_name VARCHAR(255),
									user_location VARCHAR(255),
									user_description VARCHAR(255),
									user_follower_counts VARCHAR(255),
									user_friends_count VARCHAR(255),
									user_favourites_count VARCHAR(255),
									user_statuses_count VARCHAR(255),
									user_retweeted VARCHAR(255)
									);
							""")
		self.connection.commit()
		self.trigger = True
		_, self.switching_off_time = self.add_seconds(datetime.datetime.now().time(), seconds_to_complete)
		super(StdOutListener, self).__init__()

	def standardise(input_):
		return str(input_).replace('\n', '').replace(',', '').strip()

	def add_seconds(self, current_time, seconds):
		current_time = datetime.datetime(100, 1, 1, current_time.hour, current_time.minute, current_time.second)
		return  current_time, current_time + datetime.timedelta(seconds = seconds)

	def on_error(self, status_code):
		if status_code == 420:
			return False

	def on_status(self, tweet):
		self.computer_time, _ = self.add_seconds(datetime.datetime.now().time(), 0)

		if self.computer_time <= self.switching_off_time:
			if 'RT @' in str(tweet.text):
				self.user_retweeted = 'True'
			self.user_retweeted = 'False'
			try:
				self.SQL_command = 		""" INSERT INTO tweets VALUES("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}");
										""".format(	str(tweet.created_at), str(tweet.text),
												str(tweet.user.id),
												str(tweet.user.screen_name),
												str(tweet.user.location), str(tweet.user.description),
												str(tweet.user.followers_count), str(tweet.user.friends_count),
												str(tweet.user.favourites_count), str(tweet.user.statuses_count), str(self.user_retweeted))

				self.cursor.execute(self.SQL_command)
				self.connection.commit()
				print (tweet.text)
				print ('-' * 10)
				return True
			except: pass
		else: return False


class LiveTwitterStream:
	def __init__(self, keywords):
		self.keywords = keywords
		self.listener = StdOutListener()
		self.authorize = tweepy.OAuthHandler(cfg.consumer_key, cfg.consumer_secret)
		self.authorize.set_access_token(cfg.access_token, cfg.access_token_secret)

	def activate(self):
		self.stream = tweepy.Stream(self.authorize, self.listener)
		self.stream.filter(track = self.keywords)

argument = argparse.ArgumentParser()
argument.add_argument('-k', action = 'store', dest = 'keyword', help = 'Words that you want to scrape as a whole string with pipe delimiter between them', default = False)
argument.add_argument('-s', action = 'store', dest = 'seconds', help = 'Integer as a number of seconds you want code to run', default = False)
argumentation = argument.parse_args()

if argumentation.keyword and argumentation.seconds:
	seconds_to_complete = int(argumentation.seconds)
	LiveTwitterStream(keywords = str(argumentation.keyword).split('|')).activate()
else: print ('Please provide keyword and seconds to scrape data')
