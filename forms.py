from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask.ext.uploads import UploadSet, IMAGES

# Flask-Uploads sets
images = UploadSet('images', IMAGES)
csv = UploadSet('csvfiles', 'csv')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    upl_imgs = FileField('upl_imgs', validators=[FileRequired("Please select images"), FileAllowed(images, 'Images Only Please!')])
    upl_csv = FileField('upl_csv', validators=[FileRequired("Please select config.csv"), FileAllowed(csv, 'Csv File Only!')])
    submit = SubmitField('Upload')