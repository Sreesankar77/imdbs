import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from extensions import db, bcrypt
from werkzeug.utils import secure_filename
from sqlalchemy.orm import joinedload

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://sankar:sankar_goat@localhost/imdbs_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache for static files

db.init_app(app)
bcrypt.init_app(app)

from models import Admin, User, Movie

# Pagination config
MOVIES_PER_PAGE = 20

# HTTP caching headers
@app.after_request
def add_cache_headers(response):
    """Add cache control headers to responses"""
    if response.content_type and 'text/html' in response.content_type:
        # HTML pages: cache for 5 minutes
        response.cache_control.max_age = 300
        response.cache_control.public = False
    elif response.content_type and any(t in response.content_type for t in ['image/', 'text/css', 'application/javascript']):
        # Static assets: cache for 1 year
        response.cache_control.max_age = 31536000
        response.cache_control.public = True
    
    response.headers['Vary'] = 'Accept-Encoding'
    return response


def seed_admin():
    admin = Admin.query.filter_by(username='sankar').first()
    if not admin:
        pw_hash = bcrypt.generate_password_hash('12345678').decode()
        admin = Admin(username='sankar', password_hash=pw_hash)
        db.session.add(admin)
        db.session.commit()


with app.app_context():
    db.create_all()
    seed_admin()


@app.route('/')
def index():
    return render_template('login.html', show_topbar_controls=False)


@app.route('/create_user', methods=['POST'])
def create_user():
    username = request.form.get('new_username')
    password = request.form.get('new_password')
    if not username or not password:
        flash('Provide username and password', 'error')
        return redirect(url_for('index'))
    if User.query.filter_by(username=username).first():
        flash('User exists', 'error')
        return redirect(url_for('index'))
    pw_hash = bcrypt.generate_password_hash(password).decode()
    user = User(username=username, password_hash=pw_hash)
    db.session.add(user)
    db.session.commit()
    flash('User created. Please login.', 'success')
    return redirect(url_for('index'))


@app.route('/login', methods=['POST'])
def login():
    role = request.form.get('role')
    username = request.form.get('username')
    password = request.form.get('password')
    if role == 'admin':
        admin = Admin.query.filter_by(username=username).first()
        if admin and bcrypt.check_password_hash(admin.password_hash, password):
            session['role'] = 'admin'
            session['user_id'] = admin.id
            return redirect(url_for('home'))
        flash('Invalid admin credentials', 'error')
        return redirect(url_for('index'))
    else:
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['role'] = 'user'
            session['user_id'] = user.id
            return redirect(url_for('home'))
        flash('Invalid user credentials', 'error')
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/home')
def home():
    role = session.get('role')
    page = request.args.get('page', 1, type=int)
    pagination = Movie.query.order_by(Movie.id.desc()).paginate(page=page, per_page=MOVIES_PER_PAGE)
    movies = pagination.items
    return render_template('home.html', role=role, movies=movies, pagination=pagination, show_topbar_controls=True)


@app.route('/debug/home_raw')
def debug_home_raw():
    # returns the rendered HTML of the home page as plain text for debugging cache/template issues
    role = session.get('role')
    page = request.args.get('page', 1, type=int)
    pagination = Movie.query.order_by(Movie.id.desc()).paginate(page=page, per_page=MOVIES_PER_PAGE)
    movies = pagination.items
    rendered = render_template('home.html', role=role, movies=movies, pagination=pagination, show_topbar_controls=True)
    return rendered, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route('/search')
def search():
    q = request.args.get('q', '').strip()
    role = session.get('role')
    page = request.args.get('page', 1, type=int)
    
    if not q:
        pagination = Movie.query.order_by(Movie.id.desc()).paginate(page=page, per_page=MOVIES_PER_PAGE)
    else:
        like = f"%{q}%"
        pagination = Movie.query.filter(
            (Movie.title.ilike(like)) | (Movie.director.ilike(like)) | (Movie.description.ilike(like))
        ).order_by(Movie.rating.desc()).paginate(page=page, per_page=MOVIES_PER_PAGE)
    
    movies = pagination.items
    return render_template('home.html', role=role, movies=movies, pagination=pagination, query=q, show_topbar_controls=True)


