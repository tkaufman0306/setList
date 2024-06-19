"""models.py file for setList app"""


from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

app = Flask(__name__)

def connect_db(app):
    """ connect to database."""

    db.app = app
    db.init_app(app)
    app.app_context().push()
    db.create_all()


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
    
    password_hash = db.Column(db.Text, 
                              nullable=False)
    
    songs = db.relationship('Song', 
                            backref='user', 
                            lazy=True)
    
    setlists = db.relationship('Setlist',
                                backref='user', lazy=True)

class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    lyrics = db.Column(db.Text, nullable=False)
    api_source = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    chords = db.relationship('Chord', backref='song', lazy=True)

@app.route('/add-chord', methods=['POST'])
def add_chord():
    chord = request.form['chord']
    word_index = int(request.form['word_index'])
    song_id = int(request.form['song_id'])


class Chord(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    chord_name = db.Column(db.String(20), nullable=False)
    position = db.Column(db.Integer, nullable=False) # Position of the chord within the lyrics
    word_index = db.Column(db.Integer, nullable = False) # Index of the word within the lyrics
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    words = db.relationship('Word', secondary='chord_word_association', backref='chords', lazy=True)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word_text = db.Column(db.String(100), nullable=False)

# Association Table for the many-to-many relationship between chords and words

chord_word_association = db.Table('chord_word_association',
    db.Column('chord_id', db.Integer, db.ForeignKey('chord.id'),            primary_key=True),
    db.Column('word_id', db.Integer, db.ForeignKey('word.id'),            primary_key=True),
 )

class Setlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    songs = db.relationship('Song', secondary='setlist_songs', backref=db.backref('setlists', lazy=True))

class SetlistSongs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    setlist_id = db.Column(db.Integer, db.ForeignKey('setlist.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)

