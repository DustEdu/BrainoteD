import flask
import sqlalchemy.orm

from routes import register_admin

# Flask app config
app = flask.Flask(__name__)
app.secret_key = "very_secret_key_bro_trust_me_i_bet_your_mom"
app.config["SESSION_TYPE"] = "SQLALchemy"

# SQLAlchemy DB config
engine = sqlalchemy.create_engine("sqlite:///data.db", echo=True)
dbs = sqlalchemy.orm.sessionmaker(bind=engine)()
DeclarativeBase = sqlalchemy.orm.declarative_base()


if __name__ == "__main__":
    dbs.execute(sqlalchemy.text('PRAGMA foreign_keys=ON'))
    DeclarativeBase.metadata.create_all(bind=engine)

    from flask_routes import *
    app.run(debug=True)

    register_admin()
