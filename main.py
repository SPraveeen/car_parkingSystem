import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, login_manager

# Get the absolute path of the project directory
basedir = os.path.abspath(os.path.dirname(__file__))

def create_app():
    app = Flask(__name__, template_folder='.')
    app.config['SECRET_KEY'] = 'a_very_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'parking.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Configure Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from admin import admin_bp
    app.register_blueprint(admin_bp)

    from auth import auth_bp
    app.register_blueprint(auth_bp)

    from user import user_bp
    app.register_blueprint(user_bp)

    # Import models here to avoid circular imports
    with app.app_context():
        from models import User, ParkingLot 
        db.create_all()
        # Create admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            admin_user = User(username='admin', password=generate_password_hash('admin', method='pbkdf2:sha256'), is_admin=True)
            db.session.add(admin_user)
            db.session.commit()

    return app

app = create_app()

@app.route('/')
def index():
    from models import ParkingLot
    lots = ParkingLot.query.all()
    return render_template('index.html', parking_lots=lots)

if __name__ == '__main__':
    app.run(debug=True)