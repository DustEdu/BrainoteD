import sqlalchemy
from flask import Flask
from sqlalchemy import text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

DeclarativeBase = declarative_base()
engine  = sqlalchemy.create_engine("sqlite:///data.db", echo=True)
session = sessionmaker(bind=engine)()

if __name__ == "__main__":
    session.execute(text('PRAGMA foreign_keys=ON'))
    DeclarativeBase.metadata.create_all(bind=engine)

    from flask_routes import *
    app.run(debug=True)
    app.secret_key = "very_secret_key_bro_trust_me_i_bet_your_mom"
