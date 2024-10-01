import streamlit as st
import requests
import numpy as np
import pandas as pd

def fetch_poster(movie_id):
    api_key = '21bda5edb8eb26d003da1bc9e335650c'
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US'
    r = requests.get(url)
    data = r.json()
    poster_path = data.get('poster_path')
    full_poster_path = "http://image.tmdb.org/t/p/w500/" + poster_path
    return full_poster_path


def recommend(movie, num_to_rec):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    rec_movies_name = []
    rec_movies_poster = []
    for i in distances[1:num_to_rec + 1]:
        movie_id = movies.loc[i[0], 'id']
        rec_movies_poster.append(fetch_poster(movie_id))
        rec_movies_name.append(movies.loc[i[0], 'title'])
    return rec_movies_name, rec_movies_poster

num_to_rec = 5

st.header("Movie Recommendation System")
movies = pd.read_csv('artifacts/movies.csv')
similarity = np.load('artifacts/similarities.npy')

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie to get a recommendation",
    movie_list
)

if st.button("Show recommendation"):
    rec_movies_name, rec_movies_poster = recommend(selected_movie, num_to_rec)
    cols = st.columns(num_to_rec)
    for i in range(num_to_rec):
        poster_url = rec_movies_poster[i]
        with cols[i]:
            st.markdown(
                f"[{rec_movies_name[i]}]({poster_url})"
            )