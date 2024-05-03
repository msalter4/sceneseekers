from flask import Blueprint, render_template, request, session, redirect, url_for
from . import db
from flask_login import login_required, current_user
from .models import Recommendation, WatchedMovie
from .functions import QuizFunctions, MovieCards, DBAdditions

#set up a blueprint for the flask application
views = Blueprint('views', __name__) 

# create a route 
@views.route('/')
@views.route('/home')
@login_required
#Changed this ****
def home():
    user_id = current_user.id
    return render_template("home.html", user=current_user)

@views.route('/profile', methods=['GET', 'POST'])
@login_required	
def profile():

    user_id = current_user.id
    # this returns a list of all recommendations
    recommendations = Recommendation.query.filter_by(user_id=user_id).all()
    # this returns a list of all watched movies
    watched_movies = WatchedMovie.query.filter_by(user_id=user_id).all()
    
    # MovieCard Function to print all of the movies
    # we will be storing the movies in a list of dictionaries
    if request.method == 'POST':
        selected_recommendations = request.form.getlist('recommendations')
        for recommendation_id in selected_recommendations:
            recommendation = Recommendation.query.get(recommendation_id)
            if recommendation:
                watched_movie = WatchedMovie(user_id=user_id, movie_id=recommendation.movie_id)
                db.session.add(watched_movie)

        db.session.commit()
        
    #Changed***
    return render_template('profile.html',recommendations=recommendations, watched_movies=watched_movies )
	
	
@views.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    return render_template('quiz.html', user=current_user)

@views.route('/quizsimilar', methods=['GET', 'POST'])
@login_required
def quiz_similar():
    #function needs alot of cleaning along with the attached methods
    user_id = current_user.id 
    thirty_recommendations = QuizFunctions.generate_similar_quiz_results(user_id)
    tempr = thirty_recommendations[:10]

    """if 'thirty_recommendations' not in session:
        session['thirty_recommendations'] = []
    if 'tempr' not in session:
        session['tempr'] = []
        
    if len(session['thirty_recommendations']) < 10:
        session['thirty_recommendations'] = QuizFunctions.generate_similar_quiz_results(user_id)
        session['tempr'] = session['thirty_recommendations'][:10]
    
    elif len(session['tempr']) < 10:
        session['tempr'] = session['thirty_recommendations'][:10]
        """

    if request.method == 'POST':
        watched_items = [int(request.form[key]) for key in request.form if key.startswith('w')]
        not_interested_items = [int(request.form[key]) for key in request.form if key.startswith('ni')]

        QuizFunctions.process_items(user_id, watched_items, 'watched', tempr, thirty_recommendations)
        QuizFunctions.process_items(user_id, not_interested_items, 'not_interested', tempr, thirty_recommendations)
        

        if not (watched_items or not_interested_items):
            for t in session['tempr']:
                new_recommendation = Recommendation(user_id=user_id, movie_id=t)
                db.session.add(new_recommendation)
            db.session.commit()
            return redirect(url_for('views.home'))
        
    displayed = MovieCards.display_information(tempr)

    return render_template('quizsimilar.html', user=current_user, displayed=displayed)
 
@views.route('/newquiz', methods=['GET', 'POST'])
@login_required
def quiz_new():
    user_id = current_user.id
    genre_list = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Family',
                  'Fantasy', 'Film-Noir', 'History', 'Horror', 'Music', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Short',
                  'Sport', 'Thriller', 'War', 'Western']

    if request.method == 'POST':
        genre_select = [request.form[key] for key in request.form if key.startswith('s')]
        actor_select = [request.form[key] for key in request.form if key.startswith('a')]
        director_select = [request.form[key] for key in request.form if key.startswith('d')]
        session['selected_genres'] = genre_select
        session['selected_actors'] = actor_select
        session['selected_directors'] = director_select
        if genre_select:
            session['run1'] = True
            return redirect(url_for('views.quiz_new'))
        if actor_select:
            session['run2'] = True
            return redirect(url_for('views.quiz_new'))
        if director_select:
            session['run3'] = True
            return redirect(url_for('views.quiz_new'))

    if 'run1' not in session:
        return render_template('newquiz.html', user=user_id, stage='genre_selection', genre_list=genre_list)

    if 'run2' not in session:
        selected_genres = session.get('selected_genres', [])
        actor_list = QuizFunctions.selection(selected_genres, 1) if selected_genres else {}
        return render_template('newquiz.html', user=user_id, stage='actor_display', actor_list=actor_list)
    if 'run3' not in session:
        selected_genres = session.get('selected_genres', [])
        director_list = QuizFunctions.selection(selected_genres, 2) if selected_genres else {}
        return render_template('newquiz.html', user=user_id, stage='director_display', director_list=director_list)
    
    return render_template('newquiz.html', user=user_id, stage='completion')

@views.route('/reset_quiz')
@login_required
def reset_quiz():
    session.pop('run1', None)
    session.pop('run2', None)
    session.pop('selected_genres', None)
    return redirect(url_for('views.quiz_new'))


