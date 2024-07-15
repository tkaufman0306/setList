"""models.py file for setList app"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from bcrypt import hashpw, checkpw, gensalt

db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    db.init_app(app)

setlist_songs = db.Table(
    'setlist_songs',
    db.Column('setlist_id', db.Integer, db.ForeignKey('setlists.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id'), primary_key=True)
)

class UserSong(db.Model):
    __tablename__ = 'user_songs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    lyrics = db.Column(db.Text, nullable=True)
    chords = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    user = db.relationship('User', back_populates='user_songs_rel')

    def __repr__(self):
        return f"<UserSong {self.id} - {self.title} by {self.artist}>"
    


class User(UserMixin, db.Model):
    """Site user."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, 
                   primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), 
                         unique=True, 
                         nullable=False)
    password_hash = db.Column(db.String(200), 
                              nullable=False)

    created_songs = db.relationship('Song', 
                            back_populates='creator', 
                            lazy=True)
    setlists = db.relationship('Setlist',
                                back_populates='user', lazy=True)
    user_songs_rel = db.relationship('UserSong', back_populates='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

    def get_id(self):
        return (self.id)
    
    def check_password(self, password):
        # Remove this method
        return self.password_hash == password
    
    @classmethod
    def register(cls, username, password):
        # hashed_password = bcrypt.generate_password_hash(password)
        return cls(username=username, password_hash=password)

    @classmethod
    def authenticate(cls, username, password):
        print(f"Authenticating user: {username}")
        user = cls.query.filter_by(username=username).first()
        if user:
            print(f"User found: {user.username}")
            # Print the stored password hash to verify format
            print(f"Stored password hash: {user.password_hash}")
            
            """ Need to complete logic for password encryption. """

            # if bcrypt.check_password_hash(user.password_hash, password):
            if user.password_hash == password:
                print("Password matches")
                return user
            else:
                print("Password does not match")
        else: 
            print("User not found")
        return None

class Setlist(db.Model):
    __tablename__ = 'setlists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', back_populates='setlists')
    songs = db.relationship('Song', secondary='setlist_songs', back_populates='setlists', lazy='dynamic')

    def __repr__(self): 
        return f"<Setlist {self.id} - {self.name}>"

class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    lyrics = db.Column(db.Text, nullable=True)
    chords = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    creator = db.relationship('User', back_populates='created_songs')
    setlists = db.relationship('Setlist', secondary='setlist_songs', back_populates='songs')
    def __repr__(self):
        return f"<Song {self.id} - {self.title} by {self.artist}>"



    
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
    text = db.Column(db.String(100), nullable=False)

# Association Table for the many-to-many relationship between chords and words

class ChordWordAssociation(db.Model):
    __tablename__ = 'chord_word_association'

    id = db.Column(db.Integer, primary_key=True)
    
    chord_id = db.Column(db.Integer, db.ForeignKey('chords.id'), nullable=False)
    
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)



def connect_db(app):
    """ connect to database."""

    db.app = app
    db.init_app(app)
    app.app_context().push()
    db.create_all()




