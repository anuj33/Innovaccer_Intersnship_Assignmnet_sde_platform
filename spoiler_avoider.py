
from CommonUtils import CommonUtils
from ImdbScrapper import ImdbScrapper
import re
import config
from validate_email import validate_email


#This is the main script which takes tv series and mail address as input from user
#store the above info in mysql db
#call web scrapper function to fetch upcoming episode air date details for each tv series
#send one mail to the user with all thr above tv series upcoming episodes info

email_address = str(raw_input("enter email address :  "))
if(validate_email(email_address) == False):
    raise  ValueError('Please provide valid mail address :  ')
tv_series = [l.strip(" ").strip("\n") for l in raw_input("please provide comma separated values for the tv series :  ").split(",")]
CommonUtils.insert_data_in_mysql(email_address, tv_series)
imdb_scrapper = ImdbScrapper(config.IMDB_URL)
mail_body_arr = []
for tv_series in tv_series:
    mail_body_arr.append("<br />")
    tv_series_str = "Tv series name: {}".format(tv_series)
    mail_body_arr.append(tv_series_str)
    mail_body_arr.append("<br />")
    try:
        info = imdb_scrapper.fetch_upcoming_episode_details_using_imdb_scraping(tv_series)
        upcoming_episode_info = "Status: {}".format(info)
        print("tv_series - {} and output is - {}".format(tv_series, info))
    except:
        upcoming_episode_info = "Unable to fetch upcoming episode details due to unexpected exception. Please contact admin to debug"
    mail_body_arr.append(upcoming_episode_info)
    mail_body_arr.append("<br />")

mail_body_arr.append("<br />")
upcoming_episode_info_body = " ".join(mail_body_arr)
CommonUtils.send_email(email_address, "upcoming episodes air date", upcoming_episode_info_body)

