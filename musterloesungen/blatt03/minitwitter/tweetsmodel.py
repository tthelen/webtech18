from server.log import log
import sqlite3 as sqlite
import re
from datetime import datetime


class TweetError(Exception):
    """Error handling user data."""

    def __init__(self, msg=''):
        self.msg = msg


class Tweets:
    """The User collection."""

    def __init__(self, db_connection=None):

        if not db_connection:
            self.con = sqlite.connect('user.db')
        else:
            self.con = db_connection  # assign an open db connection

        with self.con:  # CREATE TABLE is necessary and make sure default data is present
            cur = self.con.cursor()
            cur.executescript("""
              CREATE TABLE IF NOT EXISTS tweets(tweet TEXT, date TEXT, username TEXT REFERENCES user(username));
              INSERT OR IGNORE INTO tweets (rowid, tweet, date, username) VALUES (1, 'Ein Tweet. Ist er nicht schön?','29.01.2019, 15:35','admin');
              """)

    def createTweet(self, tweet, user):
        """Create a new user in db. Returns 1 if inserted, 0 if not."""

        if not user:
            raise TweetError("Invalid empty username.")

        if not tweet:
            raise TweetError("Invalid empty username.")

        with self.con:
            cur = self.con.cursor()
            now = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            print(tweet,now,user.username)
            cur.execute("INSERT INTO tweets (tweet, date, username) VALUES(?,?,?)", (tweet, now, user.username))
            return cur.rowcount

    def findTweets(self):
        """Fetches list of all tweets ordered by creation date (ascending).

        Return: Iterable with dictionaries {"tweet": "Tweet content", "date": "printable date string", "author": "Author's fullname"}
        """

        with self.con:
            cur = self.con.cursor()
            query = "SELECT tweet, date, users.fullname as author FROM tweets LEFT JOIN users ON (tweets.username = users.username) ORDER BY tweets.rowid"
            cur.execute(query)
            return cur.fetchall()

