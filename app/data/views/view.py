from flask import Blueprint, request, jsonify, make_response
from sqlalchemy.sql.elements import and_, or_
from sqlalchemy import distinct
from app.data.models import db
from app.data.helper import Helper, remove_diacritic, is_about_politician, decimal_default, flatten
from flask_restful import Api, Resource
import requests
import unidecode
import unicodedata

import json
from decimal import Decimal

stats = Blueprint('stats', __name__)
helper = Helper()
helper.load()



class View(Resource):
    root = 'https://api.monitora.cz/transparency/'
    @staticmethod
    def politicians():
        response = requests.get(View.root + 'politicians/', headers={'Authorization': 'Token ThwtYIS10zUEQ3KIgguqZ4Rd4H6BgTJ7'})
        response.encoding = 'utf-8'
        keys = ['id', 'name','search_query', 'party']
        data = [{key: item[key] for key in keys} for item in response.json()]
        return json.dumps(data)

    @staticmethod
    def articlesForPolitician(id):
        response = requests.get(View.root + 'articles/' + str(id), headers={'Authorization': 'Token ThwtYIS10zUEQ3KIgguqZ4Rd4H6BgTJ7'}, params={"count": 1})
        response.encoding = 'utf-8'
        keys = ['source', 'title', 'url', 'shares', 'perex', 'text']
        data = [{key: item[key] for key in keys} for item in response.json()]
        for index, item in enumerate(data):
            data[index]['perex'] = str(item['perex'].replace("<span class=\"article-hl\">", "").replace("</span>",""))
            text = str(remove_diacritic(data[index]['text'])).replace("\\n", " ")
            data[index]['clean-text'] = text
        with open('articles.json', 'w') as outfile:
            json.dump(data, outfile)
        return json.dumps(data)


    @staticmethod
    def topics():
        pass

    @staticmethod
    def searchPoliticianByName(name):
        for pol in json.loads(View.politicians()):
            if name == pol["name"]:
                return pol["id"]

    @staticmethod
    def topicsForPoliticianByQuery():
        raw_dict = request.get_json(force=True)
        politician_dict = raw_dict['data']
        id = View.searchPoliticianByName(politician_dict["name"])
        if id is None:
            requests.post(View.root + 'politicians/',
                                 json=politician_dict,
                                 headers={'Authorization': 'Token ThwtYIS10zUEQ3KIgguqZ4Rd4H6BgTJ7'})
        id = View.searchPoliticianByName(politician_dict["name"])
        response = requests.get(View.root + 'articles/' + str(id), headers={'Authorization': 'Token ThwtYIS10zUEQ3KIgguqZ4Rd4H6BgTJ7'}, params={"count": 100})
        #response.encoding = 'utf-8'
        data = helper.process(' '.join([item["text"] for item in response.json()]))
        return json.dumps(data)


    @staticmethod
    def topicsForPoliticianById(id):
        response = requests.get(View.root + 'articles/' + str(id), headers={'Authorization': 'Token ThwtYIS10zUEQ3KIgguqZ4Rd4H6BgTJ7'}, params={"count": 100})
        #response.encoding = 'utf-8'
        data = helper.process(' '.join([item["text"] for item in response.json()]))
        return json.dumps(data)

    @staticmethod
    def addPolitician():
        raw_dict = request.get_json(force=True)
        politician_dict = raw_dict['data']
        response = requests.post(View.root + 'politicians/',
                                json={"name": "Martin Charvát", "party": "ODS"},
                                headers={'Authorization': 'Token ThwtYIS10zUEQ3KIgguqZ4Rd4H6BgTJ7'})
        return View.politicians()


