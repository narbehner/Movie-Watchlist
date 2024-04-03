from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField
from wtforms.validators import InputRequired, NumberRange
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