@app.route('/add_movie', methods=['GET', 'POST'])
def add_movie():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    if request.method == 'POST':
        title = request.form.get('title')
        director = request.form.get('director')
        rating = request.form.get('rating')
        description = request.form.get('description')
        poster = request.files.get('poster')
        detail_poster = request.files.get('detail_poster')
        scene1 = request.files.get('scene1')
        scene2 = request.files.get('scene2')
        scene3 = request.files.get('scene3')
        def save(f):
            if not f:
                return ''
            fn = secure_filename(f.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], fn)
            f.save(path)
            return 'uploads/' + fn

        movie = Movie(
            title=title,
            director=director,
            rating=float(rating or 0),
            description=description,
            poster=save(poster),
            detail_poster=save(detail_poster),
            scene1=save(scene1),
            scene2=save(scene2),
            scene3=save(scene3),
        )
        db.session.add(movie)
        db.session.commit()
        flash('Movie added', 'success')
        return redirect(url_for('home'))
    return render_template('add_movie.html')


@app.route('/edit_movie/<int:mid>', methods=['GET', 'POST'])
def edit_movie(mid):
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    movie = Movie.query.get_or_404(mid)
    if request.method == 'POST':
        movie.title = request.form.get('title')
        movie.director = request.form.get('director')
        movie.rating = float(request.form.get('rating') or 0)
        movie.description = request.form.get('description')
        db.session.commit()
        flash('Updated', 'success')
        return redirect(url_for('home'))
    return render_template('edit_movie.html', movie=movie)


@app.route('/delete_movie/<int:mid>', methods=['POST'])
def delete_movie(mid):
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    movie = Movie.query.get_or_404(mid)
    db.session.delete(movie)
    db.session.commit()
    flash('Deleted', 'success')
    return redirect(url_for('home'))


@app.route('/movie/<int:mid>')
def movie_detail(mid):
    movie = Movie.query.get_or_404(mid)
    role = session.get('role')
    # fetch other movies by the same director (exclude current)
    related_movies = []
    if movie.director:
        related_movies = Movie.query.filter(
            Movie.director == movie.director,
            Movie.id != movie.id
        ).order_by(Movie.rating.desc()).all()
    return render_template('movie_detail.html', movie=movie, role=role,
                           related_movies=related_movies,
                           show_topbar_controls=True)


@app.route('/director/<director_name>')
def movies_by_director(director_name):
    """List movies that have exactly the given director name."""
    role = session.get('role')
    page = request.args.get('page', 1, type=int)
    pagination = Movie.query.filter(Movie.director == director_name)
    pagination = pagination.order_by(Movie.rating.desc()).paginate(page=page, per_page=MOVIES_PER_PAGE)
    movies = pagination.items
    return render_template('home.html', role=role, movies=movies,
                           pagination=pagination, query=director_name,
                           show_topbar_controls=True)


@app.route('/movie')
@app.route('/movie/')
def movie_index_redirect():
    flash('No movie selected. Redirected to homepage.', 'error')
    return redirect(url_for('home'))


@app.route('/debug/movie_raw/<int:mid>')
def debug_movie_raw(mid):
    movie = Movie.query.get_or_404(mid)
    role = session.get('role')
    rendered = render_template('movie_detail.html', movie=movie, role=role, show_topbar_controls=True)
    return rendered, 200, {'Content-Type': 'text/plain; charset=utf-8'}


@app.route('/dashboard')
def dashboard():
    if session.get('role') != 'user':
        flash('Please login as user to view dashboard', 'error')
        return redirect(url_for('home'))
    # Use eager loading to avoid N+1 queries
    user = (User.query
            .options(joinedload(User.watchlist), joinedload(User.watched), joinedload(User.favourites))
            .get(session['user_id']))
    watchlist = user.watchlist if user else []
    watched = user.watched if user else []
    favourites = user.favourites if user else []
    return render_template('dashboard.html', watchlist=watchlist, watched=watched, favourites=favourites, show_topbar_controls=True, role='user')


@app.route('/add_to_watchlist/<int:mid>', methods=['POST'])
def add_to_watchlist(mid):
    if session.get('role') != 'user':
        return redirect(url_for('home'))
    user = User.query.get(session['user_id'])
    movie = Movie.query.get_or_404(mid)
    if movie not in user.watchlist:
        user.watchlist.append(movie)
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/mark_watched/<int:mid>', methods=['POST'])
def mark_watched(mid):
    if session.get('role') != 'user':
        return redirect(url_for('home'))
    user = User.query.get(session['user_id'])
    movie = Movie.query.get_or_404(mid)
    if movie not in user.watched:
        user.watched.append(movie)
        db.session.commit()
    return redirect(url_for('home'))


@app.route('/add_fav/<int:mid>', methods=['POST'])
def add_fav(mid):
    if session.get('role') != 'user':
        return redirect(url_for('home'))
    user = User.query.get(session['user_id'])
    movie = Movie.query.get_or_404(mid)
    if movie not in user.favourites:
        user.favourites.append(movie)
        db.session.commit()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
