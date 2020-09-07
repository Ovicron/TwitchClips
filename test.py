from twitch import TwitchClient
import pprint

client = TwitchClient('9nmje2zw0z52qn0g75wcrbsh1hxwny')

channel_clips = client.clips.get_top('xqcow', limit=1, trending=True)
channel_clips_list = []
for clip in channel_clips:
    clips_info = {
        'name': clip['broadcaster']['display_name'],
        'url': clip['broadcaster']['channel_url'],
        'clip_url': clip['embed_url'],
        'clip_created': clip['created_at'],
        'clip_game': clip['game'],
        'clip_views': clip['views'],
        'clip_thumb': clip['thumbnails']['small']
    }
    channel_clips_list.append(clips_info)

pprint.pprint(channel_clips_list)
