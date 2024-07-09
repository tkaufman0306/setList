document.getElementById('fetch-lyrics-button').addEventListener('click', function() {
    const artist = '{{ song.artist }}';
    const songTitle = '{{ song.title }}';

    fetch(`/fetch-lyrics?artist=${encodeURIComponent(artist)}&song_title=${encodeURIComponent(songTitle)}`)
        .then(response => response.json())
        .then(data => {
            if (data.lyrics) {
                document.getElementById('lyrics').textContent = data.lyrics;
            } else {
                alert('Lyrics not found for the given artist and song.');
            }
        })
        .catch(error => {
            console.error('Error fetching lyrics:', error);
            alert('Failed to fetch lyrics from the API.');
        });
});

document.getElementById('save-changes-button').addEventListener('click', function() {
    const lyrics = document.getElementById('lyrics').textContent;
    const songId = {{ song.id }});

    fetch(`/save-lyrics`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ song_id: songId, lyrics: lyrics }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Lyrics and chords saved successfully.');
        } else {
            alert('Failed to save lyrics and chords.');
        }
    })
    .catch(error => {
        console.error('Error saving lyrics and chords:', error);
        alert('Failed to save lyrics and chords.');
    });

