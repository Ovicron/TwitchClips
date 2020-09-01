import pprint
import schedule
import time
import csv
from twitch import TwitchClient
from datetime import datetime as dt, timedelta
from twitchclips import app, db
from twitchclips.models import AverageViewers

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


schedule.every(15).minutes.do(save_viewers)

while True:
    schedule.run_pending()
    time.sleep(1)


# def delete_7_days():
#     DAYS = 7
#     cutoff = (dt.utcnow() - timedelta(days=DAYS))
#     AverageViewers.query.filter_by(date_snapped <= cutoff).delete()
#     db.session.commit()


# delete_7_days()

# TODO migrate postgres? make sure delete after certain time period, works.
