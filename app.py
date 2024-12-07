from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import requests
import ast

app = Flask(__name__)

# Load and preprocess the data
def load_data():
    df = pd.read_csv('tmdb_5000_movies.csv')
    df['genres'] = df['genres'].apply(lambda x: [i['name'] for i in ast.literal_eval(x)])
    return df

# Create genre string for vectorization
def create_genre_string(genres):
    return ' '.join(genres)

# Compute similarity matrix
def compute_similarity():
    df = load_data()
    df['genre_string'] = df['genres'].apply(create_genre_string)
    count = CountVectorizer()
    count_matrix = count.fit_transform(df['genre_string'])
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    return df, cosine_sim

# Get movie recommendations
def get_recommendations(title, df, cosine_sim):
    idx = df[df['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:9]  # Changed from 6 to 9 to get top 8 similar movies
    movie_indices = [i[0] for i in sim_scores]
    return df['title'].iloc[movie_indices].tolist()

# Initialize data
df, cosine_sim = compute_similarity()

# OMDb API Configuration
OMDB_API_KEY = '3cf62584'  # Replace with your OMDb API key
OMDB_BASE_URL = 'http://www.omdbapi.com/'

@app.route('/')
def home():
    movies_list = df['title'].tolist()
    return render_template('index.html', movies=movies_list)

@app.route('/get_recommendations', methods=['POST'])
def recommend():
    movie_title = request.json['movie']
    recommendations = get_recommendations(movie_title, df, cosine_sim)
    
    # Fetch movie posters
    movies_with_posters = []
    for title in recommendations:
        response = requests.get(OMDB_BASE_URL, params={
            'apikey': OMDB_API_KEY,
            't': title
        })
        
        if response.status_code == 200:
            movie_data = response.json()
            if movie_data['Response'] == 'True':
                poster_url = movie_data.get('Poster', 'N/A')
                movies_with_posters.append({
                    'title': title,
                    'poster_url': poster_url
                })
    
    return jsonify(movies_with_posters)

if __name__ == '__main__':
    app.run(debug=True)
