import tweepy
import os
import json
import sys
import json
import time
import logging
import twitter
import urllib.parse
import urllib.request as req
from glob import glob
import flask
from flask import request,make_response
from flask_cors import CORS, cross_origin
from flask import jsonify
import re
import threading
app = flask.Flask(__name__)
CORS(app)

def tweet_url(t):
		return "https://twitter.com/%s/status/%s" % (t.user.screen_name, t.id)

def get_tweets(filename):
		for line in open(filename):
				yield twitter.Status.NewFromJsonDict(json.loads(line))

def get_replies(tweet, t):
		user = tweet.user.screen_name
		tweet_id = tweet.id
		max_id = None
		while True:
				q = urllib.parse.urlencode({"q": "to:%s" % user,"count":"10000"})
				try:
						replies = t.GetSearch(raw_query=q, since_id=tweet_id,include_entities=True)
				except twitter.error.TwitterError as e:
						logging.error("caught twitter api error: %s", e)
						time.sleep(60)
						continue
				for reply in replies:
						if reply.in_reply_to_status_id == tweet_id:
								yield reply
								# recursive magic to also get the replies to this reply
								for reply_to_reply in get_replies(reply, t):
										yield reply_to_reply
						max_id = reply.id
				if len(replies) != 100:
						break



def initialize_api():
	consumer_key = 'abcd'
	consumer_secret = 'abcd'
	access_token = 'abcd'
	access_token_secret = 'abcd'
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth)
	
	e = {}
	e['CONSUMER_KEY'] = 'abcd'
	e['CONSUMER_SECRET'] = 'abcd'

	e['ACCESS_TOKEN'] = 'abcd'
	e['ACCESS_TOKEN_SECRET'] = 'abcd'

	t = twitter.Api(
			consumer_key=e["CONSUMER_KEY"],
			consumer_secret=e["CONSUMER_SECRET"],
			access_token_key=e["ACCESS_TOKEN"],
			access_token_secret=e["ACCESS_TOKEN_SECRET"],
			sleep_on_rate_limit=True,
			tweet_mode='extended'
	)
	return api, t

def save_tweetids(screen_name, api):
#	crawl all the tweets from user's timeline and then save them into tweets.json
	out_file = open("./tweetids.json", "w")
	tweet = {}
	tweet["user"] = {"screen_name": screen_name}
	for twt in api.user_timeline(screen_name = screen_name, include_rts = False):
		tweet["id"] = twt.id
		try:
			id_str = twt.text.split("This is a story from ")[1].split(".")[0]
#			print(id_str)
		except:
			continue
		tweet["id_str"] = id_str
		out_file.write(json.dumps(tweet)+"\n")


def crawl_replies(t):
	tweets_file = './tweetids.json'
	crawled = False
	for tweet in get_tweets(tweets_file):
		print(tweet.id_str)
#		create a folder for each tweet
		file_path = "./replies/" + str(tweet.id_str) + "/tweet" + str(tweet.id) + "/"
#		save tweet
		ori_tweet = t.GetStatus(tweet.id)
		if ori_tweet.full_text[:5] == 'reply':
			continue
		directory = os.path.dirname(file_path)
		if not os.path.exists(directory):
			os.makedirs(directory)
		tweet_file = open(file_path + "tweet.txt", "w")
#		save content
		try:
			tweet_file.write(ori_tweet.full_text[:-24])
		except:
			pass
		tweet_file.close()
#		download images
		try:
			i = 0
			for media in ori_tweet.media:
				req.urlretrieve(media.media_url, file_path + str(i) + ".jpg")
				i += 1
		except:
#			no images
			import shutil

			shutil.rmtree(file_path)
			continue
			
		for reply in get_replies(tweet,t):
#			create a folder for each reply
			reply_path = file_path + "reply" +reply.id_str + "/"
			directory = os.path.dirname(reply_path)
			if not os.path.exists(directory):
				os.makedirs(directory)
			else:
				continue
#			save user profile photo
			req.urlretrieve(reply.user.profile_image_url.replace("_normal",""), reply_path + "profile.jpg")
			reply_file = open(reply_path + "reply.txt", "w")
#			save user name
			reply_file.write(reply.user.screen_name + '\n')
#			save created time
			reply_file.write(reply.created_at + '\n')
#			save reply content
			reply_file.write(reply.full_text[:-24])
#			download images
			try:
				i = 0
				for media in reply.media:
					req.urlretrieve(media.media_url, reply_path + str(i) + ".jpg")
					i += 1
					crawled = True
			except:
#				no images
				import shutil

				shutil.rmtree(reply_path)
				continue
	return crawled
