from flask import Flask, jsonify, request, Response
import pandas as pd
import os
from dotenv import load_dotenv
import re
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from itertools import compress
import pytest
import json
from utils import hello, get_clean_data

load_dotenv()

app = Flask(__name__, static_folder='build/', static_url_path='/')


## load the data
df = get_clean_data()




#####################################################$$ CREATING INDEX #############################################################
indices = pd.Series(df.index, index=df['title']).drop_duplicates()
max_watchers = df['watchers'].max()
####################################################################################################################################




##################################################### PREPARING TF-IDF #############################################################
####################################################################################################################################
tfidf = TfidfVectorizer(stop_words='english')

tfidf_matrix = tfidf.fit_transform(df['synopsis'])

cosine_sim_tf_idf = linear_kernel(tfidf_matrix, tfidf_matrix)
####################################################################################################################################
####################################################################################################################################


#####################################################$ PREPARING SOUP ##############################################################
####################################################################################################################################
def create_soup(x, director_w, genres_w, tags_w, mainrole_w, supportrole_w):
    soup = ""
    
    for i in range(director_w):
        soup += ' '.join(x['director_list']) + ' '
    for i in range(genres_w):
        soup += ' '.join(x['genres_list']) + ' '
    for i in range(tags_w):
        soup += ' '.join(x['tags_list']) + ' '
    for i in range(mainrole_w):
        soup += ' '.join(x['mainrole_list']) + ' '
    for i in range(supportrole_w):
        soup += ' '.join(x['supportrole_list']) + ' '
    return soup
####################################################################################################################################
####################################################################################################################################



###################################################### GET TOP RECS ################################################################
####################################################################################################################################
top_soup = df.apply(lambda x: create_soup(x, director_w=2, genres_w=4, tags_w=4, mainrole_w=5, supportrole_w=1), axis = 1)
count = CountVectorizer(stop_words='english')
count_matrix = count.fit_transform(top_soup)

cosine_sim_top = cosine_similarity(count_matrix, count_matrix)

def get_top_recommendations(title, tf_idf_w, soup_w, weighted_score_w, watchers_w):
    # Get the index of the movie that matches the title
    idx = indices[title]

    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores_tf_idf = list(enumerate(cosine_sim_tf_idf[idx]))
    sim_scores_soup = list(enumerate(cosine_sim_top[idx]))
    
    recommend_scores = []
    
    for i in range(len(sim_scores_tf_idf)):
        watchers = df['watchers'].iloc[i]/max_watchers
        diminished_watchers = 2*watchers / (2*watchers + .1)
        modified_score = tf_idf_w*sim_scores_tf_idf[i][1] + soup_w*sim_scores_soup[i][1] + weighted_score_w*(df['score'].iloc[i]/10) + watchers_w*diminished_watchers 
        recommend_scores.append((i, modified_score))
    
    recommend_scores = list(compress(recommend_scores, df['watchers'] >= 10000))
    recommend_scores = sorted(recommend_scores, key=lambda x: x[1], reverse=True)
    recommend_scores = recommend_scores[1:11]
    
    movie_indices = [i[0] for i in recommend_scores]
    

    # Return the top 10 most similar movies
    return [[df['title'].iloc[i], df['img_url'].iloc[i], df['score'].iloc[i], df['url'].iloc[i]] for i in movie_indices]
    
####################################################################################################################################
####################################################################################################################################




###################################################### GET CAST RECS ###############################################################
####################################################################################################################################
cast_soup = df.apply(lambda x: create_soup(x, director_w=1, genres_w=0, tags_w=0, mainrole_w=8, supportrole_w=3), axis = 1)
count = CountVectorizer(stop_words='english')
count_matrix_cast = count.fit_transform(cast_soup)

cosine_sim_cast = cosine_similarity(count_matrix_cast, count_matrix_cast)

def get_top_recommendations_cast(title, tf_idf_w, soup_w, weighted_score_w, watchers_w):
    # Get the index of the movie that matches the title
    idx = indices[title]

    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores_tf_idf = list(enumerate(cosine_sim_tf_idf[idx]))
    sim_scores_soup = list(enumerate(cosine_sim_cast[idx]))
    
    recommend_scores = []
    
    for i in range(len(sim_scores_tf_idf)):
        watchers = df['watchers'].iloc[i]/max_watchers
        diminished_watchers = watchers / (watchers + .1)
        modified_score = tf_idf_w*sim_scores_tf_idf[i][1] + soup_w*sim_scores_soup[i][1] + weighted_score_w*(df['score'].iloc[i]/10) + watchers_w*diminished_watchers 
        recommend_scores.append((i, modified_score))
    
    recommend_scores = list(compress(recommend_scores, df['watchers'] > 10000))
    recommend_scores = sorted(recommend_scores, key=lambda x: x[1], reverse=True)
    recommend_scores = recommend_scores[1:11]

    print(recommend_scores)
    
    movie_indices = [i[0] for i in recommend_scores]
    
    # fig, ax = plt.subplots(1,10, figsize=(20,20))
    # for i in range(len(movie_indices)):
    #     url = df.iloc[movie_indices[i]]["img_url"]
    #     response = requests.get(url)
    #     img = Image.open(BytesIO(response.content))
    #     ax[i].imshow(img)
    #     ax[i].axis("off")
    

     # Return the top 10 most similar movies
    return [[df['title'].iloc[i], df['img_url'].iloc[i], df['score'].iloc[i], df['url'].iloc[i]] for i in movie_indices]
    #.sort_values(by=['watchers'], ascending=False)['title']
####################################################################################################################################
####################################################################################################################################

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

    top_recommendations = get_top_recommendations(title, tf_idf_w=.35, soup_w=.525, weighted_score_w=.05, watchers_w=.075)
    top_recommendations_cast = get_top_recommendations_cast(title, tf_idf_w=.05, soup_w=.70, weighted_score_w=.15, watchers_w=.10)

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


#################################### Tests #################################

@app.route("/test")
def test():
    return "Testing, Flask!"

@app.route("/test/dataframe")
def test_dataframe():
    return jsonify({"df": df.to_json(orient=None)})

if __name__ == "__main__":
    app.run(debug=True)