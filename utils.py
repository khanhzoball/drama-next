import pandas as pd
import re
from itertools import compress
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

def hello():
    print("hello world")

def get_clean_data():
    data_url = "https://raw.githubusercontent.com/khanhzoball/drama-next/main/kdrama.csv"
    df = pd.read_csv(data_url)

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

    df["country"] = df["country"].apply(lambda x: x.strip())
    df["type"] = df["type"].apply(lambda x: x.strip())

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
    

    return df

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


def get_recommendations(df, soup, title, tf_idf_w, soup_w, weighted_score_w, watchers_w, cosine_sim_tf_idf, indices, max_watchers, cosine_sim):

    # Get the index of the movie that matches the title
    idx = indices[title]

    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores_tf_idf = list(enumerate(cosine_sim_tf_idf[idx]))
    sim_scores_soup = list(enumerate(cosine_sim[idx]))
    
    recommend_scores = []
    
    for i in range(len(sim_scores_tf_idf)):
        watchers_ratio = df['watchers'].iloc[i]/max_watchers
        diminished_watchers = 2*watchers_ratio / (2*watchers_ratio + .1)
        modified_score = tf_idf_w*sim_scores_tf_idf[i][1] + soup_w*sim_scores_soup[i][1] + weighted_score_w*(df['score'].iloc[i]/10) + watchers_w*diminished_watchers 
        recommend_scores.append((i, modified_score))
    
    recommend_scores = list(compress(recommend_scores, df['watchers'] >= 10000))
    recommend_scores = sorted(recommend_scores, key=lambda x: x[1], reverse=True)
    recommend_scores = recommend_scores[1:11]
    
    movie_indices = [i[0] for i in recommend_scores]
    

    # Return the top 10 most similar movies
    return [[df['title'].iloc[i], df['img_url'].iloc[i], df['score'].iloc[i], df['url'].iloc[i]] for i in movie_indices]