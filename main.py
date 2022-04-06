import os
from flask import Flask
from flask_restful import Resource, Api
from application import config
from application.config import LocalDevelopmentConfig
from application.data.database import db
from application.jobs import workers
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_security import Security, SQLAlchemySessionUserDatastore, SQLAlchemyUserDatastore
from application.data.models import User, Role

from flask_login import LoginManager
from flask_security import utils
from flask_cors import CORS

app = None
api = None
celery = None

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
    # Create celery
    celery = workers.celery
    # Update with configuration
    celery.conf.update(
        broker_url = app.config["CELERY_BROKER_URL"],
        result_backend = app.config["CELERY_RESULT_BACKEND"],
        timezone='Asia/Kolkata'
        )
    celery.Task = workers.ContextTask
    app.app_context().push()
    
    return app, api, celery

app,api,celery = create_app()

from application.controller.api import UserAPI, DeckAPI, CardAPI
api.add_resource(UserAPI, "/api/user")
api.add_resource(DeckAPI, "/api/deck", "/api/deck/<int:deck_id>")
api.add_resource(CardAPI, "/api/card/<int:id>")



if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0',port=8080, debug=True)