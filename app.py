"""app.py file for setList application"""


from flask import Flask, render_template, redirect, session, flash, request, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, Setlist, Song, User, UserSong, Chord, Word  
from forms import UserForm, SetListForm, AddSongForm, CreateSongForm, LoginForm, UserSongForm
from sqlalchemy.exc import IntegrityError
# from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import requests
from flask_migrate import Migrate
app = Flask(__name__)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # Query User model to retrieve the user by ID
    return User.query.get(int(user_id))

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///setlist-app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"
app.config['SESSION_COOKIE_NAME'] = "setlist_session"
app.config['SESSION_COOKIE_HTTPONLY'] = True

connect_db(app)

bcrypt = Bcrypt(app)
toolbar = DebugToolbarExtension(app)

@app.before_request
def create_tables():
    # db.drop_all()
    db.create_all()
    app.tables_created = True
# db = SQLAlchemy(app)


@app.route('/reset-db')
def reset_db():
    # db.drop_all()
    db.create_all()
    return "Database reset!"

"""Musixmatch API key:"""
API_KEY = '5246d25b2a2d0134a4a519068cf1e3aa'


@app.route('/')
def homepage():
    if 'user_id' in session:
        return redirect(url_for('view_setlists'))
    form = LoginForm()
    if form.validate_on_submit():
        print("Form validated successfully")
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('view_setlists'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.register(username, password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('setlists'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
       
        if user:
            print(f"User found: {user.username}")
            if user.password_hash == password:  # Direct comparison for simplicity
                login_user(user)
                session['user_id'] = user.id
                print("User logged in successfully")
                flash('Logged in successfully!', 'success')
                return redirect(url_for('view_setlists'))
            else:
                print("Invalid password")
                flash('Invalid username or password.')
        else:
            print("User not found")
            flash('User not found.', 'danger')
    else:
        print("Form not validated")

    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if current_user.is_authenticated:
        logout_user()
        session.pop('user_id', None)
        flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

#  Route to view user setlists

@app.route('/setlists', methods=['GET', 'POST'])
@login_required
def view_setlists():
    setlists = Setlist.query.filter_by(user_id=current_user.id).all()

    form = SetListForm()
    
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('homepage'))
    
    user_id = session['user_id']
    setlists = Setlist.query.filter_by(user_id=user_id).all()
    
    return render_template('setlists.html', setlists=setlists, form=form)



@app.route('/create_setlist', methods=['GET', 'POST'])
# @login_required
def create_setlist():
    if 'user_id' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))
    
    form = SetListForm()
    
    if form.validate_on_submit():
        try:
            setlist_name = form.name.data
            user_id = session['user_id']
            
            user = User.query.get(user_id)
            if not user:
                flash('User does not exist.', 'error')
                return redirect(url_for('login'))  # Redirect to login or handle appropriately
            
            # Create new setlist
            new_setlist = Setlist(name=setlist_name, user_id=user_id)
            db.session.add(new_setlist)
            db.session.commit()
            
            flash('Setlist created successfully!', 'success')
            return redirect(url_for('view_setlists'))
        
        except Exception as e:
            print(f"Error creating setlist: {e}")
            db.session.rollback()
            flash('An error occurred. Please try again.', 'error')
    
    return render_template('create_setlist.html', form=form)
  

# Route to view a specific setlist
@app.route('/setlist/<int:setlist_id>', methods=['GET', 'POST'])
@login_required
def view_setlist(setlist_id):
    setlist = Setlist.query.get_or_404(setlist_id)
    add_song_form = AddSongForm()
    create_song_form = CreateSongForm()

    if add_song_form.validate_on_submit():
        song_id = add_song_form.existing_song.data
        song = Song.query.get(song_id)

        if song:
            print(f"Song found: {song.id}")
            setlist.songs.append(song)
            db.session.commit()
            flash("Song added to setlist!", "success")
        else:
            flash("Song not found.", "error")
        return redirect(url_for('view_setlist', setlist_id=setlist.id))
    
    if create_song_form.validate_on_submit():
        new_song = Song(
            title=create_song_form.title.data,
            artist=create_song_form.artist.data,
            Key=create_song_form.key.data,
            user_id=current_user.id
        )
        
        db.session.add(new_song)
        db.session.commit()
        flash("New song created and added to setlist!", "success")
        setlist.songs.append(new_song)
        db.session.commit()
        return redirect(url_for('view_setlist', setlist_id=setlist.id))

    add_song_form.existing_song.choices = [(s.id, f'{s.title} by {s.artist}') for s in Song.query.all()]

    return render_template('setlist.html', setlist=setlist, add_song_form=add_song_form, create_song_form=create_song_form)


        # except Exception as e:
        #     db.session.rollback()
        #     print(f"Error adding song to setlist: {e}")
        #     flash('An error occured, Please try again.', 'error')

# Populate the dropdown with existing songs
    # add_song_form.existing_song.choices = [(song.id, f"{song.title} by {song.artist}") for song in Song.query.all()]



