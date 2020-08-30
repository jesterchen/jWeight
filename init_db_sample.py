from app import app, db
from app.models import User, Measurement

u = User(username='username', email='user@email')
u.set_password('secret-password')
db.session.add(u)

mt = MeasureTypes(description='weight')
db.session.add(mt)
mt = MeasureTypes(description='bmi')
db.session.add(mt)

m = Measurement(user_id=1, date='202002721925')

v = Values(measure_id=1, measure_type_id=1, value=130)
db.session.add(v)
v = Values(measure_id=1, measure_type_id=2, value=30)
db.session.add(v)

db.session.commit()

db.session.rollback()
