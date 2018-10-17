
import urllib2
from bs4 import BeautifulSoup
from datetime import datetime
import re
from dateutil.parser import parse


''' algorithm is as follows :-
    if plot is mentioned for last season and last epiosde - then series has ended.
    if plot is not mentioned for last season first episode - then this is first episode of next season. Fetch the year info.
    else Iterate through all the episodes of last season and whichever episode doesn't have plot info, fetch the date and publich the result.
    if date is not provided in any of the above cases, then return - "date is not available for next episode on imdb"

  '''

class ImdbScrapper:


    def __init__(self, imdb_url):
        self.imdb_url = imdb_url


    # return upcoming episode information for given tv series
    def fetch_upcoming_episode_details_using_imdb_scraping(self, tv_series_title):

        #search for tv series in imdb and fetch the content url
        tv_series_title_imb_url = "{}/search/title?title={}".format(self.imdb_url, tv_series_title)
        resp = urllib2.urlopen(tv_series_title_imb_url)
        soup = BeautifulSoup(resp, 'html.parser')
        tv_series_containers = soup.find_all('div', class_ = 'lister-item mode-advanced')

        #the top most container might not be the one which we wanted
        required_tv_series_container = tv_series_containers[0]
        for container in tv_series_containers:
            #if title matches then this the correct container
            if (tv_series_title.lower() in container.find_all('div', class_ = 'lister-item-content')[0].getText().lower()):
                required_tv_series_container = container
                break


        tv_series_item_content = required_tv_series_container.find_all('div', class_ = 'lister-item-content')
        tv_series_info_url = str(tv_series_item_content[0].find('a')['href'])

        #fetch the season info from imdb page of given tv series
        actual_tv_series_url = "{}{}".format(self.imdb_url, tv_series_info_url)
        tv_series_page = urllib2.urlopen(actual_tv_series_url)
        tv_series_page_soup = BeautifulSoup(tv_series_page, 'html.parser')
        seasons_soup = tv_series_page_soup.find_all('div', class_ = 'seasons-and-year-nav')
        latest_season_link = seasons_soup[0].find_all('a')[0]['href']

        #scrape episode info from latest/upcoming season of given tv series
        latest_season_url = "{}{}".format(self.imdb_url, latest_season_link)
        latest_season_web_page = urllib2.urlopen(latest_season_url)
        latest_season_soup = BeautifulSoup(latest_season_web_page, 'html.parser')

        #scrape title and air date info for latest/upcoming episodes of given tv series
        tv_series_current_season_episode_titles_sorted = [l for l in latest_season_soup.find_all('div',class_ = "list detail eplist")[0].find_all('div', class_ = "item_description")]
        tv_series_current_season_episode_airdate_sorted =  [str(l.getText().replace(".", " ").replace("\n", " ").strip(" ")) for l in latest_season_soup.find_all('div',class_ = "airdate")]
        upcoming_episode_air_details = get_upcoming_episode_airdate_details(tv_series_current_season_episode_titles_sorted, tv_series_current_season_episode_airdate_sorted)
        return upcoming_episode_air_details



def get_upcoming_episode_airdate_details( tv_series_current_season_episode_titles_sorted, tv_series_current_season_episode_airdate_sorted):
    date_pattern = re.compile("\d{2}\s\w+\s+\d{4}") #pattern for date of next episode
    year_pattern = re.compile("\d{4}")
    result = None
    latest_season_info = dict(zip(tv_series_current_season_episode_titles_sorted, tv_series_current_season_episode_airdate_sorted))

    #if no episodes are given then information is not sufficent on imdb
    if len(tv_series_current_season_episode_titles_sorted) == 0:
        result = "air date of next episode id not given on imdb"
        return result

    #if no details about first episode then this is next season
    # if air date is none or empty then date info is missing on imdb
    if("Know what this is about" in  tv_series_current_season_episode_titles_sorted[0].getText()):
        next_season_first_episode_air_year = tv_series_current_season_episode_airdate_sorted[0]
        if (year_pattern.findall(next_season_first_episode_air_year)):
            result = "The next season begins in {}".format(next_season_first_episode_air_year)
        else:
            result = "Air date details of next season is not there on imdb"
        return result

    #check for an episode whose plot details are not known but plot details of previous episode is known.
    #return the air date of that episode
    for key, value in latest_season_info.iteritems():
        # coming episode
        if "Know what this is about" in key.getText():
            episode_air_date = value
            if episode_air_date == "":
                result = "Air date details of next episode is not there on imdb"
            elif(date_pattern.match(episode_air_date)is not None):
                dt= parse(episode_air_date)
                result = "The next episode airs on {}".format(dt.strftime('%Y-%m-%d'))
            elif(year_pattern.match(episode_air_date) == True):
                result = "The next episode airs in year - {}".format(episode_air_date)

    #if we have reached till here which means plot details of all episodes of last season is available, which means this series has ended
    if result is None:
        result = "The show has finished streaming all its episodes."
    return result




