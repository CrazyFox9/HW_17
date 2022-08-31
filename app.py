from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from schemas import *
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_AS_ASCII'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 3}

db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


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


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        all_directors = db.session.query(Director).all()
        return directors_schema.dump(all_directors), 200

    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "Режиссер создан", 201


@director_ns.route('/<int:did>')
class DirectorView(Resource):
    def get(self, did: int):
        director = db.session.query(Director).get(did)
        if not director:
            return "Такого режиссера нет", 404
        return director_schema.dump(director), 200

    def put(self, did: int):
        director = db.session.query(Director).get(did)
        if not director:
            return "Такого режиссера нет", 404
        req_json = request.json
        director.name = req_json['name']
        db.session.add(director)
        db.session.commit()
        db.session.close()
        return "Режиссер обновлен", 200

    def delete(self, did: int):
        director = db.session.query(Director).get(did)
        if not director:
            return "Такого режиссера нет", 404
        db.session.delete(director)
        db.session.commit()
        db.session.close()
        return "Режиссер удален", 204


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        all_genres = db.session.query(Genre).all()
        return genres_schema.dump(all_genres), 200

    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return "Жанр создан", 201


@genre_ns.route('/<int:gid>')
class GenreView(Resource):
    def get(self, gid: int):
        genre = db.session.query(Director).get(gid)
        if not genre:
            return "Такого жанра нет", 404
        return genre_schema.dump(genre), 200

    def put(self, gid: int):
        genre = db.session.query(Genre).get(gid)
        if not genre:
            return "Такого жанра нет", 404
        req_json = request.json
        genre.name = req_json['name']
        db.session.add(genre)
        db.session.commit()
        db.session.close()
        return "Жанр обновлен", 200

    def delete(self, gid: int):
        genre = db.session.query(Genre).get(gid)
        if not genre:
            return "Такого жанра нет", 404
        db.session.delete(genre)
        db.session.commit()
        db.session.close()
        return "Жанр удален", 204


if __name__ == '__main__':
    app.run(debug=True)
