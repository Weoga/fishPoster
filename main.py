import telebot
import praw
from json import load
from telebot.util import extract_arguments
from prawcore.exceptions import Redirect
import re
import logging  # logger ¯\_(ツ)_/¯
from sys import stdout

logging.basicConfig(handlers=[logging.FileHandler("./reports.log"), logging.StreamHandler(stdout)], level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s: %(message)s')  # logger config
#

with open('login.json') as f:
	login = load(f)

reddit = praw.Reddit(
	client_id=login['client_id'],
	client_secret=login['client_secret'],
	redirect_uri=login['redirect_uri'],
	user_agent=login['user_agent'],
	username=login['username']
)
bot = telebot.TeleBot(login['tg_id'])
with open('subreddit.txt', 'r') as f:
	subreddit_name = f.read()
channel_id = "@hnshgd"


@bot.message_handler(commands=['imfish'])
def im_fish(message):
	if not message.chat.id == 1397541766:
		bot.send_message(message.chat.id, "Access denied")
		return
	bot.send_message(channel_id, "я рыбка")


@bot.message_handler(commands=['start'])
def start(message):
	if not message.chat.id == 1397541766:
		bot.send_message(message.chat.id, "Access denied")
		return
	bot.send_message(message.chat.id, 'hi mom')
	logging.info(f"{message.chat.username} sent a {message.text}")
	print(f"{message.date} {message.chat.username} sent a {message.text}")


FLAG_confirm_post = False
index = 0
post_img = None
post_title = None


@bot.message_handler(commands=['newpost', 'np', 'n'])
def newpost(message):
	if not message.chat.id == 1397541766:
		bot.send_message(message.chat.id, "Access denied")
		return
	global FLAG_confirm_post, post_img, post_title, index
	subreddit = reddit.subreddit(subreddit_name)
	hot = subreddit.new()
	i = 0
	for post in hot:
		i = i + 1
		print(f"i={i}, index={index}")
		if i < index + 1:
			continue
		image_link = post.url if ('.png' in post.url or '.jpg' in post.url or '.jpeg' in post.url) else None
		if image_link:
			title = post.title
			bot.send_photo(chat_id=message.chat.id, photo=image_link, caption=title)
			post_img = image_link
			post_title = title
			index = i
			break
	FLAG_confirm_post = True


def send_post(chat_id, image_link, title):
	if image_link and title:
		bot.send_photo(chat_id=chat_id, photo=image_link, caption=title)


@bot.message_handler(regexp='^y$')
def confirm_post(message):
	if not message.chat.id == 1397541766:
		bot.send_message(message.chat.id, "Access denied")
		return
	global FLAG_confirm_post, post_img, post_title, index
	if not FLAG_confirm_post: return
	FLAG_confirm_post = False
	image_link = post_img
	title = post_title
	send_post(channel_id, image_link, title)
	index = 0


@bot.message_handler(commands=['changesub'])
def changesub(message):
	if not message.chat.id == 1397541766:
		bot.send_message(message.chat.id, "Access denied")
		return
	global subreddit_name, index
	sub = extract_arguments(message.text)
	try:
		subreddit = reddit.subreddit(sub)
		hot = subreddit.new()
		for post in hot:
			break
	except Redirect:
		bot.send_message(message.chat.id, "Unable to find this sub")
		return
	subreddit_name = sub
	index = 0
	with open('subreddit.txt', 'w') as output_f:
		output_f.write(sub)
	logging.info(f'contents of subreddit.txt changed to {sub}')
	bot.send_message(message.chat.id, f"Changed to r/{sub}, boss")


@bot.message_handler(commands=['changetitle', 'ct'])
def changetitle(message):
	if not message.chat.id == 1397541766:
		bot.send_message(message.chat.id, "Access denied")
		return
	global FLAG_confirm_post, post_title
	if not FLAG_confirm_post: return
	new_title = re.search('(/\\w*)\\s(.*)', message.text).group(2)
	post_title = new_title
	send_post(message.chat.id, post_img, post_title)


if __name__ == '__main__':
	logging.info('STARTING')
	try:
		bot.polling()
	except Exception as _e:
		logging.error(_e)
		print(_e.__str__())
