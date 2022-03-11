import os
from flask import Flask
from flask_restful import Resource, Api
from application import config
from application.config import LocalDevelopmentConfig
from application.database import db
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_security import Security, SQLAlchemySessionUserDatastore, SQLAlchemyUserDatastore
from application.models import User, Role
from flask_login import LoginManager
from flask_security import utils
from flask_cors import CORS

app = None
api = None

def create_app():
	app = Flask(__name__)
	app.config.from_object(LocalDevelopmentConfig)
	db.init_app(app)
	app.app_context().push()
	
  # Setup Flask-Security
	user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
	security = Security(app, user_datastore)

	@security.register_context_processor
	def security_login_processor():
	    return dict(something="else")

	api = Api(app)
	CORS(app)
	app.app_context().push()
	return app, api

app,api = create_app()

from application.api import *
api.add_resource(UserAPI, "/api/user")
api.add_resource(DeckAPI, "/api/deck", "/api/deck/<int:deck_id>")
api.add_resource(CardAPI, "/api/card/<int:deck_id>")



if __name__ == '__main__':
  # Run the Flask app
  app.run(host='0.0.0.0',port=8080, debug=True)