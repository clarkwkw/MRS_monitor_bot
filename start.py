import config, tgbot, crawler
from functools import partial
from telegram.ext import Updater, CommandHandler, ChosenInlineResultHandler, CallbackQueryHandler
from multiprocessing import Lock
import schedule

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

schedule.every(config.UPDATE_FREQ).minutes.do(partial(crawler.crawl, bot = updater.bot)).run()
updater.start_polling()
updater.idle()
config.log("Shutting down..")
config.EXIT_FLAG = True