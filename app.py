from flask import Flask
import pandas as pd
import os
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__, static_folder='build/', static_url_path='/')


###################################################### LOADING THE DATA ############################################################
####################################################################################################################################
data_url = os.getenv("DATA_URL")
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

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/hello')
def hello():
    return "hello world"

if __name__ == "__main__":
    app.run(debug=True)