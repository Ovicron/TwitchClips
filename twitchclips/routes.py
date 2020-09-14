from twitchclips import app, db, bcrypt, login_manager
from twitchclips.forms import RegisterForm, LoginForm, UpdateAccountForm, PostForm, ClipForm, CommentForm, EditPostForm, EditCommentForm
from twitchclips.models import User, Post, Comment, AverageViewers
from flask import render_template, flash, url_for, redirect, request, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename
from twitchclips.parser import get_clip_link  # Clip uploads parser
from twitch import TwitchClient  # Twitch API
# scraping
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import json
import random
# caching
from twitchclips import cache
# time
import humanize
import datetime as dt
import time


@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.order_by(Post.date_posted.desc())
    return render_template('home.html', title='Home', posts=posts)


# USER REGISTRATION AND LOGIN VIEWS --------------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(
            password=form.password.data).decode('utf-8')
        user = User(email=form.email.data,
                    username=form.username.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('You have been logged in.', 'success')
            return redirect('next_page') if next_page else redirect(url_for('home'))
        else:
            flash('Incorrect password or username', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))
# -----------------------------------------------------------------------------------------------------------


# USER SETTINGS PAGE AND PREFERENCES ------------------------------------------------------------------------
@login_required
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if not current_user.is_authenticated:
        flash('You must login to access that page.', 'danger')
        return redirect(url_for('login'))

    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Information updated!', 'success')
        return redirect(url_for('settings'))
    else:
        request.method == 'GET'
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('settings.html', title='Account Settings', form=form)


@login_required
@app.route('/delete/account', methods=['GET', 'POST'])
def delete_account():
    if not current_user.is_authenticated:
        abort(403)

    if current_user.is_authenticated:
        db.session.query(User).filter_by(id=current_user.id).delete()
        db.session.commit()
        flash('Your account has been deleted!', 'success')
        return redirect(url_for('home'))
    return render_template('settings.html', title='Account Settings')


@login_required
@app.route('/delete/posts', methods=['GET', 'POST'])
def delete_all_posts():
    if not current_user.is_authenticated:
        abort(403)

    if current_user.is_authenticated:
        db.session.query(Post).filter(Post.user_id == current_user.id).delete()
        db.session.commit()
        flash('All your posts has been deleted!', 'success')
        return redirect(url_for('home'))
# -----------------------------------------------------------------------------------------------------------


# USER CREATES POST AND IMAGE/CLIP UPLOADS ---------------------------------------------------------------------------
app.config['IMAGE_UPLOADS'] = 'C:/Users/ovicr/Desktop/VSCode Projects/TwitchClips/twitchclips/static/images/uploads'
app.config['ALLOWED_IMG_EXTENSIONS'] = ['JPG', 'PNG', 'JPEG', 'GIF', 'MP4', 'WEBM', "MOV"]
app.config['MAX_IMG_SIZE'] = 5000000


def allowed_images(filename):
    if not '.' in filename:
        return False

    ext = filename.rsplit('.', 1)[1]

    if ext.upper() in app.config['ALLOWED_IMG_EXTENSIONS']:
        return True
    else:
        return False


def allowed_image_size(filesize):
    if int(filesize) >= app.config['MAX_IMG_SIZE']:
        return True
    else:
        return False


@login_required
@app.route('/submit/post', methods=['GET', 'POST'])
def submit_post():
    if not current_user.is_authenticated:
        abort(403)

    # Image upload and validation
    if request.method == 'POST':
        if request.files:

            if allowed_image_size(request.cookies.get('filesize')):
                flash('Image exceeds the maximum size limit of 5 MB!', 'danger')
                return redirect(request.url)

            image = request.files['uploadImg']

            if image.filename == '':
                flash('No image detected or file name is empty!', 'danger')
                return redirect(request.url)

            if not allowed_images(image.filename):
                flash('Invalid image extension!', 'danger')
                return redirect(request.url)
            else:
                filename = secure_filename(image.filename)
                image.save(os.path.join(
                    app.config['IMAGE_UPLOADS'], filename))

                path = os.path.join(app.config['IMAGE_UPLOADS'], filename)
                new_path = path.split('twitchclips')[-1]

    # Regular Posts with Image
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, clip="NONE", body=form.body.data, link=new_path, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post submitted', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='Submit Post', form=form)


