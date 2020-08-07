import requests
import json


def get_clip_link(link):
    try:
        slug = link.split('/')[-1]

        url = 'https://gql.twitch.tv/gql'

        headers = {
            'Client-Id': 'kimne78kx3ncx6brgo4mv6wki5h1ko',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://clips.twitch.tv',
            'Referer': f'https://clips.twitch.tv/{slug}',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        }

        payload = [{"operationName": "VideoAccessToken_Clip", "variables": {"slug": slug}, "extensions": {
            "persistedQuery": {"version": 1, "sha256Hash": "9bfcc0177bffc730bd5a5a89005869d2773480cf1738c592143b5173634b7d15"}}}]

        r = requests.post(url, data=json.dumps(payload[0]), headers=headers)
        video_url = json.loads(r.text)
        video_url = video_url['data']['clip']['videoQualities'][0]['sourceURL']

        filename = f"{video_url}"
    except:
        return "Invalid link for clip"

    return filename
