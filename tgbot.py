import config
from pymongo.errors import ConnectionFailure
from pymongo import MongoClient
import traceback

mongo_client = None

def setup():
	global mongo_client
	try:
		mongo_client = MongoClient("mongodb://%s/MKTG-studies"%config.DB_HOST, 
			username = config.DB_USERNAME if len(config.DB_USERNAME) > 0 else None, 
			password = config.DB_PASSWORD if len(config.DB_PASSWORD) > 0 else None)
		mongo_client["MKTG-studies"]["Studies"].find_one()
		mongo_client["MKTG-studies"]["Subscribed"].find_one()
	except Exception as e:
		print(e)
		print("Failed to connect to MongoDB")
		exit(-1)

def start(bot, update):
	content = "Hi, I can help keep track of the availability of MRS!\n"
	content += "Try out the following commands:\n"
	content += "  - /list\n"
	content += "  - /subscribe\n"
	update.message.reply_text(content, timeout = 10, parse_mode = "HTML")

def list(bot, update):
	try:
		collection = mongo_client["MKTG-studies"]["Studies"]
		studies = collection.find()
		content = ""
		if studies.count() == 0:
			content = "There is no study on the page, please try again later"
		else:
			i = 1
			for study in studies:
				status = "<b>OPEN</b>" if study["available"] else "<i>closed</i>"
				content += "%d. %s\n    (%s)   %s\n"%(i, study["study_name"], study["credit"], status)
				i += 1
		content += "\nClick <a href = \"%s\">here</a> to register\n"%config.URLS["HOME"]
		update.message.reply_text(content.rstrip("\n"), timeout = 10, parse_mode = "HTML")
	except:
		print(traceback.format_exc())

def subscribe(bot, update):
	try:
		collection = mongo_client["MKTG-studies"]["Subscribed"]
		tg_user_id = update.effective_user.id
		user_obj = collection.find_one({"tgid": tg_user_id})
		if user_obj is not None:
			update.message.reply_text("But you have already subscribed\nTo unsubscribe, click /unsubscribe", timeout = 10, parse_mode = "HTML")
		else:
			collection.insert_one({"tgid": tg_user_id})
			update.message.reply_text("Subscribed, you will be notified whenever a <b>credit bearing</b> study becomes available", timeout = 10, parse_mode = "HTML")
	except:
		print(traceback.format_exc())

def unsubscribe(bot, update):
	try:
		collection = mongo_client["MKTG-studies"]["Subscribed"]
		tg_user_id = update.effective_user.id
		user_obj = collection.find_one({"tgid": tg_user_id})
		if user_obj is None:
			update.message.reply_text("But you have not subscribed before", timeout = 10, parse_mode = "HTML")
		else:
			collection.delete_one({"tgid": tg_user_id})
			update.message.reply_text("Unsubscribed, thanks for using", timeout = 10, parse_mode = "HTML")
	except:
		print(traceback.format_exc())

def push_notification(bot, content):
	try:
		collection = mongo_client["MKTG-studies"]["Subscribed"]
		users = collection.find({})
		content = content.strip("\n")
		for user in users:
			bot.send_message(user["tgid"], content, timeout = 10, parse_mode = "HTML")
	except:
		print(traceback.format_exc())