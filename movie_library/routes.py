from dataclasses import asdict
import uuid
from flask import Blueprint, current_app, render_template, session, request, redirect, url_for
from movie_library.forms import MovieForm
from movie_library.models import Movie

pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)

#def get_movie_collection():
#    with current_app.app_context():
#        moviedb = current_app.db.movie
####################################### 
#can only access current_app in application context, would have to do this then call moviedb = get_movie_collection() in each route
#would be worthwhile if i had more routes

@pages.route("/")
def index():
    movie_data = current_app.db.movie.find({}) #find({}) finds all dictionaries (entries) in the db
    movies = [Movie(**data) for data in movie_data]

    return render_template(
        "index.html",
        title="Movies Watchlist",
        movie_data = movies
    )

@pages.route("/add", methods = ["GET", "POST"])
def add_movie():
    #in Flask-WTF, when you create an instance of a form class, you typically do not need to pass any arguments to it directly
    form = MovieForm()

    #using validate_on_submit() if there are errors (ie missing fields) it will update form and be sent to be rendered
    if form.validate_on_submit():
        movie = Movie(_id = uuid.uuid4().hex,
            title= form.title.data,
            director= form.director.data,
            year= form.year.data
        )

        #create 'movie' collection in the database.
        #MAKE SURE TO CONVERT movie obj to dictionary to be BSON compatible
        current_app.db.movie.insert_one(asdict(movie))

        #checking if movie was added
        if current_app.db.movie.find_one(asdict(movie)):
            print(f"movie now exists in db: '{current_app.db.movie}'")

        return redirect(url_for('.index'))

    return render_template("new_movie.html", title="Movies Watchlist - Add Movie", form=form)


@pages.get("/toggle-theme")
def toggle_theme():
    theme = session.get('theme')
    if theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"
    
    return redirect(request.args.get('current_page'))