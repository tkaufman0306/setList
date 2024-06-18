
Musixmatch.com API:

api_url = f'http://api.musixmatch.com/ws/1.1/matcher.lyrics.get?q_artist={artist}&q_track={song_title}&apikey={API_KEY}'


With regards to DB relationships:

One user can have many songs and many setlists.
Each song can have many chords associated with it.
Each setlist can contain many songs, and each song can be present in multiple setlists.
