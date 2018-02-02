import config, tgbot, crawler
from telegram.ext import Updater, CommandHandler, ChosenInlineResultHandler, CallbackQueryHandler
import threading

HANDLERS = {
	"start": tgbot.start,
	"list": tgbot.list,
	"subscribe": tgbot.subscribe,
	"unsubscribe": tgbot.unsubscribe
}

tgbot.setup()
config.log("Starting..")
updater = Updater(token = config.TG_TOKEN)
for command, handler in HANDLERS.items():
	updater.dispatcher.add_handler(CommandHandler(command, handler))

crawler_thread = threading.Thread(target = crawler.crawler_management, kwargs = {"bot": updater.bot}).start()
updater.start_polling()
updater.idle()
config.log("Shutting down..")
config.EXIT_FLAG = True