"""forms.py file for setList app"""


from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, Length, DataRequired, Optional


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


class AddSongForm(FlaskForm):
    existing_song = SelectField('Select an existing song', coerce=int, choices=[])
    new_song_title = StringField('Or add a new song title', validators=[Length(max=100), Optional()])
    new_song_artist = StringField('Add artist name', validators=[Length(max=100), Optional()])
    submit = SubmitField('Add Song')

class CreateSongForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    artist = StringField('Artist', validators=[DataRequired(), Length(max=100)])
    chords = StringField('Key (Optional)', validators=[Optional()])
    submit = SubmitField('Create Song')

class UserSongForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    artist = StringField('Artist', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Create Song')
    chords = TextAreaField('Chords', validators=[Length(max=1000)])  
    
    
# Optional: Add validators as needed
# class SongForm(FlaskForm):
#     """Form for adding songs."""
#     title = StringField("Title", validators=[InputRequired(), Length(min=1, max=100)])
#     artist = StringField("Artist", validators=[InputRequired(), Length(min=1, max=100)])

# class NewSongForSetListForm(FlaskForm):
#     """Form for adding a song to playlist."""

#     existing_song = SelectField('Select an existing song', coerce=int)
#     new_song_title = StringField('Or add a new song title', validators=[Length(max=100)])
#     new_song_artist = StringField('Add artist name', validators=[Length(max=100)])
#     submit = SubmitField('Add Song')