# CLIP POST ROUTE
@app.route('/submit/clip', methods=['GET', 'POST'])
def submit_clip():
    if not current_user.is_authenticated:
        abort(403)

    form = ClipForm()
    if form.validate_on_submit():
        clip_mp4 = get_clip_link(link=form.clip.data)
        post = Post(title=form.title.data, clip=clip_mp4, body=form.body.data, link="NONE", author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Clip submitted', 'success')
        return redirect(url_for('home'))
    return render_template('create_clip.html', title='Submit Clip', form=form)
# -----------------------------------------------------------------------------------------------------------


# POST ROUTES -----------------------------------------------------------------------------------------------
@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_page(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter_by(post_id=post.id)
    return render_template('post_page.html', title=post.title, post=post, comments=comments)


@app.route('/user/<string:username>')
def user_posts(username):
    user = User.query.filter_by(username=username).first()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc())
    return render_template('user_posts.html', title=f"Submissions by: {user.username}", user=user, posts=posts)


@login_required
@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)

    form = EditPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.commit()
        flash('Post updated', 'success')
        return redirect(url_for('post_page', post_id=post.id))
    else:
        form.title.data = post.title
        form.body.data = post.body
    return render_template('edit_post.html', title='Edit Post', form=form)


@login_required
@app.route('/post/<int:post_id>/delete')
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    else:
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted!', 'success')
    return redirect(url_for('home'))
# -------------------------------------------------------------------------------------------------------------


# COMMENT ROUTES -----------------------------------------------------------------------------------------------
@login_required
@app.route('/post/<int:post_id>/comment', methods=['GET', 'POST'])
def comment(post_id):
    if not current_user.is_authenticated:
        abort(403)

    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          user_id=current_user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment posted.', 'success')
        return redirect(url_for('post_page', post_id=post.id))
    return render_template('reply.html', title=f"Reply to {post.author.username}", post=post, form=form)


@login_required
@app.route('/edit/comment/<int:comment_id>', methods=['GET', 'POST'])
def edit_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        abort(403)
    form = EditCommentForm()
    if form.validate_on_submit():
        comment.body = form.body.data
        db.session.commit()
        flash('Comment updated!', 'success')
    else:
        request.method == 'GET'
        form.body.data = comment.body
    return render_template('edit_reply.html', title='Edit Reply', form=form)


@login_required
@app.route('/delete/comment/<int:comment_id>')
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.author != current_user:
        abort(403)
    else:
        db.session.delete(comment)
        db.session.commit()
        flash('Comment deleted', 'success')
    return redirect(request.referrer)
# -----------------------------------------------------------------------------------------------------------------


# RATINGS ROUTES ---------------------------------------------------------------------------------------------------
@login_required
@app.route('/post/<int:post_id>/<action>/', methods=['GET', 'POST'])
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'Like':
        current_user.like_post(post)
        db.session.commit()
        flash('Liked Post', 'success')
        return redirect(url_for('post_page', post_id=post.id))
    if action == 'Dislike':
        current_user.unlike_post(post)
        db.session.commit()
        flash('Disliked Post', 'warning')
        return redirect(url_for('post_page', post_id=post.id))
# --------------------------------------------------------------------------------------------------------------------


# ERROR HANDLER ROUTES --------------------------------------------------------------------------------------------------
@app.errorhandler(404)
def error_404(e):
    return render_template('error_templates/404.html', title='Not Found 404')


@app.errorhandler(403)
def error_403(e):
    return render_template('error_templates/403.html', title='Forbidden 403')


@app.errorhandler(500)
def error_500(e):
    return render_template('error_templates/500.html', title='Internal Server Error 500')
# ------------------------------------------------------------------------------------------------------------------------


