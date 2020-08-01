from twitchclips import app, db, bcrypt, login_manager
from twitchclips.forms import RegisterForm, LoginForm, UpdateAccountForm, PostForm, CommentForm, EditPostForm, EditCommentForm
from twitchclips.models import User, Post, Comment
from flask import render_template, flash, url_for, redirect, request, abort, after_this_request
from flask_login import login_user, logout_user, login_required, current_user
import os
from werkzeug.utils import secure_filename


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


# USER CREATES POST AND IMAGE UPLOADS ---------------------------------------------------------------------------------
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
                    app.config['IMAGE_UPLOADS'], filename))

                path = os.path.join(app.config['IMAGE_UPLOADS'], filename)
                print(path)
                new_path = path.split('twitchclips')[-1]

    # Regular Posts
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data,
                    body=form.body.data, link=new_path, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post submitted', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='Create Post', form=form)
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
    posts = Post.query.filter_by(
        author=current_user).order_by(Post.date_posted.desc())
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
# -----------------------------------------------------------------------------------------------------------


# COMMENT ROUTES -----------------------------------------------------------------------------------------------
@app.route('/post/<int:post_id>/comment', methods=['GET', 'POST'])
def comment(post_id):
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
# -----------------------------------------------------------------------------------------------------------
