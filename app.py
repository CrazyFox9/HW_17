from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from schemas import movie_schema, movies_schema
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 3}

db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')


@movie_ns.route('/')
class MoviesView(Resource):

    def get(self):
        movie_with_genre_and_director = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating,
                                                         Movie.trailer,
                                                         Genre.name.label('genre'),
                                                         Director.name.label('director')).join(Genre).join(Director)
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            movie_with_genre_and_director = movie_with_genre_and_director.filter(Movie.director_id == director_id)
        if genre_id:
            movie_with_genre_and_director = movie_with_genre_and_director.filter(Movie.genre_id == genre_id)

        all_movies = movie_with_genre_and_director.all()
        return movies_schema.dump(all_movies), 200

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "Фильм создан", 201


@movie_ns.route('/<int:mid>')
class MovieView(Resource):

    def get(self, mid: int):
        movie_with_genre_and_director = db.session.query(Movie.id, Movie.title, Movie.description, Movie.rating,
                                                         Movie.trailer,
                                                         Genre.name.label('genre'),
                                                         Director.name.label('director')).join(Genre).join(
                                                         Director).filter(
                                                         Movie.id == mid)
        movie = movie_with_genre_and_director.first()
        if not movie:
            return "Такого фильма нет", 404
        return movie_schema.dump(movie), 200

    def patch(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        req_json = request.json
        if not movie:
            return "Такого фильма нет", 404
        if "title" in req_json:
            movie.title = req_json['title']
        elif "description" in req_json:
            movie.description = req_json['description']
        elif "trailer" in req_json:
            movie.trailer = req_json['trailer']
        elif "year" in req_json:
            movie.year = req_json['year']
        elif "rating" in req_json:
            movie.rating = req_json['rating']
        elif "genre_id" in req_json:
            movie.genre_id = req_json['genre_id']
        elif "director_id" in req_json:
            movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        db.session.close()
        return "Фильм обновлен", 200

    def put(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return "Такого фильма нет", 404
        req_json = request.json
        movie.title = req_json['title']
        movie.description = req_json['description']
        movie.trailer = req_json['trailer']
        movie.year = req_json['year']
        movie.rating = req_json['rating']
        movie.genre_id = req_json['genre_id']
        movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        db.session.close()
        return "Фильм обновлен", 200

    def delete(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return "Такого фильма нет", 404
        db.session.delete(movie)
        db.session.commit()
        db.session.close()
        return "Фильм удален", 204


if __name__ == '__main__':
    app.run(debug=True)