# TWITCH API ROUTES ---------------------------------------------------------------------------------------------------
@app.route('/games')
def games():
    client = TwitchClient(app.config['TWITCH_CLIENT_ID'])
    page = request.args.get('page', 0, type=int)
    page_size = 20
    try:
        games = client.games.get_top(limit=page_size, offset=page * page_size)
    except:
        return redirect(request.referrer)
    # games = client.games.get_top(limit=20)

    games_list = []
    for game in games:
        game_info = {
            'name': game['game']['name'],
            'viewers': game['viewers'],
            'thumbnail': game['game']['box']['large']
        }
        games_list.append(game_info)
    return render_template('games.html', title='Top Games', games_list=games_list, page=page)


@app.route('/streamers')
def streamers():
    client = TwitchClient(app.config['TWITCH_CLIENT_ID'])
    page = request.args.get('page', 0, type=int)
    page_size = 12
    try:
        streamers = client.streams.get_live_streams(limit=page_size, offset=page * page_size)
    except:
        return redirect(request.referrer)

    streamers_list = []
    for stream in streamers:
        streams_info = {
            'streamer_name': stream['channel']['display_name'],
            'current_game': stream['channel']['game'],
            'current_viewers': stream['viewers'],
            'stream_thumbnail': stream['preview']['large'],
            'stream_url': stream['channel']['url'],
            'streamer_logo': stream['channel']['logo'],
            # 'streamer_banner': stream['channel']['profile_banner']
        }
        streamers_list.append(streams_info)
    return render_template('streamers.html', title='Top Streamers', streamers_list=streamers_list, page=page)


@app.route('/clips')
def clips():
    client = TwitchClient(app.config['TWITCH_CLIENT_ID'])

    # TOP CLIPS API CALLS:
    clips_day = client.clips.get_top(limit=12, period="day")
    clips_day_list = []
    for clip_day in clips_day:
        clips_info_day = {
            'clip_url': clip_day['embed_url'],
            'clip_thumb': clip_day['thumbnails']['medium'],
            'clip_title': clip_day['title'],
            'clip_views': clip_day['views'],
            'clip_game': clip_day['game'],
            'clip_streamer': clip_day['broadcaster']['display_name'],
        }
        clips_day_list.append(clips_info_day)
    # WEEK
    clips_week = client.clips.get_top(limit=12, period="week")
    clips_week_list = []
    for clip_week in clips_week:
        clips_info_week = {
            'clip_url': clip_week['embed_url'],
            'clip_thumb': clip_week['thumbnails']['medium'],
            'clip_title': clip_week['title'],
            'clip_views': clip_week['views'],
            'clip_game': clip_week['game'],
            'clip_streamer': clip_day['broadcaster']['display_name'],
        }
        clips_week_list.append(clips_info_week)
    # MONTH
    clips_month = client.clips.get_top(limit=12, period="month")
    clips_month_list = []
    for clip_month in clips_month:
        clips_info_month = {
            'clip_url': clip_month['embed_url'],
            'clip_thumb': clip_month['thumbnails']['medium'],
            'clip_title': clip_month['title'],
            'clip_views': clip_month['views'],
            'clip_game': clip_month['game'],
            'clip_streamer': clip_day['broadcaster']['display_name'],
        }
        clips_month_list.append(clips_info_month)
    # ALL
    clips_all = client.clips.get_top(limit=12, period="all")
    clips_all_list = []
    for clip_all in clips_all:
        clips_info_all = {
            'clip_url': clip_all['embed_url'],
            'clip_thumb': clip_all['thumbnails']['medium'],
            'clip_title': clip_all['title'],
            'clip_views': clip_all['views'],
            'clip_game': clip_all['game'],
            'clip_streamer': clip_day['broadcaster']['display_name'],
        }
        clips_all_list.append(clips_info_all)
    return render_template('clips.html', title='Top Clips', clips_day_list=clips_day_list, clips_week_list=clips_week_list,
                           clips_month_list=clips_month_list, clips_all_list=clips_all_list)


@app.template_filter()
def commaFormat(value):
    value = int(value)
    return f"{value:,}"
# ---------------------------------------------------------------------------------------------------------------------------


