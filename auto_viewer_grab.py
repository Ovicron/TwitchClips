from twitchclips import app, db
from twitchclips.models import AverageViewers, Post
import schedule
import time
from twitch import TwitchClient
from datetime import datetime as dt, timedelta

client = TwitchClient(client_id=app.config['TWITCH_CLIENT_ID'])
streams = client.streams.get_live_streams(limit=100)
dt_now = dt.utcnow()


def save_viewers():
    for stream in streams:
        data = {
            'streamer': stream['channel']['name'],
            'viewers': stream['viewers'],
            'date': dt_now
        }

        streamer_viewer_data = AverageViewers(streamer=data['streamer'], viewers=data['viewers'], date_snapped=data['date'])
        db.session.add(streamer_viewer_data)
        db.session.commit()
        print('SAVED TO DATABASE')


schedule.every(5).seconds.do(save_viewers)

while True:
    schedule.run_pending()
    time.sleep(1)
