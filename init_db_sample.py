from app import app, db
from app.models import User, Measurement

u = User(username='marion', email='marion@woschek.de')
u.set_password('nasenlurch')
db.session.add(u)

db.session.commit()

db.session.rollback()