# STREAMER SPECIFIC ROUTES DATA/ETC --------------------------------------------------------------------------------------------------
@app.route('/streamers/<string:streamer>')
def streamers_page(streamer):
    # ALL TIME STATISTICS -----------------------------
    session = HTMLSession()
    r = session.get(f'https://sullygnome.com/channel/{streamer}/365')

    peak_viewers_elem = r.html.find('div.InfoStatPanelWrapper:nth-child(5) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)')
    peak_viewers = []
    p_v = peak_viewers_elem[0].text
    peak_viewers.append(p_v)

    hours_streamed_elem = r.html.find('div.InfoStatPanelWrapper:nth-child(6) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)')
    hours_streamed = []
    h_s = hours_streamed_elem[0].text
    hours_streamed.append(h_s)

    # MONTHLY STATISTICS -----------------------------
    session = HTMLSession()
    r = session.get(f'https://sullygnome.com/channel/{streamer}/30')

    avg_viewers_elem = r.html.find('div.InfoStatPanelWrapper:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)')
    avg_viewers = []
    a_v = avg_viewers_elem[0].text
    avg_viewers.append(a_v)

    hrs_watched_elem = r.html.find('div.InfoStatPanelWrapper:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)')
    hrs_watched = []
    h_w = hrs_watched_elem[0].text
    hrs_watched.append(h_w)

    hours_streamed_elem_month = r.html.find('div.InfoStatPanelWrapper:nth-child(6) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)')
    hours_streamed_month = []
    h_s_m = hours_streamed_elem_month[0].text
    hours_streamed_month.append(h_s_m)

    peak_viewers_elem_month = r.html.find('div.InfoStatPanelWrapper:nth-child(5) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)')
    peak_viewers_month = []
    p_v_m = peak_viewers_elem_month[0].text
    peak_viewers_month.append(p_v_m)

    # GROWTH CHART CHART -------------------------------
    chart_streamer = AverageViewers.query.filter_by(streamer=streamer.lower()).all()

    # Streamer specific data ----------------------------
    client = TwitchClient(app.config['TWITCH_CLIENT_ID'])

    users = client.users.translate_usernames_to_ids(streamer)
    streamers_page_list = []
    for user in users:
        streamer_channel_info = {
            'first_seen': user['created_at'],
            'last_seen': user['updated_at'],
            'name': user['display_name'],
            'bio': user['bio'],
            'logo': user['logo'],
            'id': user['id']
        }
        last_seen_time = streamer_channel_info['last_seen']
        readable_time = humanize.naturaldelta(last_seen_time - dt.datetime.now())
        streamers_page_list.append(streamer_channel_info)

    channel = client.channels.get_by_id(users[0]['id'])
    channel_page_list = []
    channel_info = {
        'language': channel['broadcaster_language'],
        'type': channel['broadcaster_type'],
        'followers': channel['followers'],
        'views': channel['views'],
        'current_game': channel['game'],
        'current_status': channel['status'],
        'channel_url': channel['url'],
        'channel_banner': channel['video_banner']
    }
    channel_page_list.append(channel_info)

    stream_status = []
    if users == []:
        pass
    else:
        channel = client.streams.get_stream_by_user(users[0]['id'])
        if channel == None:
            pass
        else:
            live_status = {
                "status": channel['broadcast_platform'],
                "viewers": channel['viewers']
            }
            stream_status.append(live_status)

    # STREAMER CLIPS -----------------------------------
    channel_clips = client.clips.get_top(f'{streamer}', limit=4, period='all')
    channel_clips_list = []
    for clip in channel_clips:
        clips_info = {
            'name': clip['broadcaster']['display_name'],
            'url': clip['broadcaster']['channel_url'],
            'clip_url': clip['embed_url'],
            'clip_game': clip['game'],
            'clip_views': clip['views'],
            'clip_thumb': clip['thumbnails']['small']
        }
        channel_clips_list.append(clips_info)

    return render_template('streamers_page.html', title=f'Overview for streamer {streamer}', streamer=streamer, channel_page_list=channel_page_list,
                           streamers_page_list=streamers_page_list, stream_status=stream_status, readable_time=readable_time, chart_streamer=chart_streamer,
                           peak_viewers=peak_viewers, hours_streamed=hours_streamed, avg_viewers=avg_viewers, hrs_watched=hrs_watched,
                           hours_streamed_month=hours_streamed_month, peak_viewers_month=peak_viewers_month, channel_clips_list=channel_clips_list)


