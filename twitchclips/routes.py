from twitchclips import app, db, bcrypt, login_manager
from twitchclips.forms import RegisterForm, LoginForm, UpdateAccountForm, PostForm
from twitchclips.models import User, Post
from flask import render_template, flash, url_for, redirect, request, send_file
from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename
import io


@app.route('/')
@app.route('/home')
def home():
    posts = Post.query.all()
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


# USER SETTINGS PAGE AND PREFERENCES  ------------------------------------------------------------------------
@login_required
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if not current_user.is_authenticated:
        flash('You must login to access that page.', 'danger')
        return redirect(url_for('home'))

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
    if current_user.is_authenticated:
        db.session.query(User).filter_by(id=current_user.id).delete()
        db.session.commit()
        flash('Your account has been deleted!', 'success')
        return redirect(url_for('home'))
    return render_template('settings.html', title='Account Settings')


@login_required
@app.route('/delete/posts', methods=['GET', 'POST'])
def delete_all_posts():
    if current_user.is_authenticated:
        db.session.query(Post).filter(Post.user_id == current_user.id).delete()
        db.session.commit()
        flash('All your posts has been deleted!', 'success')
        return redirect(url_for('home'))
# -----------------------------------------------------------------------------------------------------------


# USER POSTS AND IMAGE UPLOADS ------------------------------------------------------------------------------------
app.config['IMAGE_UPLOADS'] = 'C:/Users/ovicr/Desktop/VSCode Projects/TwitchClips/twitchclips/static/images/uploads'
app.config['ALLOWED_IMG_EXTENSIONS'] = ['JPG', 'PNG', 'JPEG', 'GIF']
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


@app.route('/create/post', methods=['GET', 'POST'])
def create_post():
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
                    app.config['IMAGE_UPLOADS'], image.filename))
    # Regular Posts
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data, link=filename, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('Post submitted', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='Create Post', form=form)
# -----------------------------------------------------------------------------------------------------------
