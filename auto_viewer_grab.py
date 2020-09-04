from twitchclips import app, db
from twitchclips.models import AverageViewers, Post
import time
from twitch import TwitchClient
from datetime import datetime as dt, timedelta
from apscheduler.schedulers.background import BackgroundScheduler


def save_viewers():
    client = TwitchClient(client_id=app.config['TWITCH_CLIENT_ID'])
    streams = client.streams.get_live_streams(limit=100)
    dt_now = dt.utcnow()

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


if __name__ == '__main__':
    schedular = BackgroundScheduler()
    schedular.add_job(save_viewers, 'interval', minutes=10)
    schedular.start()

    while True:
        time.sleep(1)
