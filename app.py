import os
import datetime
from flask import Flask, session, g, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "quiz_master_secret_key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///quiz_master.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(hours=2)

# Initialize the app with the extension
db.init_app(app)


# User session management
@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        from models import User
        g.user = User.query.get(user_id)


# Import routes after app is created to avoid circular imports
with app.app_context():
    # Import models
    import models
    
    # Import controllers
    from controllers import auth, admin, user
    
    # Register blueprints
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(user.bp)
    
    # Create tables
    db.create_all()
    
    # Create admin if not exists
    admin_user = models.User.query.filter_by(email="admin@quizmaster.com").first()
    if not admin_user:
        from werkzeug.security import generate_password_hash
        admin = models.User(
            email="admin@quizmaster.com",
            password=generate_password_hash("adminpass"),
            full_name="Quiz Master Admin",
            qualification="Administrator",
            date_of_birth=datetime.date(2000, 1, 1),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        logging.info("Admin user created successfully")


@app.route('/')
def index():
    if g.user:
        if g.user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    return redirect(url_for('auth.login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
