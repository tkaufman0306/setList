"""app.py file for setList application"""


import requests

from flask import Flask, render_template, redirect, session, flash, request, url_for, jsonify

from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, Setlist, Song, SetlistSong, User, Chord, Word  

from forms import UserForm, SetListForm, SongForm, NewSongForSetListForm, AddSongForm, LoginForm

from sqlalchemy.exc import IntegrityError

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///setlist-app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

connect_db(app)
db.create_all()

db = SQLAlchemy(app)

# Musixmatch API key:
API_KEY = '5246d25b2a2d0134a4a519068cf1e3aa'


@app.route('/')
def homepage():
    if 'user_id' in session:
        return redirect(url_for('view_setlists'))
    form = LoginForm()
    return render_template('home_anon.html', form=form)

@app.route('/view-setlists')
def view_setlists():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('homepage'))
    
    user_id = session['user_id']
    setlists = Setlist.query.filter_by(user_id=user_id).all()
    return render_template('setlists.html', setlists=setlists)

@app.route('/setlist/<int:setlist_id>')
def view_setlist(setlist_id):
    setlist = Setlist.query.get_or_404(setlist_id)
    form = AddSongForm()
    
    # Populate the dropdown with existing songs
    form.existing_song.choices = [(song.id, f"{song.title} by {song.artist}") for song in Song.query.all()]

    if form.validate_on_submit():
        if form.existing_song.data:
            song_id = form.existing_song.data
            song = Song.query.get(song_id)
        else:
            song_title = form.new_song_title.data
            song_artist = form.new_song_artist.data
            song = Song(title=song_title, artist=song_artist, user_id=session['user_id'])
            db.session.add(song)
            db.session.commit

        setlist.songs.append(song)
        db.session.commit()
        flash("Song added to setlist!", "success")
        return redirect(url_for('view_setlist', setlist_id=setlist_id))
    
    return render_template('setlist.html', setlist=setlist, form=form)


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
    
    # Make request to Lyrics.ovh API
    api_url = f'http://api.musixmatch.com/ws/1.1/matcher.lyrics.get?q_artist={artist}&q_track={song_title}&apikey={API_KEY}'
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        if 'message' in data and 'body' in data['message'] and 'lyrics' in  data['message']['body']:
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



@app.route('/register', methods=['GET', 'POST'])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        new_user = User.register(username, password)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('signup.html', form=form)
        
        session['user_id'] = new_user.id
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect('/setlists')
    
    return render_template('signup.html', form=form)
    

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = UserForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            session['user_id'] = user.id
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for('view_setlists'))
        form.username.errors = ['Invalid username or password.']

    return render_template('home-anon.html', form=form)


@app.route('/logout')
def logout():
    session.pop('user_id')
    flash("You have successfully logged out.", "success")
    return redirect(url_for('homepage'))



if __name__ == '__main__':
     app.run(debug=True)