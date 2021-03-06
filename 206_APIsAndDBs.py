## SI 206 2017
## Project 3
## Building on HW7, HW8 (and some previous material!)

##THIS STARTER CODE DOES NOT RUN!!


##OBJECTIVE:
## In this assignment you will be creating database and loading data 
## into database.  You will also be performing SQL queries on the data.
## You will be creating a database file: 206_APIsAndDBs.sqlite
##comment
import unittest
import itertools
import collections
import tweepy
import twitter_info # same deal as always...
import json
import sqlite3

## Your name: Katarina Mazanka mmm
## The names of anyone you worked with on this project:



##### TWEEPY SETUP CODE:
# Authentication information should be in a twitter_info file...
consumer_key = twitter_info.consumer_key
consumer_secret = twitter_info.consumer_secret
access_token = twitter_info.access_token
access_token_secret = twitter_info.access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# Set up library to grab stuff from twitter with your authentication, and 
# return it in a JSON format 
api = tweepy.API(auth, parser=tweepy.parsers.JSONParser())

##### END TWEEPY SETUP CODE

## Task 1 - Gathering data

## Define a function called get_user_tweets that gets at least 20 Tweets 
## from a specific Twitter user's timeline, and uses caching. The function 
## should return a Python object representing the data that was retrieved 
## from Twitter. (This may sound familiar...) We have provided a 
## CACHE_FNAME variable for you for the cache file name, but you must 
## write the rest of the code in this file.

CACHE_FNAME = "206_APIsAndDBs_cache.json"
# Put the rest of your caching setup here:

try:
    cache_file = open(CACHE_FNAME,'r')
    cache_contents = cache_file.read()
    cache_file.close()
    CACHE_DICTION = json.loads(cache_contents)
except:
    CACHE_DICTION = {}

## [PART 1]


##takes in a name and returns a list of the 20 tweets on timeline
def get_user_tweets(user_name):
    
     ##looks for key in dictionary
    if user_name in CACHE_DICTION:
        print("Data was in the cache")
        print(CACHE_DICTION[user_name])
        return CACHE_DICTION[user_name]
    else:
    	print("Making a request")
    	print("Retrieving" + "\n")
        ##searches for the term in all tweets
    	results = api.user_timeline(screen_name = user_name, count = 20)

    
    
    d_list = []
    for tweet in results:
        
        
        d_list.append(tweet)
        key =  tweet["id"]
        
        
        CACHE_DICTION[key] = tweet
    ##print(CACHE_DICTION[key])
    dumped_json_cache = json.dumps(CACHE_DICTION)
    fw = open(CACHE_FNAME,"w")
    fw.write(dumped_json_cache)
    fw.close() # Close the open file
    
    return d_list

get_user_tweets("@umsi")






# Write an invocation to the function for the "umich" user timeline and 
# save the result in a variable called umich_tweets:
umich_tweets = get_user_tweets("@umsi")



## Task 2 - Creating database and loading data into database
## You should load into the Users table:
# The umich user, and all of the data about users that are mentioned 
# in the umich timeline. 
# NOTE: For example, if the user with the "TedXUM" screen name is 
# mentioned in the umich timeline, that Twitter user's info should be 
# in the Users table, etc.
list_users = []

seen = set()
##finds users mentioned in the tweets and adds to a list
for item in umich_tweets:
	if item['entities']['user_mentions'] != []:
		for dic in item['entities']['user_mentions']:
			if dic['id'] not in seen:

				list_users.append(api.get_user(dic['id']))
				seen.add(dic['id'])
conn = sqlite3.connect('206_APIsAndDBs.sqlite')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Users')
cur.execute('CREATE TABLE Users (user_id TEXT,screen_name TEXT,num_favs INT,description TEXT)')
conn.commit()

for user in list_users:
	
		
	
	cur.execute('INSERT INTO Users (user_id, screen_name, num_favs, description) VALUES (?,?,?,?)',(user["id"], user["screen_name"], user["favourites_count"], user["description"]))
	conn.commit()

cur.execute('DROP TABLE IF EXISTS Tweets')
cur.execute('CREATE TABLE Tweets (tweet_id TEXT,author TEXT,time_posted TEXT,tweet_text TEXT,retweets  INT)')
conn.commit()
um_tweets = []
for item in umich_tweets:
	if item not in um_tweets:
		um_tweets.append(item)

for tweet in um_tweets:
	cur.execute('INSERT INTO Tweets (tweet_id, author, time_posted, tweet_text, retweets) VALUES (?, ?,?,?,?)',(tweet["id"], tweet["user"]["screen_name"], tweet["created_at"], tweet["text"], tweet["retweet_count"]))
	conn.commit()





# Make a query to select all of the records in the Users database. 
# Save the list of tuples in a variable called users_info.
users_info = []
sqlstr = 'SELECT user_id, screen_name, num_favs, description FROM Users'
temp_tup = ()
for row in cur.execute(sqlstr):
	temp_tup = (str(row[0]), str(row[1]), str(row[2]), str(row[3]))
	users_info.append(temp_tup)


# Make a query to select all of the user screen names from the database. 
# Save a resulting list of strings (NOT tuples, the strings inside them!) 
# in the variable screen_names. HINT: a list comprehension will make 
# this easier to complete! 
screen_names = []
sqlstr = 'SELECT screen_name FROM Users'
for row in cur.execute(sqlstr):
	screen_names.append(str(row[0]))






# Make a query to select all of the tweets (full rows of tweet information)
# that have been retweeted more than 10 times. Save the result 
# (a list of tuples, or an empty list) in a variable called retweets.
retweets = []
sqlstr = 'SELECT author FROM Tweets WHERE retweets > 10'
temp_tup = ()
for row in cur.execute(sqlstr):
	temp_tup = (str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]))


