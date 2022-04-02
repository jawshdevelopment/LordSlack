from datetime import date
from numpy import number


def create_classes(db):
    class Pushup(db.Model):
        __tablename__ = 'pushups'

        id = db.Column(db.Integer, primary_key=True)
        number = db.Column(db.Int)
        date = db.Column(db.DateTime)
        lat = db.Column(db.Float)
        lon = db.Column(db.Float)

        def __repr__(self):
            return '<Pushup %r>' % (self.name)
    return Pushup