@app.route('/user/songs', methods=['GET', 'POST'])
# @login_required
def user_songs():
    form = UserSongForm()
    
    if form.validate_on_submit():
        title = form.title.data
        artist = form.artist.data
        # Optionally, fetch lyrics here from an API
        lyrics = fetch_lyrics(title, artist)  # Implement fetch_lyrics function
        chords = form.chords.data
        current_user = session['user_id']
        
        new_song = UserSong(title=title, artist=artist, lyrics=lyrics, chords=chords, user_id=current_user.id)
        db.session.add(new_song)
        db.session.commit()
        
        return redirect(url_for('user_songs'))
    
    user_songs = UserSong.query.filter_by(user_id=current_user.id).all()
    return render_template('user_songs.html', form=form, user_songs=user_songs)


@app.route('/song/<int:song_id>')
# @login_required
def view_song(song_id):
    song = Song.query.get_or_404(song_id)
    return render_template('song.html', song=song)

@app.route('/save-lyrics', methods=['POST'])
# @login_required
def save_lyrics():
    data = request.get_json()
    song_id = data.get('song_id')
    lyrics = data.get('lyrics')

    song = Song.query.get_or_404(song_id)
    song.lyrics = lyrics

    db.session.commit()

    return jsonify({'success': True}), 200

# @app.route('/setlist/<int:setlist_id>/add-song', methods=['POST'])
# # @login_required
# def add_song_to_setlist(setlist_id):
#     data = request.get_json()
#     song_title = data.get('title')
#     song_artist = data.get('artist')

#     if not song_title or not song_artist:
#         return jsonify({'success': False, 'error': 'Missing title or artist'}), 400

#     new_song = Song(title=song_title, artist=song_artist, user_id=current_user.id)

#     setlist = Setlist.query.get(setlist_id)
#     if not setlist:
#         return jsonify({'success': False, 'error': 'Setlist not found'}), 404

#     setlist.songs.append(new_song)
#     db.session.add(new_song)
#     db.session.commit()

#     return jsonify({'success': True, 'song_id': new_song.id})


# Route to remove a song from a setlist
@app.route('/setlist/<int:setlist_id>/remove-song', methods=['POST'])
def remove_song_from_setlist(setlist_id):
    data = request.get_json()
    song_id = data.get('song_id')

    setlist = Setlist.query.get_or_404(setlist_id)
    song = Song.query.get_or_404(song_id)

    if song in setlist.songs:
        setlist.songs.remove(song)
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'error': 'Song not found in setlist'}), 404
    

@app.route('/fetch-lyrics', methods=['GET'])
def fetch_lyrics():
    artist = request.args.get('artist')
    song_title = request.args.get('song_title')
    
    if not artist or not song_title:
        return jsonify({'error': 'Missing artist or song_title parameter'}), 400
    
    # Replace 'API_KEY' with your actual Musixmatch API key
    api_url = f'http://api.musixmatch.com/ws/1.1/matcher.lyrics.get?q_artist={artist}&q_track={song_title}&apikey={API_KEY}'
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if 'message' in data and 'body' in data['message'] and 'lyrics' in data['message']['body']:
            lyrics = data['message']['body']['lyrics']['lyrics_body']
            return jsonify({'lyrics': lyrics}), 200
        else:
            return jsonify({'error': 'Lyrics not found for the given artist and song'}), 404
    else:
        return jsonify({'error': 'Failed to fetch lyrics from the API'}), 500


# if __name__ == '__main__':
#     app.run(debug=True)


@app.route('/add-chord', methods=['POST'])
def add_chord():
    chord = request.form['chord']
    word_index = int(request.form['word_index'])
    song_id = int(request.form['song_id'])

    # Retrieve the song from the database
    song = song.query.get(song_id)

    if not song:
        return jsonify({'error': 'Song not found'}), 404

    # Split the lyrics into words
    words = song.lyrics.split()

    if word_index < 0 or word_index >= len(words):
        return jsonify({'error': 'Invalid word index'}), 400

    # Add the chord above the specified word
    words[word_index] = f"[{chord}] {words[word_index]}"

    # Join the words back into lyrics
    updated_lyrics = ' '.join(words)
    song.lyrics = updated_lyrics

    db.session.commit()

    return redirect(url_for('view_song', song_id=song_id))




    
    # form = UserForm()
    # if form.validate_on_submit():
    #     username = form.username.data
    #     password = form.password.data
    #     new_user = User.register(username=username, password=password)

    #     try:
    #         db.session.add(new_user)
    #         db.session.commit()
    #         session['user_id'] = new_user.id
    #         flash('Welcome! Successfully Created Your Account! Congrats', "success")
    #         return redirect(url_for('view_setlists'))
        
    #     except IntegrityError as e:
    #         db.session.rollback()
    #         print(f"IntegrityError: {e}")
    #         form.username.errors.append('Username taken.  Please pick another')

    #     except Exception as e:
    #         db.session.rollback()
    #         print(f"Exception: {e}")
    #         form.username.errors.append('An error occurred. Please try again.')
    
    # return render_template('signup.html', form=form)
    





if __name__ == '__main__':
     app.run(debug=True)