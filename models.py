"""models.py file for setList app"""

from flask_sqlalchemy import SQLAlchemy

from flask import Flask, render_template, request, redirect, url_for, jsonify

from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

app = Flask(__name__)

# from app import db

def connect_db(app):
    """ connect to database."""

    db.app = app
    db.init_app(app)
    app.app_context().push()
    db.create_all()

setlist_songs = db.Table(
    'setlist_songs',
    db.Column('setlist_id', db.Integer, db.ForeignKey('setlist.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'), primary_key=True)
)

class Setlist(db.Model):
    __tablename__ = 'setlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    songs = db.relationship('Song', secondary=('setlist_songs'), backref=db.backref('setlists', lazy=True))


class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    lyrics = db.Column(db.Text, nullable=False)
    api_source = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chords = db.relationship('Chord', backref='songs', lazy=True)


class SetlistSong(db.Model):

    __tablename__ = 'setlist_songs'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    
    setlist_id = db.Column(db.Integer, db.ForeignKey('setlists.id'), primary_key=True, nullable=False)
    
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), primary_key=True, nullable=False)

    # Define relationships
    setlist = db.relationship('Setlist', backref=db.backref('setlist_songs', cascade='all, delete-orphan'))
    song = db.relationship('Song', backref=db.backref('setlist_songs', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<SetlistSong id={self.id} setlist_id={self.setlist_id} song_id={self.song_id}>'

class User(db.Model):
    """Site user."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, 
                   primary_key=True,        autoincrement=True)
    
    username = db.Column(db.Text, 
                         unique=True, 
                         nullable=False)
    
    email = db.Column(db.Text, 
                      unique=True, 
                      nullable=False)
    
    password_hash = db.Column(db.String(200), 
                              nullable=False)
    
    songs = db.relationship('Song', 
                            backref='user', 
                            lazy=True)
    
    setlists = db.relationship('Setlist',
                                backref='user', lazy=True)
    
    @classmethod
    def register(cls, username, password):
        """Register user with hashed password and return user instance."""
        hashed_pwd = generate_password_hash(password)
        return cls(username=username, password_hash=hashed_pwd)
    
    def check_password(self, password):
        """check if password matches hashed password."""
        return check_password_hash(self.password_hash, password)

class Chord(db.Model):

    __tablename__ = 'chords'
    id = db.Column(db.Integer, primary_key=True)
    chord_name = db.Column(db.String(20), nullable=False)
    position = db.Column(db.Integer, nullable=False) # Position of the chord within the lyrics
    word_index = db.Column(db.Integer, nullable = False) # Index of the word within the lyrics
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    words = db.relationship('Word', secondary='chord_word_association', backref='chords', lazy=True)

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word_text = db.Column(db.String(100), nullable=False)

# Association Table for the many-to-many relationship between chords and words

class ChordWordAssociation(db.Model):
    __tablename__ = 'chord_word_association',
    chord_id = db.Column('chord_id', db.Integer, db.ForeignKey('chords.id'), primary_key=True)
    word_id = db.Column('word_id', db.Integer, db.ForeignKey('words.id'), primary_key=True)
 





