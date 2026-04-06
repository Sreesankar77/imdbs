from extensions import db


watchlist_table = db.Table('watchlist',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'))
)

watched_table = db.Table('watched',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'))
)

fav_table = db.Table('favourites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'))
)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    watchlist = db.relationship('Movie', secondary=watchlist_table, backref='watchlisted_by')
    watched = db.relationship('Movie', secondary=watched_table, backref='watched_by')
    favourites = db.relationship('Movie', secondary=fav_table, backref='fav_by')


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    director = db.Column(db.String(120))
    rating = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text)
    poster = db.Column(db.String(300))
    detail_poster = db.Column(db.String(300))
    scene1 = db.Column(db.String(300))
    scene2 = db.Column(db.String(300))
    scene3 = db.Column(db.String(300))
