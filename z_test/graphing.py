import requests
from bs4 import BeautifulSoup
from twitch import TwitchClient
import pprint


client = TwitchClient('9nmje2zw0z52qn0g75wcrbsh1hxwny', 'yonru5pzy6xjbundnwz2cvjeyvxrn0')
streamers = client.users.translate_usernames_to_ids('Gaules')

# # scraping metrics
page = requests.get('https://www.twitchmetrics.net/channels/viewership').text
soup = BeautifulSoup(page, 'html.parser')

elem = soup_one.select('.col-md-10')
cards = soup_one.select('li.list-group-item')

for viewers_hours_column in elem:
    for card in cards:
        streamer = card.h5.text
        monthly_viewer_hours = card.samp.text
        last_seen = card.time.text

        print(streamer)
        print(f"{monthly_viewer_hours} - viewer hours this month")
        print(last_seen)
