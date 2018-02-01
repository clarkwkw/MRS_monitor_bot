import getpass, time, datetime, pytz

try:
	USERNAME = input("Username: ")
	PASSWORD = getpass.getpass("Password: ")
	TG_TOKEN = input("Telegram bot token: ")
	DB_HOST = "localhost:27017"
	DB_USERNAME = input("MongoDB username:")
	DB_PASSWORD = getpass.getpass("MongoDB password:")
except:
	print("\nPlease complete the configuration")
	exit(-1)

EXIT_FLAG = False
UPDATE_FREQ = 20

URLS = {
	"HOME": "https://cuhk.sona-systems.com",
	"LOGIN": "https://cuhk.sona-systems.com/Default.aspx?ReturnUrl=%2f",
	"LIST": "https://cuhk.sona-systems.com/all_exp_participant.aspx",
	"AVAILABILITY": "https://cuhk.sona-systems.com/exp_view_slots.aspx?experiment_id="
}

GENERAL_HEADER = {
	"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
	"Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja;q=0.6"

}

REFERER = {
	"LOGIN": "https://cuhk.sona-systems.com/Default.aspx",
	"LIST": "https://cuhk.sona-systems.com/Main.aspx?p_log=%s"%USERNAME,
	"AVAILABILITY": "https://cuhk.sona-systems.com/exp_info_participant.aspx?experiment_id="
}

def log(msg):
	timeUTC = datetime.datetime.now()
	timezone = pytz.timezone("Asia/Hong_Kong")
	corrected = pytz.utc.localize(timeUTC).astimezone(timezone)
	print("%s: %s"%(corrected.strftime("%m-%d %H:%M"), msg))