def start_crawler():
	crawler_thread = threading.Thread(target=main)
	crawler_thread.start()
	print("crawler started")
	
def main():
	api, t = initialize_api()
	screen_name = 'collectfeedback'
#	screen_name = 'zmpy_2016'
	br = start_browser()
#	time.sleep(5)
	br.get("file:///Users/zl/Desktop/memory2slideshow/web/index.html")
	while True:
		save_tweetids(screen_name, api)
		logging.basicConfig(level=logging.INFO)
		crawled = crawl_replies(t)
		print(crawled)
		if crawled:
			br.refresh()
		time.sleep(1000)

def start_browser():
	from selenium import webdriver
	profile = webdriver.FirefoxProfile()
	br = webdriver.Firefox(firefox_profile = profile)
#    br.implicitly_wait(10)
	return br
	
@app.route("/slideshow")
def slideshow():
	if request.method == 'GET':
		u_id = request.args.get('u_id')
		
	path = "./replies/" + u_id + '/'
	tweets = []
	for tweet_folder in glob(path+"*"):
		with open(tweet_folder + '/tweet.txt','r') as tweet_file:
			try:
				tweets.append({})
				tweets[-1]["tweet"] = re.sub(r"http\S+", "", next(tweet_file)[:-1])
				
				tweets[-1]["img"] = []
				
				for img_idx in range(len(glob(tweet_folder+"/*.jpg"))):
					tweets[-1]["img"].append(tweet_folder[1:] + "/" + str(img_idx) + ".jpg")
				
				tweets[-1]["replies"] = []
				for reply_folder in glob(tweet_folder+"/reply*"):
					reply_file = open(reply_folder + "/reply.txt",'r')
					tweets[-1]["replies"].append({})
					tweets[-1]["replies"][-1]["profile"] = reply_folder[1:] + "/profile.jpg"
					tweets[-1]["replies"][-1]["user_name"] = next(reply_file)[:-1]
					tweets[-1]["replies"][-1]["time"] = next(reply_file)[:-1]
					tweets[-1]["replies"][-1]["text"] = re.sub(r"http\S+", "", next(reply_file))
					tweets[-1]["replies"][-1]["img"] = reply_folder[1:] + "/0.jpg"	
			except:
				tweets.pop(-1)
	return jsonify(tweets)
	

@app.route("/index_slideshow")
def index_slideshow():
	
	uids = []
	for root,dirs,_ in os.walk('./replies'):
		for d in dirs:
			uids.append(d)
		break
		
	tweets = []
	r = 0
	for u_id in uids:
		
		path = "./replies/" + u_id + '/'
		
		for tweet_folder in glob(path+"*"):
			with open(tweet_folder + '/tweet.txt','r') as tweet_file:
				try:
					tweets.append({})
					tweets[-1]["tweet"] = re.sub(r"http\S+", "", next(tweet_file)[:-1])
					tweets[-1]["img"] = []
					for img_idx in range(len(glob(tweet_folder+"/*.jpg"))):
						tweets[-1]["img"].append(tweet_folder[1:] + "/" + str(img_idx) + ".jpg")
					tweets[-1]["replies"] = []
					for reply_folder in glob(tweet_folder+"/reply*"):
						reply_file = open(reply_folder + "/reply.txt",'r')
						tweets[-1]["replies"].append({})
						tweets[-1]["replies"][-1]["profile"] = reply_folder[1:] + "/profile.jpg"
						tweets[-1]["replies"][-1]["user_name"] = next(reply_file)[:-1]
						tweets[-1]["replies"][-1]["time"] = next(reply_file)[:-1]
						tweets[-1]["replies"][-1]["text"] = re.sub(r"http\S+", "", next(reply_file))
						tweets[-1]["replies"][-1]["img"] = reply_folder[1:] + "/0.jpg"	
						r += 1
				except:
					tweets.pop(-1)
	return jsonify(tweets)
	

@app.route("/all_pics")
def all_pics():
	if request.method == 'GET':
		u_id = request.args.get('u_id')
		
	path = "./replies/" + u_id + '/'
	pics = []
	for tweet_folder in glob(path+"*"):
		with open(tweet_folder + '/tweet.txt','r') as tweet_file:
			if len(glob(tweet_folder+"/reply*")) != 0:
				pics.append(tweet_folder[1:] + "/0.jpg")
			for reply_folder in glob(tweet_folder+"/reply*"):
				pics.append(reply_folder[1:] + "/0.jpg")
	return jsonify(pics)


if __name__ == "__main__":	
	start_crawler()
	port = 8000

	app.debug = True
	app.run(port=port,host='0.0.0.0',threaded = True,debug=False)