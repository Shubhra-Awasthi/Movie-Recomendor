from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests

app = Flask(__name__)

# Load and preprocess the data
def load_data():
    df = pd.read_csv('Cleaned_Movies.csv')
    return df

# Compute similarity matrix using tags
def compute_similarity():
    df = load_data()
    # Create count matrix from tags
    count = CountVectorizer(stop_words='english')
    count_matrix = count.fit_transform(df['tags'])
    
    # Compute cosine similarity
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    return df, cosine_sim

# Get movie recommendations
def get_recommendations(title, df, cosine_sim):
    # Get the index of the movie
    idx = df[df['title'] == title].index[0]
    
    # Get similarity scores for all movies
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort movies based on similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get top 8 similar movies (excluding the movie itself)
    sim_scores = sim_scores[1:9]
    
    # Get movie indices and titles
    movie_indices = [i[0] for i in sim_scores]
    recommended_movies = df.iloc[movie_indices][['title', 'movie_id']].to_dict('records')
    return recommended_movies

# Initialize data
df, cosine_sim = compute_similarity()

# OMDb API Configuration
OMDB_API_KEY = '3cf62584'
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
    for movie in recommendations:
        response = requests.get(OMDB_BASE_URL, params={
            'apikey': OMDB_API_KEY,
            't': movie['title']
        })
        
        if response.status_code == 200:
            movie_data = response.json()
            if movie_data['Response'] == 'True':
                poster_url = movie_data.get('Poster', 'N/A')
                movies_with_posters.append({
                    'title': movie['title'],
                    'poster_url': poster_url,
                    'movie_id': movie['movie_id']
                })
    
    return jsonify(movies_with_posters)

if __name__ == '__main__':
    app.run(debug=True)
