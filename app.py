from flask import Flask, jsonify, request, Response
import pandas as pd
import os
from dotenv import load_dotenv
import re
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from itertools import compress
import json

load_dotenv()

app = Flask(__name__, static_folder='build/', static_url_path='/')


###################################################### LOADING THE DATA ############################################################
####################################################################################################################################
data_url = "https://raw.githubusercontent.com/khanhzoball/drama-next/main/kdrama.csv"
df = pd.read_csv(data_url)
####################################################################################################################################




##################################################### CLEANING THE DATA ############################################################
####################################################################################################################################

# lowercases names and strips white space
def clean_data(x):
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    else:
        #Check if director exists. If not, return empty string
        if isinstance(x, str):
            return str.lower(x.replace(" ", ""))
        else:
            return ''

df["ranked"] = pd.to_numeric(df["ranked"].str.replace("#", ""))
df["popularity"] = pd.to_numeric(df["popularity"].str.replace("#", ""))
df["watchers"] = pd.to_numeric(df["watchers"].str.replace(",", ""))

df['synopsis'] = df['synopsis'].fillna('')
df['genres'] = df['genres'].fillna('')
df['tags'] = df['tags'].fillna('')
df['mainrole'] = df['mainrole'].fillna('')
df['supportrole'] = df['supportrole'].fillna('')
df['director'] = df['director'].fillna('')


score_series = df["score"].str.split("(")

df["score"] = [float(i[0]) for i in score_series]
df["total_raters"] = [int(re.sub("[^0-9.]", "", i[1])) for i in score_series]

mainrole = df["mainrole"]
mainrole = mainrole.str.split(',')
mainrole = [dict.fromkeys(mainrole[i][0:], "1") for i in range(len(mainrole))]
df["mainrole"] = mainrole

supportrole = df["supportrole"]
supportrole = supportrole.str.split(',')
supportrole = [dict.fromkeys(supportrole[i][0:], "1") for i in range(len(supportrole))]
df["supportrole"] = supportrole

genres = df["genres"]
genres = genres.str.split(',')
genres = [dict.fromkeys(genres[i][0:], "1") for i in range(len(genres))]
df["genres"] = genres

tags = df["tags"]
tags = tags.str.split(',')
tags = [dict.fromkeys(tags[i][0:], "1") for i in range(len(tags))]
df["tags"] = tags

director = df["director"]
director = director.str.split(',')
director = [dict.fromkeys(director[i][0:], "1") for i in range(len(director))]
df["director"] = director

df["director_list"] = df["director"].apply(lambda x: list(x.keys())).apply(clean_data)
df["mainrole_list"] = df["mainrole"].apply(lambda x: list(x.keys())).apply(clean_data)
df["supportrole_list"] = df["supportrole"].apply(lambda x: list(x.keys())).apply(clean_data)
df["genres_list"] = df["genres"].apply(lambda x: list(x.keys()))
df["tags_list"] = df["tags"].apply(lambda x: list(x.keys()))

v = df["total_raters"]
m = 10000
r = df["score"]
c = r.mean()

df["weighted_score"] = ((v*r)/(v+m)) + ((m*c)/(v+m))
####################################################################################################################################
####################################################################################################################################




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
    return list(df['title'].iloc[movie_indices])
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

if __name__ == "__main__":
    app.run(debug=True)