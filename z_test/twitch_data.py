from twitch import TwitchClient
import pprint
import requests
import json
import os
import pandas as pd

# STREAMER VODS
# client = TwitchClient(app.config['TWITCH_CLIENT_ID'])
# streamers = client.streams.get_live_streams(limit=15)

# for stream in streamers:
#     streams_info = {
#         'channel_id': stream['channel']['id'],
#         'streamer_name': stream['channel']['display_name']
#     }

#     vods_info = []
#     streamer_vods = client.channels.get_videos(streams_info['channel_id'], limit=15)
#     for vods in streamer_vods:
#         vod_info = {
#             'vod_streamer_name': vods['channel']['name'],
#             'preview': vods['preview']['medium'],
#             'url': vods['url'],
#             'title': vods['title']
#         }
#         if streams_info['streamer_name'] == vod_info['vod_streamer_name']:
#             vods_info.append(vod_info)


# client = TwitchClient('9nmje2zw0z52qn0g75wcrbsh1hxwny', 'yonru5pzy6xjbundnwz2cvjeyvxrn0')
# streamers = client.users.translate_usernames_to_ids('Gaules')

# for streamer in streamers:
#     streamer_channel_info = {
#         'first_seen': streamer['created_at'],
#         'last_seen': streamer['updated_at'],
#         'streamer_name': streamer['display_name'],
#         'streamer_bio': streamer['bio'],
#         'streamer_logo': streamer['logo'],
#         'streamer_id': streamer['id']
#     }

#     pprint.pprint(streamers)


# token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiNWM1Mzg3MDE5NDE2MWY0NmRmZDg3NzA5Iiwicm9sZSI6Im93bmVyIiwiY2hhbm5lbCI6IjVjNTM4NzAxOTQxN\
#         jFmMGQ1YWQ4NzcwYSIsInByb3ZpZGVyIjoidHdpdGNoIiwiYXV0aFRva2VuIjoiRGlNdGlHU2s2REIxbm94aU9VWEZaOWpJM2UtWVRWVzNoU3BUSlpEX1JHaFA1ajFaIiwiaWF0IjoxN\
#         Tk3OTYxMzg5LCJpc3MiOiJTdHJlYW1FbGVtZW50cyJ9.yXoL9UuH21jEJOJVZVkVGoMBFFaX32RrFqKflmdTdFA'
# custom_params = {
#     'channel_id': '71092938',
#     'channel_name': 'xqcow',
#     'my_id': '239485467'
# }
# querystring = {
#     "interval": "2020",
#     "date": "1597708800",
#     "tz": "est"
# }

# headers = {
#     'accept': 'application/json',
#     'Authorization': f'Bearer {token}',
#     'content-type': "application/json"
# }


# url = f"https://api.streamelements.com/kappa/v2/sessions/{custom_params['my_id']}"

# response = requests.get(url, headers=headers, params=querystring).text

# json_data = json.loads(response)
# json_formatted = json.dumps(json_data, indent=4)

# pprint.pprint(json_formatted)

# grabbing xhr url chart data
# url = 'https://www.twitchmetrics.net/c/71092938-xqcow/stream_growth_values'

# r = requests.get(url)

# with open('viewers.csv', 'wb') as f:
#     f.write(r.content)


client = TwitchClient('9nmje2zw0z52qn0g75wcrbsh1hxwny', 'usw9kto60ddfap0ec1pxxripykehia')
channel = client.channels.get()


headers = {
    'accept': 'application/vnd.twitchtv.v5+json',
    'Client-ID': '9nmje2zw0z52qn0g75wcrbsh1hxwny',
    'Authorization': 'OAuth usw9kto60ddfap0ec1pxxripykehia'
}
r = requests.get('https://api.twitch.tv/kraken/channel', headers=headers).text

pprint.pprint(r)
