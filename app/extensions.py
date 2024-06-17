from flask_pymongo import PyMongo

# Setup MongoDB here
# mongo = PyMongo(uri="mongodb://localhost:27017/database")
mongo = PyMongo()

def init_app(app):
    app.config["MONGO_URI"] = "mongodb://localhost:27017/github_webhooks"
    mongo.init_app(app)