from flask_restful import Resource, Api
from flask_restful import fields, marshal_with, marshal
from flask_restful import reqparse
from application.data.database import db
from flask import current_app as app
from flask import request
from application.data.models import *
import werkzeug
import requests
import json
import csv
import uuid
from datetime import datetime
from flask import abort
from flask_login import current_user
from flask_bcrypt import Bcrypt
from flask_security import auth_required, login_required, roles_accepted, roles_required, auth_token_required

from application.jobs import tasks
from flask_caching import Cache
import time

# add cache to the app
cache = Cache(app)
app.app_context().push()

expor_deck_post_args = reqparse.RequestParser()
expor_deck_post_args.add_argument('d_id')
expor_deck_post_args.add_argument('deck_name')
expor_deck_post_args.add_argument('deck_info')
expor_deck_post_args.add_argument('score')
expor_deck_post_args.add_argument('time_created')

@app.route("/export", methods=["POST"])
@auth_token_required
def export_to_csv():
    args = request.get_json()
    if args:
        deck_data, card_data = [], []
        for arg in args:
            my_deck = current_user.decks.filter(Deck.d_id == arg["d_id"]).first()
            json_deck_data = marshal(my_deck, deck_fields)
            deck_data.append(json_deck_data)
            json_card_data = marshal(my_deck.cards.all(), card_fields)
            card_data.append(json_card_data)
        job = tasks.export_data_to_csv.delay([deck_data, card_data])
        result = job.wait()
        return "Ok", 200
    else:
        return "oops something wrong", 404

@app.route("/remind", methods=["GET"])
def remind():
    # ptask = PeriodicTask.objects.get(name='task_name')
    ptask = tasks.setup_periodic_tasks.s()
    ptask.enabled = False
    ptask.save()
    return "ok", 200

user_post_args = reqparse.RequestParser()
user_post_args.add_argument('username')
user_post_args.add_argument('email')
user_post_args.add_argument('password')


class UserAPI(Resource):
    @auth_token_required
    def get(self):
        
        return {"public_id" : current_user.public_id, "name" : current_user.username}

    def post(self):

        args = user_post_args.parse_args()

        user = db.session.query(User).filter(User.email == args["email"]).first()

        if user:
            return "email already in use", 435

        new_user = User(username=args["username"], email=args["email"], password=args["password"])
        new_user.fs_uniquifier = str(uuid.uuid4())
        new_user.public_id = str(uuid.uuid4())
        new_user.active = 1
        db.session.add(new_user)
        db.session.commit()
        
        return "registration successful", 200

deck_post_args = reqparse.RequestParser()
deck_post_args.add_argument('deck_name')
deck_post_args.add_argument('deck_info')

deck_fields = {
    "d_id": fields.Integer,
    "deck_name": fields.String,
    "deck_info": fields.String,
    "time_created": fields.String,
    "score": fields.Integer
}

class DeckAPI(Resource):
    @auth_token_required
    # @cache.cached(timeout=50)
    @marshal_with(deck_fields)
    def get(self):
        start = time.perf_counter_ns()
        # send all the available decks
        all_decks = current_user.decks.all(), 201
        stop = time.perf_counter_ns()
        print("time taken to retrieve deck data", stop - start)
        return all_decks

    @auth_token_required
    def post(self):
        args = deck_post_args.parse_args()

        new_deck = Deck(deck_name=args["deck_name"], deck_info=args["deck_info"], score=0)
        db.session.add(new_deck)
        current_user.decks.append(new_deck)
        db.session.commit()

        return "deck added successfully", 200

    @auth_token_required
    def put(self, deck_id):
        args = deck_post_args.parse_args()
        deck = db.session.query(Deck).filter(Deck.d_id == deck_id).first()

        if deck:
            deck.deck_name = args["deck_name"]
            deck.deck_info = args["deck_info"]
            db.session.commit()

            return "Deck updated successfully", 201

    @auth_token_required
    def delete(self, deck_id):
        deck = db.session.query(Deck).filter(Deck.d_id==deck_id).first()

        if deck:
            db.session.delete(deck)
            db.session.commit()
        
        return "deck deleted successfully", 201

card_post_args = reqparse.RequestParser()
card_post_args.add_argument('front')
card_post_args.add_argument('back')

card_fields = {
    "c_id": fields.Integer,
    "front": fields.String,
    "back": fields.String,
    "score": fields.Integer
}

class CardAPI(Resource):
    @auth_token_required
    @marshal_with(card_fields)
    def get(self, id):
        deck = current_user.decks.filter(Deck.d_id==id).first()
        cards = []
        if deck:
            cards = deck.cards.all()
            return cards, 201
        else:
            return "not found", 404

    @auth_token_required
    def post(self, id):
        args = card_post_args.parse_args()

        deck = current_user.decks.filter(Deck.d_id==id).first()
        if deck:
            new_card = Card(front=args["front"], back=args["back"], score=0)
            db.session.add(new_card)
            deck.cards.append(new_card)
            db.session.commit()
            return "card added successfully", 201
        else:
            return "something went wrong", 404

    @auth_token_required
    def put(self, id):
        deck = current_user.decks.filter(Deck.d_id == id).first()
        if deck:
            deck.time_created = datetime.now()
            cards_json = request.get_json()
        if cards_json:
            score = 0
            for card_json in cards_json:
                card =  deck.cards.filter(Card.c_id == card_json["c_id"]).first()
                card.front = card_json["front"]
                card.back = card_json["back"]
                card.score = card_json["score"]
                score += card_json["score"]
            score = score // len(card_json)
            deck.score = score
            db.session.commit()
        else:
            deck.score = 0
            db.session.commit()
            return "No cards to update", 201

        return "all cards has been updated", 201

    @auth_token_required
    def delete(self, id):
        card = db.session.query(Card).filter(Card.c_id==id).first()

        if card:
            db.session.delete(card)
            db.session.commit()
        
        return "card deleted successfully", 201
