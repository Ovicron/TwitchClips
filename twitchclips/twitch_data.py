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


def get_top_streams():
    client = TwitchClient('95asuy3jl29tye4odxmykelgawgot6')
    streamers = client.streams.get_live_streams(limit=2)

    for stream in streamers:
        streams_info = {
            'streamer_name': stream['channel']['display_name'],
            'current_game': stream['channel']['game'],
            'current_viewers': stream['viewers'],
            'stream_thumbnail': stream['preview']['large'],
            'stream_url': stream['channel']['url']
        }
        pprint.pprint(streams_info)


get_top_streams()
