"""forms.py file for setList app"""


from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length


class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

class SetListForm(FlaskForm):
    """Form for adding playlists."""

    name = StringField("Setlist Name", validators=[InputRequired(), Length(min=1, max=100)])
    submit = SubmitField('Create Setlist')
    # description = StringField("Description", validators=[InputRequired(), Length(min=1, max=200)])  

class SongForm(FlaskForm):
    """Form for adding songs."""
    title = StringField("Title", validators=[InputRequired(), Length(min=1, max=100)])
    artist = StringField("Artist", validators=[InputRequired(), Length(min=1, max=100)])

class NewSongForSetListForm(FlaskForm):
    """Form for adding a song to playlist."""

    song = SelectField('Song To Add', coerce=int, validators=[InputRequired()])

class AddSongForm(FlaskForm):
    existing_song = SelectField('Select an existing song', coerce=int)
    new_song_title = StringField('Or add a new song title', validators=[Length(max=100)])
    new_song_artist = StringField('Add artist name', validators=[Length(max=100)])
    submit = SubmitField('Add Song')