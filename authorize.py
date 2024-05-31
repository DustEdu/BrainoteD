from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager

from main import app

app.debug = True
# app.config['SECRET_KEY'] = 'a really really really really long secret key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:pass@localhost/flask_app_db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = 'youmail@gmail.com'
# app.config['MAIL_DEFAULT_SENDER'] = 'youmail@gmail.com'
# app.config['MAIL_PASSWORD'] = 'password'

# manager = Manager(app)
# manager.add_command('db', MigrateCommand)
# db = SQLAlchemy(app)
# migrate = Migrate(app,  db)
# mail = Mail(app)

login_manager = LoginManager(app)