# DELETES CHART DATA OLDER THAN 7 DAYS.
@app.route('/delete_7_days_or_older_data')
def delete_7_days():
    AverageViewers.delete_older_than_7_days()
    ''''http://:5000/delete_7_days_or_older_data'''
    return 'Deleted all data older than 7 days!'
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------


# STREAMER SPECIFIC CLIPS -----------------------------------------------------------------------------------------------------------------------------------------
@app.route('/streamer/<string:streamer>/clips')
def more_clips(streamer):
    client = TwitchClient(app.config['TWITCH_CLIENT_ID'])

    # clips ------------------------------------
    clips = client.clips.get_top(f'{streamer}', limit=100, period='all')
    clips_list = []
    for clip in clips:
        clips_info = {
            'url': clip['broadcaster']['channel_url'],
            'clip_url': clip['embed_url'],
            'game': clip['game'],
            'views': clip['views'],
            'thumb': clip['thumbnails']['small'],
            'title': clip['title'],
        }
        clips_list.append(clips_info)

    # streamer logo -----------------------------
    users = client.users.translate_usernames_to_ids(streamer)
    logo = users[0]['logo']

    return render_template('streamer_clips_templates/more_clips.html', title=f"{streamer}'s Clips", streamer=streamer, logo=logo, clips_list=clips_list)


@app.route('/streamer/<string:streamer>/clips/monthly')
def monthly_streamer_clips(streamer):
    client = TwitchClient(app.config['TWITCH_CLIENT_ID'])

    # clips month------------------------------------
    clips = client.clips.get_top(f'{streamer}', limit=100, period='month')
    clips_list = []
    for clip in clips:
        clips_info = {
            'url': clip['broadcaster']['channel_url'],
            'clip_url': clip['embed_url'],
            'game': clip['game'],
            'views': clip['views'],
            'thumb': clip['thumbnails']['small'],
            'title': clip['title'],
        }
        clips_list.append(clips_info)

    # streamer logo -----------------------------
    users = client.users.translate_usernames_to_ids(streamer)
    logo = users[0]['logo']
    return render_template('streamer_clips_templates/monthly.html', title=f"{streamer}'s Clips", streamer=streamer, logo=logo, clips_list=clips_list)


@app.route('/streamer/<string:streamer>/clips/weekly')
def weekly_streamer_clips(streamer):
    client = TwitchClient(app.config['TWITCH_CLIENT_ID'])

    # clips week------------------------------------
    clips = client.clips.get_top(f'{streamer}', limit=100, period='week')
    clips_list = []
    for clip in clips:
        clips_info = {
            'url': clip['broadcaster']['channel_url'],
            'clip_url': clip['embed_url'],
            'game': clip['game'],
            'views': clip['views'],
            'thumb': clip['thumbnails']['small'],
            'title': clip['title'],
        }
        clips_list.append(clips_info)

    users = client.users.translate_usernames_to_ids(streamer)
    logo = users[0]['logo']
    return render_template('streamer_clips_templates/weekly.html', title=f"{streamer}'s Clips", streamer=streamer, logo=logo, clips_list=clips_list)


@app.route('/streamer/<string:streamer>/clips/daily')
def daily_streamer_clips(streamer):
    client = TwitchClient(app.config['TWITCH_CLIENT_ID'])

    # clips daily------------------------------------
    clips = client.clips.get_top(f'{streamer}', limit=100, period='day')
    clips_list = []
    for clip in clips:
        clips_info = {
            'url': clip['broadcaster']['channel_url'],
            'clip_url': clip['embed_url'],
            'game': clip['game'],
            'views': clip['views'],
            'thumb': clip['thumbnails']['small'],
            'title': clip['title'],
        }
        clips_list.append(clips_info)

    users = client.users.translate_usernames_to_ids(streamer)
    logo = users[0]['logo']
    return render_template('streamer_clips_templates/daily.html', title=f"{streamer}'s Clips", streamer=streamer, logo=logo, clips_list=clips_list)
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------
# todo paginated ranks.........update passwords for users...... some form of search functionality... games page streamers
