import http.cookiejar as cookielib
from urllib import request, parse
import re
import config, tgbot
import traceback

def crawl(bot):
	try:
		config.log("Crawling..")
		cookie_jar = cookielib.CookieJar()
		opener = build_opener(cookie_jar)
		login(opener)
		studies = list_studies(opener)

		collection_studies = tgbot.mongo_client["MKTG-studies"]["Studies"]
		old_studies_docs = collection_studies.find({})
		old_studies = {}
		for old_study in old_studies_docs:
			old_studies[old_study["study_id"]] = old_study

		noti_content = "The following studies now become available:\n"
		noti_flag = False
		for study in studies:
			status = check_availability(opener, study["study_id"])
			study["available"] = status
			if "credit" in study["credit"] and status:
				noti_criteria = study["study_id"] in old_studies and not old_studies[study["study_id"]]["available"]
				noti_criteria = noti_criteria or study["study_id"] not in old_studies
				if noti_criteria:
					noti_content += "  - %s (%s)\n"%(study["study_name"], study["credit"])
					noti_flag = True
		
		config.log("New data ready")
		collection_studies.delete_many({})
		collection_studies.insert_many(studies)
		
		noti_content += "\nClick <a href = \"%s\">here</a> to register\n"%config.URLS["HOME"]
		
		if noti_flag:
			config.log("Pushing notification")
			tgbot.push_notification(bot, noti_content)
	except SystemExit:
		exit(-1)
	except:
		print(traceback.format_exc())

def build_opener(cookie_jar, header = config.GENERAL_HEADER):
	handler = request.HTTPCookieProcessor(cookie_jar)
	opener = request.build_opener(handler)
	opener.addheaders = list(header.items())
	return opener

def login(opener):
	fields_to_copy = ["__LASTFOCUS", "__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTTARGET", "__EVENTARGUMENT", "__EVENTVALIDATION"]
	fields = {}

	regex = r'<input type="hidden" name="([^"]*)" id="([^"]*)" value="([^"]*)" \/>'
	with opener.open(config.URLS["HOME"]) as page:
		page_content = page.read().decode("utf-8")
		for match in re.finditer(regex, page_content):
			if match.group(1) in fields_to_copy:
				fields[match.group(1)] = match.group(3)

	header = dict(config.GENERAL_HEADER)
	header["referer"] = config.REFERER["LOGIN"]
	opener.addheaders = list(header.items())

	fields["ctl00$ContentPlaceHolder1$return_experiment_id"] = ""
	fields["ctl00$ContentPlaceHolder1$userid"] = config.USERNAME
	fields["ctl00$ContentPlaceHolder1$pw"] = config.PASSWORD
	fields["ctl00$ContentPlaceHolder1$default_auth_button"] = "Log In"
	
	with opener.open(config.URLS["LOGIN"], data = parse.urlencode(fields).encode()) as page:
		page_content = page.read().decode("utf-8")
		if "Login failed." in page_content:
			config.log("Cannot login to the system")
			config.EXIT_FLAG = True
			exit(-1)

def list_studies(opener):
	header = dict(config.GENERAL_HEADER)
	header["referer"] = config.REFERER["LIST"]
	opener.addheaders = list(header.items())

	study_regex = r'<tr id="ctl00_ContentPlaceHolder1_repStudentStudies_ctl\d+_RepeaterRow">((.|\n)*?)</tr>'
	study_id_name_regex = r'<a id="ctl00_ContentPlaceHolder1_repStudentStudies_ctl\d+_HyperlinkStudentStudyInfo" href="exp_info_participant\.aspx\?experiment_id=(\d+)">([^<]*)</a>'
	study_credit_regex = r'<span id="ctl00_ContentPlaceHolder1_repStudentStudies_ctl\d+_LabelCredits">\s*\((.*)\)</span>'
	studies = []
	with opener.open(config.URLS["LIST"]) as page:
		page_content = page.read().decode("utf-8")
		for match in re.finditer(study_regex, page_content):
			submatch = re.search(study_id_name_regex, match.group(1))
			study_id = submatch.group(1)
			study_name = submatch.group(2)
			submatch = re.search(study_credit_regex, match.group(1))
			credit = submatch.group(1)
			studies.append({
				"study_id": study_id,
				"study_name": study_name,
				"credit": credit
			})
	return studies

def check_availability(opener, study_id):
	header = dict(config.GENERAL_HEADER)
	header["referer"] = config.REFERER["AVAILABILITY"] + study_id
	opener.addheaders = list(header.items())

	reject_str = "There are no timeslots currently available for this study."
	with opener.open(config.URLS["AVAILABILITY"] + study_id) as page:
		page_content = page.read().decode("utf-8")
		if reject_str in page_content:
			return False

		return True

if __name__ == "__main__":
	cookie_jar = cookielib.CookieJar()
	opener = build_opener(cookie_jar)
	login(opener)
	studies = list_studies(opener)
	for study in studies:
		if "credit" in study["credit"]:
			status = check_availability(opener, study["study_id"])
			print("%s (%s): %s"%(study["study_id"], study["credit"], status))
