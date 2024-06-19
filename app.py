import requests

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Tweet
from forms import UserForm, TweetForm
from sqlalchemy.exc import IntegrityError

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///setlist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Musixmatch API key:
API_KEY = '5246d25b2a2d0134a4a519068cf1e3aa'

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

if __name__ == '__main__':
    app.run(debug=True)


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

if __name__ == '__main__':
    app.run(debug=True)

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
        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another')
            return render_template('register.html', form=form)
        session['user_id'] = new_user.id
        flash('Welcome! Successfully Created Your Account!', "success")
        return redirect('/songs')