from dataclasses import asdict
import datetime
import uuid
import functools
from flask import Blueprint, current_app, render_template, session, request, redirect, url_for, flash
from movie_library.forms import MovieForm, ExtendedMovieForm, RegisterForm, LoginForm
from movie_library.models import Movie, User
from passlib.hash import pbkdf2_sha256

pages = Blueprint(
    "pages", __name__, template_folder="templates", static_folder="static"
)


#login decorator, checks if there is an email present in the session, if not redirects to login page
def login_required(route):
    @functools.wraps(route)
    def route_wrapper(*args, **kwargs):
        if session.get("email") is None:
            return redirect(url_for(".login"))
    
        return route(*args, **kwargs)
    return route_wrapper

#def get_movie_collection():
#    with current_app.app_context():
#        moviedb = current_app.db.movie
####################################### 
#can only access current_app in application context, would have to do this then call moviedb = get_movie_collection() in each route
#would be worthwhile if i had more routes

@pages.route("/")
@login_required
def index():
    #find({}) grabs all
    #find_one(...) returns a SINGLE object not a CURSOR which is what find(..) returns
    user_data = current_app.db.user.find_one({"email": session["email"]})
    user = User(**user_data)
    
    #finding _id that is "$in" user's movie list (user.movies) (created above in the user object when we get session email)
    movie_data = current_app.db.movie.find({"_id": {"$in": user.movies}}) 
    movies = [Movie(**data) for data in movie_data]

    return render_template(
        "index.html",
        title="Movies Watchlist",
        movie_data = movies
    )


@pages.route("/register", methods=["GET", "POST"])
def register():
    if session.get("email"):
        return redirect(url_for(".index"))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            _id = uuid.uuid4().hex,
            email = form.email.data,
            password = pbkdf2_sha256.hash(form.password.data)
        )

        current_app.db.user.insert_one(asdict(user))
        flash("Successfully Registered!", "success")

        return redirect(url_for(".login"))

    return render_template("register.html", title= "Movies Watchlist - Register", form=form)


@pages.route("/login", methods=["GET", "POST"])
def login(): 
    if session.get("email"):
        return redirect(url_for(".index"))
    
    form = LoginForm()
    if form.validate_on_submit():
        user_data = current_app.db.user.find_one({"email": form.email.data})
        if not user_data:
            #if this flashes, means that user has not registered or email incorrect 
            flash("Incorrect login information", category="danger")
            return redirect(url_for(".login"))
        
        user = User(**user_data)

        #hash login form password (arg1) and compare to user password in db (arg2)
        if user and pbkdf2_sha256.verify(form.password.data, user.password):
            session["user_id"] = user._id
            session["email"] = user.email

            return redirect(url_for(".index"))
        
        #if this flashes, means that password was incorrect (email exists) 
        flash("Incorrect login information", category="danger")

    return render_template("login.html", title="Movie Watchlist - Login", form = form)


@pages.route("/logout")
def logout():
    theme = session.get("theme")
    session.clear()
    session["theme"] = theme

    return redirect(url_for(".login"))



@pages.route("/add", methods = ["GET", "POST"])
@login_required
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
        
        #ADD TO USER'S MOVIE LIST
        current_app.db.user.update_one(
            {"_id": session["user_id"]}, {"$push": {"movies": movie._id}}
        )
        #checking if movie was added
        if current_app.db.movie.find_one(asdict(movie)):
            print(f"movie now exists in db: '{current_app.db.movie}'")

        return redirect(url_for('.index'))

    return render_template("new_movie.html", title="Movies Watchlist - Add Movie", form=form)

#Flask routing, the angle brackets < > are used to indicate variable parts of the URL
@pages.get("/movie/<string:_id>")
def movie(_id: str):
    #can add 404 check (if not ... : abort(404))
    movie = Movie(**current_app.db.movie.find_one({"_id": _id}))
    return render_template("movie_details.html", movie=movie)


@pages.get("/movie/<string:_id>/rate")
@login_required
def rate_movie(_id):
    rating = int(request.args.get('rating'))
    current_app.db.movie.update_one({"_id": _id}, {"$set": {"rating":rating}})
    
    return redirect(url_for(".movie", _id=_id))


@pages.get("/movie/<string:_id>/watch")
@login_required
def watch_today(_id):
    current_app.db.movie.update_one({"_id": _id}, {"$set": {"last_watched":datetime.datetime.today()}})

    return redirect(url_for(".movie", _id=_id))


                    #no emptyspace
@pages.route("/edit/<string:_id>", methods= ["GET", "POST"])
@login_required
def edit_movie(_id: str):
    movie = Movie(**current_app.db.movie.find_one({"_id": _id}))
    form = ExtendedMovieForm(obj=movie)
    if form.validate_on_submit():
        movie.cast = form.cast.data
        movie.series = form.series.data
        movie.tags = form.tags.data
        movie.description = form.description.data
        movie.video_link = form.video_link.data

        #convert all the modified and original movie data into a dict and update the entry with matching _id
        current_app.db.movie.update_one({"_id": movie._id}, {"$set": asdict(movie)})
        return redirect(url_for(".movie", _id=movie._id))
    
    return render_template("movie_form.html", movie=movie, form=form)




@pages.get("/toggle-theme")
def toggle_theme():
    theme = session.get('theme')
    if theme == "dark":
        session["theme"] = "light"
    else:
        session["theme"] = "dark"
    
    return redirect(request.args.get('current_page'))