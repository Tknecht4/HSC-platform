from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Required
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import UploadSet, IMAGES

# Flask-Uploads sets
images = UploadSet('images', IMAGES)
csv = UploadSet('csvfiles', 'csv')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    my_choices = [('Southeast Saskatchewan','Southeast Saskatchewan'), ('Southwest Saskatchewan','Southwest Saskatchewan'), ('Southern Alberta','Southern Alberta'),
                    ('Manitoba', 'Manitoba'), ('Northeast Saskatchewan','Northeast Saskatchewan'), ('Northwest Saskatchewan','Northwest Saskatchewan'),
                    ('East Saskatchewan','East Saskatchewan'), ('North Central Alberta','North Central Alberta'), ('Northern Alberta','Northern Alberta'),
                    ('Glenndive','Glenndive'), ('Test Scorecards','Test Scorecards'), ('US Scorecards','US Scorecards'), ('Australia Scorecards','Australia Scorecards')]
    upl_imgs = FileField('upl_imgs', validators=[FileRequired("Please select images"), FileAllowed(images, 'Images Only Please!')])
    upl_csv = FileField('upl_csv', validators=[FileRequired("Please select config.csv"), FileAllowed(csv, 'Csv File Only!')])
    division_drop = SelectField('Division', choices = my_choices, validators = [Required()])
    retail_loc = StringField('Retail Name', validators=[DataRequired()])
    grower_name = StringField('Grower Name', validators=[DataRequired()])
    submit = SubmitField('Upload')