# Make a query to select all the descriptions (descriptions only) of 
# the users who have favorited more than 500 tweets. Access all those 
# strings, and save them in a variable called favorites, 
# which should ultimately be a list of strings.
favorites = []
sqlstr = 'SELECT description FROM Users WHERE num_favs > 500'
for row in cur.execute(sqlstr):
	favorites.append(str(row[0]))


# Make a query using an INNER JOIN to get a list of tuples with 2 
# elements in each tuple: the user screenname and the text of the 
# tweet. Save the resulting list of tuples in a variable called joined_data2.
joined_data = []
sqlstr = 'SELECT author, tweet_text FROM Tweets INNER JOIN Users ON Tweets.author = Users.screen_name'
for row in cur.execute(sqlstr):
	
	temp_tup = (str(row[0]), str(row[1]))
	joined_data.append(temp_tup)




# Make a query using an INNER JOIN to get a list of tuples with 2 
# elements in each tuple: the user screenname and the text of the 
# tweet in descending order based on retweets. Save the resulting 
# list of tuples in a variable called joined_data2.
##sorts the joined table by retweets
joined_data2 = []
sqlstr = 'SELECT author, tweet_text, retweets FROM Tweets INNER JOIN Users ON Tweets.author = Users.screen_name ORDER BY Tweets.retweets DESC'
for row in cur.execute(sqlstr):
	
	temp_tup = (str(row[0]), str(row[1]))
	joined_data2.append(temp_tup)


cur.close()
conn.close()
### IMPORTANT: MAKE SURE TO CLOSE YOUR DATABASE CONNECTION AT THE END 
### OF THE FILE HERE SO YOU DO NOT LOCK YOUR DATABASE (it's fixable, 
### but it's a pain). ###

###### TESTS APPEAR BELOW THIS LINE ######
###### Note that the tests are necessary to pass, but not sufficient -- 
###### must make sure you've followed the instructions accurately! 
######
print("\n\nBELOW THIS LINE IS OUTPUT FROM TESTS:\n")


class Task1(unittest.TestCase):
	def test_umich_caching(self):
		fstr = open("206_APIsAndDBs_cache.json","r")
		data = fstr.read()
		fstr.close()
		self.assertTrue("umich" in data)
	def test_get_user_tweets(self):
		res = get_user_tweets("umsi")
		self.assertEqual(type(res),type(["hi",3]))
	def test_umich_tweets(self):
		self.assertEqual(type(umich_tweets),type([]))
	def test_umich_tweets2(self):
		self.assertEqual(type(umich_tweets[18]),type({"hi":3}))
	def test_umich_tweets_function(self):
		self.assertTrue(len(umich_tweets)>=20)

class Task2(unittest.TestCase):
	def test_tweets_1(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result)>=20, "Testing there are at least 20 records in the Tweets database")
		conn.close()
	def test_tweets_2(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(len(result[1])==5,"Testing that there are 5 columns in the Tweets table")
		conn.close()
	def test_tweets_3(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT tweet_id FROM Tweets');
		result = cur.fetchall()
		self.assertTrue(result[0][0] != result[19][0], "Testing part of what's expected such that tweets are not being added over and over (tweet id is a primary key properly)...")
		if len(result) > 20:
			self.assertTrue(result[0][0] != result[20][0])
		conn.close()


	def test_users_1(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result)>=2,"Testing that there are at least 2 distinct users in the Users table")
		conn.close()
	def test_users_2(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result)<20,"Testing that there are fewer than 20 users in the users table -- effectively, that you haven't added duplicate users. If you got hundreds of tweets and are failing this, let's talk. Otherwise, careful that you are ensuring that your user id is a primary key!")
		conn.close()
	def test_users_3(self):
		conn = sqlite3.connect('206_APIsAndDBs.sqlite')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Users');
		result = cur.fetchall()
		self.assertTrue(len(result[0])==4,"Testing that there are 4 columns in the Users database")
		conn.close()

class Task3(unittest.TestCase):
	def test_users_info(self):
		self.assertEqual(type(users_info),type([]),"testing that users_info contains a list")
	def test_users_info2(self):
		self.assertEqual(type(users_info[0]),type(("hi","bye")),"Testing that an element in the users_info list is a tuple")

	def test_track_names(self):
		self.assertEqual(type(screen_names),type([]),"Testing that screen_names is a list")
	def test_track_names2(self):
		self.assertEqual(type(screen_names[0]),type(""),"Testing that an element in screen_names list is a string")

	def test_more_rts(self):
		if len(retweets) >= 1:
			self.assertTrue(len(retweets[0])==5,"Testing that a tuple in retweets has 5 fields of info (one for each of the columns in the Tweet table)")
	def test_more_rts2(self):
		self.assertEqual(type(retweets),type([]),"Testing that retweets is a list")
	def test_more_rts3(self):
		if len(retweets) >= 1:
			self.assertTrue(retweets[1][-1]>10, "Testing that one of the retweet # values in the tweets is greater than 10")

	def test_descriptions_fxn(self):
		self.assertEqual(type(favorites),type([]),"Testing that favorites is a list")
	def test_descriptions_fxn2(self):
		self.assertEqual(type(favorites[0]),type(""),"Testing that at least one of the elements in the favorites list is a string, not a tuple or anything else")
	def test_joined_result(self):
		self.assertEqual(type(joined_data[0]),type(("hi","bye")),"Testing that an element in joined_result is a tuple")



if __name__ == "__main__":
	unittest.main(verbosity=2)
