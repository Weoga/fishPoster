import telebot
import praw
import json

with open('login.json') as f:
    login = json.load(f)

reddit = praw.Reddit(
    client_id=login['client_id'],
    client_secret=login['client_secret'],
    redirect_uri=login['redirect_uri'],
    user_agent=login['user_agent'],
    username=login['username'],
    password=login['password'],
)
bot = telebot.TeleBot("6744314989:AAENrlOqZOi-7lojTqaD5VuTnmNGQKbbb90")

channel_id = "@marcestest"
def imFish():
	bot.send_message("@hnshgd", "я рыбка")


def catpost():
	subreddit = reddit.subreddit('cats')
	hot = subreddit.new()
	for post in hot:
		image_link = post.url if ('.png' in post.url or '.jpg' in post.url or '.jpeg' in post.url) else None
		if image_link:
			title = post.title
			print(post.title)
			# print(post.caption)
			bot.send_photo(chat_id=channel_id, photo=image_link, caption=title)

if __name__ == "__main__":
	catpost()