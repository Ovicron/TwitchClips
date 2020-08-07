from twitchclips import app, db, bcrypt, login_manager
from twitchclips.forms import RegisterForm, LoginForm, UpdateAccountForm, PostForm, ClipForm, CommentForm, EditPostForm, EditCommentForm
from twitchclips.models import User, Post, Comment
from flask import render_template, flash, url_for, redirect, request, abort, after_this_request
from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename
# Twitch Clips Imports
from twitchclips.parser import get_clip_link
from twitch import TwitchClient


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
@app.route('/post/<int:post_id>/<action>', methods=['GET', 'POST'])
def like_action(post_id, action):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if action == 'Like':
        current_user.like_post(post)
        db.session.commit()
    if action == 'Dislike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(request.referrer)
# --------------------------------------------------------------------------------------------------------------------


# TWITCH API ROUTES ---------------------------------------------------------------------------------------------------
@app.route('/games')
def games():
    client = TwitchClient(app.config['TWITCH_CLIENT_ID'])
    # games = client.games.get_top(limit=16)
    page = request.args.get('page', 0, type=int)
    page_size = 16
    try:
        games = client.games.get_top(limit=page_size, offset=page * page_size)
    except:
        return redirect(request.referrer)

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
    client = TwitchClient('95asuy3jl29tye4odxmykelgawgot6')
    # streamers = client.streams.get_live_streams(limit=5)
    page = request.args.get('page', 0, type=int)
    page_size = 5
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
            'streamer_logo': stream['channel']['logo']
        }
        streamers_list.append(streams_info)
    return render_template('streamers.html', title='Top Streamers', streamers_list=streamers_list, page=page)

# TODO TOP CLIP ROUTES FROM API
# ---------------------------------------------------------------------------------------------------------------------------
