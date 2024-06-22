"""models.py file for setList app"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from bcrypt import hashpw, checkpw, gensalt

db = SQLAlchemy()
bcrypt = Bcrypt()


# from app import db



setlist_songs = db.Table(
    'setlist_songs',
    db.Column('setlist_id', db.Integer, db.ForeignKey('setlists.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id'), primary_key=True)
)

class Setlist(db.Model):
    __tablename__ = 'setlists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    songs = db.relationship('Song', secondary=setlist_songs, backref=db.backref('setlists', lazy=True))


class Song(db.Model):
    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), nullable=False)
    lyrics = db.Column(db.Text, nullable=False)
    api_source = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    chords = db.relationship('Chord', backref='songs', lazy=True)


# class SetlistSong(db.Model):

#     __tablename__ = 'setlist_songs'
#     __table_args__ = {'extend_existing': True}

#     id = db.Column(db.Integer, primary_key=True)
    
#     setlist_id = db.Column(db.Integer, db.ForeignKey('setlists.id'), primary_key=True, nullable=False)
    
#     song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), primary_key=True, nullable=False)

#     # Define relationships
#     setlist = db.relationship('Setlist', backref='setlist_song_associations', overlaps="setlists,songs")
#     song = db.relationship('Song', backref='setlist_song_associations', overlaps="setlists,songs")

#     def __repr__(self):
#         return f'<SetlistSong id={self.id} setlist_id={self.setlist_id} song_id={self.song_id}>'

class User(db.Model):
    """Site user."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, 
                   primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), 
                         unique=True, 
                         nullable=False)
    password_hash = db.Column(db.String(200), 
                              nullable=False)
    songs = db.relationship('Song', 
                            backref='user', 
                            lazy=True)
    setlists = db.relationship('Setlist',
                                backref='user', lazy=True)
    
    def set_password(self, password):
        """Set password with bcrypt"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Check password with bcrypt"""
        return bcrypt.check_password_hash(self.password_hash, password)
    
    @classmethod
    def register(cls, username, password):
        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        return cls(username=username, password_hash=hashed_password)

    @classmethod
    def authenticate(cls, username, password):
        print(f"Authenticating user: {username}")
        user = cls.query.filter_by(username=username).first()
        if user:
            print(f"User found: {user.username}")
            # Print the stored password hash to verify format
            print(f"Stored password hash: {user.password_hash}")
            
            if bcrypt.check_password_hash(user.password_hash, password):
                print("Password matches")
                return user
            else:
                print("Password does not match")
        else: 
            print("User not found")
        return None

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




