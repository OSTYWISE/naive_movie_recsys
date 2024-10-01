import pandas as pd
import numpy as np
import json
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df_movie = pd.read_csv("tmdb_5000_movies_data/movies.csv")
df_credit = pd.read_csv("tmdb_5000_movies_data/credits.csv")

movies = (df_movie
      .merge(df_credit.drop(columns=['title']), left_on='id', right_on='movie_id')
      .drop(columns=['movie_id']))

df = movies[['id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

df['title'] = df['title'].fillna('unknown')
df['overview'] = df['overview'].fillna('')

df['genres'] = df['genres'].apply(lambda list_str: [item['name'] for item in json.loads(list_str)])
df['keywords'] = df['keywords'].apply(lambda list_str: [item['name'] for item in json.loads(list_str)])

def cast_preprocess(cast_str):
    names_list = []
    cast_dict = json.loads(cast_str)
    for i in range(min(len(cast_dict), 3)):
        names_list.append(cast_dict[i]['name'])
    return names_list
        
df['cast'] = df['cast'].apply(cast_preprocess)

def fetch_director(text):
    l = []
    for item in json.loads(text):
        if item['job'] == 'Director':
            l.append(item['name'])
            break
    return l

df['crew'] = df['crew'].apply(fetch_director)
df['overview'] = df['overview'].apply(lambda x: x.replace(',', '').split())

def remove_space(list_of_phrases):
    l = []
    for phrase in list_of_phrases:
        l.append(phrase.replace(" ", ""))
    return l

df['cast'] = df['cast'].apply(remove_space)
df['genres'] = df['genres'].apply(remove_space)
df['keywords'] = df['keywords'].apply(remove_space)
df['crew'] = df['crew'].apply(remove_space)

df['tags'] = df['overview'] + df['genres'] + df['keywords'] + df['cast'] + df['crew']

new_df = df[['id', 'title', 'tags']]
new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x).lower())

ps = PorterStemmer()
def stems(text):
    l = []
    for i in text.split():
        l.append(ps.stem(i))
    return " ".join(l)

new_df['tags'] = new_df['tags'].apply(stems)

cv = CountVectorizer(max_features=5000, stop_words='english')
vector = cv.fit_transform(new_df['tags']).toarray()
similarity = cosine_similarity(vector)

def recommend(movie):
    index = new_df[new_df['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    for i in distances[1:6]:
        print(new_df.loc[i[0], 'title'])

new_df.to_csv('artifacts/movies.csv')
np.save('artifacts/similarities.npy', similarity)

print("Files save successfully!")






