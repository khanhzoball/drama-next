from flask import Flask, jsonify, request, Response
import pandas as pd
import os
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from itertools import compress
import pytest
import json
from utils import hello, get_clean_data, create_soup, get_recommendations

load_dotenv()

app = Flask(__name__, static_folder='build/', static_url_path='/')


## load the data
df = get_clean_data()

indices = pd.Series(df.index, index=df['title']).drop_duplicates()
max_watchers = df['watchers'].max()

## prepare tf-idf
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df['synopsis'])
cosine_sim_tf_idf = linear_kernel(tfidf_matrix, tfidf_matrix)


## create soups
top_soup = df.apply(lambda x: create_soup(x, director_w=2, genres_w=4, tags_w=4, mainrole_w=5, supportrole_w=1), axis = 1)
count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(top_soup)
cosine_sim_top = cosine_similarity(count_matrix, count_matrix)

cast_soup = df.apply(lambda x: create_soup(x, director_w=1, genres_w=0, tags_w=0, mainrole_w=8, supportrole_w=3), axis = 1)
count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(cast_soup)
cosine_sim_cast = cosine_similarity(count_matrix, count_matrix)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/hello')
def hello():
    return "hello world"

# @app.route('/title/<int:idx>')
@app.route('/recommendations', methods=["POST"])
def recommendations():
    data = json.loads(request.data.decode("utf-8"))

    title = data["title"]

    top_recommendations = get_recommendations(df, soup=top_soup, title=title, tf_idf_w=.35, soup_w=.525, weighted_score_w=.05, watchers_w=.075, cosine_sim_tf_idf=cosine_sim_tf_idf, indices=indices,
                                                max_watchers=max_watchers, cosine_sim=cosine_sim_top)
    top_recommendations_cast = get_recommendations(df, soup=cast_soup, title=title, tf_idf_w=.05, soup_w=.70, weighted_score_w=.15, watchers_w=.10, cosine_sim_tf_idf=cosine_sim_tf_idf, indices=indices,
                                                max_watchers=max_watchers, cosine_sim=cosine_sim_cast)

    recommendations = {
        "top_recommendations": top_recommendations,
        "top_recommendations_cast": top_recommendations_cast,
    }

    return Response(json.dumps(recommendations), status=200, mimetype='application/json')

@app.route('/trending', methods=["GET"])
def trending():
    trending_idx = [18, 24, 645]

    trending_dramas = [[df['title'].iloc[i], df['img_url'].iloc[i], df['score'].iloc[i], df['url'].iloc[i]] for i in trending_idx]

    return Response(json.dumps({"trending_dramas": trending_dramas}), status=200, mimetype='application/json')

# Tests
@app.route("/test")
def test():
    return "Testing, Flask!"

@app.route("/test/dataframe")
def test_dataframe():
    return jsonify({"df": df.to_json(orient=None)})

if __name__ == "__main__":
    app.run(debug=True)