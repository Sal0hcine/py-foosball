from app import db
import datetime

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    team1score = db.Column(db.Integer, default=0)
    team2score = db.Column(db.Integer, default=0)
    complete = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return '<Match %r>' % (self.id)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, default="")

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    matchId = db.Column(db.Integer, db.ForeignKey('match.id'), default=0)
    match = db.relationship('Match', backref=db.backref('goals', lazy='dynamic'))
    playerId = db.Column(db.Integer, db.ForeignKey('player.id'), default=0)
    player = db.relationship('Player', backref=db.backref('goals', lazy='dynamic'))
    position = db.Column(db.String, default="")
    ownGoal = db.Column(db.Boolean, default=False)