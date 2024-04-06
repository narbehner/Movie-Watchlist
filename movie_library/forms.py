from typing import Any, Sequence
from flask_wtf import FlaskForm
from wtforms import IntegerField, PasswordField, StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo
import datetime

current_year = datetime.datetime.now().year
#FlaskForm to protect from CSRF 
class MovieForm(FlaskForm):
    #can call each as MovieFormobjname.<field> i.e. form = MovieForm() ---> form.title, form.director etc
    title = StringField("Title", validators=[InputRequired()])
    director = StringField("Director", validators=[InputRequired()])

    #validators are run in the order in which they appear
    year = IntegerField("Year", validators=[
                                    InputRequired(), 
                                    NumberRange(min=1878, max=current_year, 
                                        message="Please enter a valid year in form YYYY")])

    submit = SubmitField("Add Movie")

#In Python, when a class is defined with parentheses after its name, as in class StringListField(TextAreaField):
    #it indicates that the new class (StringListField) inherits from the class specified within the parentheses.
#This means that StringListField will inherit all the attributes and methods of TextAreaField, 
    #and you can also add additional attributes and methods specific to StringListField.
class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""

    #valuelist[0] is the contents of the text area
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = [line.strip() for line in valuelist[0].split("\n")]
        else:
            self.data = []


class ExtendedMovieForm(MovieForm):
    cast = StringField("Cast")
    series = StringField("Series")
    tags = StringField("Tags")
    description = TextAreaField("Description")
    video_link = URLField("video link")

    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password= PasswordField("Password", validators=[InputRequired(), Length(min=4, message="Your password must be at least 4 chars long")])

    confirm_password = PasswordField("Confirm password", validators=[InputRequired(), EqualTo("password", message="Passwords must match")])

    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")