from flask import Flask
from application.database import db
from application.models import *
app = None

def create_app():
    app = Flask(__name__, template_folder='.', static_folder='static')
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tma.sqlite3'
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()
from application.auth import auth_bp, format_date
app.register_blueprint(auth_bp)
app.jinja_env.filters['date'] = format_date

with app.app_context():
    db.create_all()
    Admin = User.query.filter_by(role='admin').first()
    if Admin is None:
        Admin = User(fullname='Admin', email='admin@gmail.com', password='admin1234', role='admin')
        db.session.add(Admin)
        db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
