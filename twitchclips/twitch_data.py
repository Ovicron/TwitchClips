from twitch import TwitchClient
import pprint


# def get_top_games():
#     client = TwitchClient('95asuy3jl29tye4odxmykelgawgot6')
#     games = client.games.get_top(limit=2)

#     for game in games:
#         game_info = {
#             'name': game['game']['name'],
#             'viewers': game['viewers'],
#             'thumbnail': game['game']['box']['large']
#         }
#         return game_info


# def get_top_streams():
#     client = TwitchClient('95asuy3jl29tye4odxmykelgawgot6')
#     streamers = client.streams.get_live_streams(limit=2)

#     for stream in streamers:
#         streams_info = {
#             'streamer_name': stream['channel']['display_name'],
#             'current_game': stream['channel']['game'],
#             'current_viewers': stream['viewers'],
#             'stream_thumbnail': stream['preview']['large'],
#             'stream_url': stream['channel']['url']
#         }
#         pprint.pprint(streams_info)


# get_top_streams()


# client = TwitchClient('95asuy3jl29tye4odxmykelgawgot6')

# clips_day = client.clips.get_top(limit=12, period="day")
# clips_day_list = []
# for clip_day in clips_day:
#     clips_info_day = {
#         'clip_url': clip_day['embed_url'],
#         'clip_thumb': clip_day['thumbnails']['medium'],
#         'clip_title': clip_day['title'],
#         'clip_views': clip_day['views'],
#         'clip_category': clip_day['game']
#     }
#     clips_day_list.append(clips_info_day)


# clips_week = client.clips.get_top(limit=12, period="week")
# clips_week_list = []
# for clip_week in clips_week:
#     clips_info_week = {
#         'clip_url': clip_week['embed_url'],
#         'clip_thumb': clip_week['thumbnails']['medium'],
#         'clip_title': clip_week['title'],
#         'clip_views': clip_week['views'],
#         'clip_category': clip_week['game']
#     }
#     clips_week_list.append(clips_info_week)

# clips_month = client.clips.get_top(limit=12, period="month")
# clips_month_list = []
# for clip_month in clips_month:
#     clips_info_month = {
#         'clip_url': clip_month['embed_url'],
#         'clip_thumb': clip_month['thumbnails']['medium'],
#         'clip_title': clip_month['title'],
#         'clip_views': clip_month['views'],
#         'clip_category': clip_month['game']
#     }
#     clips_month_list.append(clips_info_month)

# clips_all = client.clips.get_top(limit=12, period="all")
# clips_all_list = []
# for clip_all in clips_all:
#     clips_info_all = {
#         'clip_url': clip_all['embed_url'],
#         'clip_thumb': clip_all['thumbnails']['medium'],
#         'clip_title': clip_all['title'],
#         'clip_views': clip_all['views'],
#         'clip_category': clip_all['game']
#     }
#     clips_all_list.append(clips_info_all)

# pprint.pprint(clips_all_list)