"""
FastAPI application for movies.json
Run with: uvicorn movies_api:app --reload
Swagger UI: http://127.0.0.1:8000/docs
"""

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Movies API",
    description="A simple API to manage a collection of movies stored in movies.json",
)

DATA_FILE = Path("movies.json")


# ---------- Pydantic model for validating a new movie ----------
class Movie(BaseModel):
    title: str = Field(..., example="The Matrix")
    director: str = Field(..., example="Lana Wachowski")
    rating: float = Field(..., ge=0, le=10, example=8.7, description="Rating must be between 0 and 10")
    duration_minutes: int = Field(..., gt=0, example=136, description="Duration must be a positive integer")


# ---------- Helper functions to read/write the JSON file ----------
def read_movies():
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def write_movies(movies):
    with open(DATA_FILE, "w") as f:
        json.dump(movies, f, indent=4)


# ---------- (A) GET all movies ----------
@app.get("/movies", description="Returns the full list of movies stored in movies.json")
def get_movies():
    return read_movies()


# ---------- (A) DELETE a movie by id ----------
@app.delete(
    "/movies/{movie_id}",
    description="Deletes the movie with the given id. Example: DELETE /movies/3",
)
def delete_movie(movie_id: int):
    movies = read_movies()
    updated_movies = [m for m in movies if m["id"] != movie_id]

    if len(updated_movies) == len(movies):
        raise HTTPException(status_code=404, detail=f"Movie with id {movie_id} not found")

    write_movies(updated_movies)
    return {"message": f"Movie with id {movie_id} deleted successfully"}


# ---------- (B) GET movies sorted by popularity_score (ascending) ----------
@app.get("/movies/sorted", description="Returns movies sorted by popularity_score in ascending order")
def get_movies_sorted_by_popularity():
    movies = read_movies()

    for movie in movies:
        movie["popularity_score"] = movie["rating"] * 10

    sorted_movies = sorted(movies, key=lambda m: m["popularity_score"])
    return sorted_movies


# ---------- (C) POST a new movie ----------
@app.post("/movies", description="Adds a new movie after validating it with Pydantic")
def add_movie(movie: Movie):
    movies = read_movies()

    # Raise 409 if the movie already exists (same title)
    if any(m["title"].lower() == movie.title.lower() for m in movies):
        raise HTTPException(status_code=409, detail="This movie already exists")

    new_id = max((m["id"] for m in movies), default=0) + 1
    new_movie = {"id": new_id, **movie.dict()}
    movies.append(new_movie)
    write_movies(movies)

    print(f"Movie '{movie.title}' added successfully")
    return {"message": f"Movie '{movie.title}' added successfully", "movie": new_movie}
