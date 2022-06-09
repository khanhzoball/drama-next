import json
import pandas as pd
import pytest
import numpy as np
from app import app
from utils import get_clean_data
import random

def test_0():
    response = app.test_client().get('/test')

    assert response.status_code == 200
    assert response.data.decode('utf-8') == 'Testing, Flask!'

def test_dictionary():
    response = app.test_client().get('/test/dataframe')
    df = json.loads(response.data.decode('utf-8')).get("df")
    df = pd.read_json(df)

    assert response.status_code == 200
    assert list(df.columns) == ['id','url','title','img_url','type','country','synopsis','director','alsoknownas','episodes','score','ranked','popularity','watchers','aired','duration','genres','tags','mainrole','supportrole','total_raters','director_list','mainrole_list','supportrole_list','genres_list','tags_list','weighted_score']
    assert all(country == "South Korea" for country in list(df.country))
    assert all(show_type == "Drama" for show_type in list(df.type))
    assert all(score <= 10 for score in list(df.score))
    assert all(weighted_score <= 10 for weighted_score in list(df.weighted_score))
    assert all(type(x) is dict for x in list(df.director))
    assert all(type(x) is dict for x in list(df.tags))
    assert all(type(x) is dict for x in list(df.mainrole))
    assert all(type(x) is dict for x in list(df.supportrole))
    assert all(type(x) is list for x in list(df.director_list))
    assert all(type(x) is list for x in list(df.tags_list))
    assert all(type(x) is list for x in list(df.mainrole_list))
    assert all(type(x) is list for x in list(df.supportrole_list))
    assert all(type(x) is list for x in list(df.genres_list))

def test_recommendations_sort():
    df = get_clean_data(data_url="https://raw.githubusercontent.com/khanhzoball/drama-next/main/kdrama.csv")
    valid = []

    for i in range(100):
        response = app.test_client().post('/recommendations', json = {
            "title": df.iloc[i]["title"]
        })

        score_top = json.loads(response.data.decode("utf-8")).get("score_top")
        score_cast = json.loads(response.data.decode("utf-8")).get("score_top_cast")

        valid.append(score_top == sorted(score_top))
        valid.append(score_cast == sorted(score_cast))
    
    assert(all(valid))

# def test_recommendations_sort():
#     response = app.test_client().post('/recommendations', json = {
#             "title": "Start-Up (2020)"
#     })

