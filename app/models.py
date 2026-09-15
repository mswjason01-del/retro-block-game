from datetime import datetime, timezone
from . import db


def now():
    return datetime.now(timezone.utc)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)
    high_score = db.Column(db.Integer, default=0, nullable=False)
    high_score_lines = db.Column(db.Integer, default=0, nullable=False)
    high_score_level = db.Column(db.Integer, default=1, nullable=False)
    games = db.relationship("GameSession", backref="user", lazy=True, cascade="all, delete-orphan")


class GameSession(db.Model):
    id = db.Column(db.String(48), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    started_at = db.Column(db.DateTime(timezone=True), default=now, nullable=False)
    ended_at = db.Column(db.DateTime(timezone=True), nullable=True)
    score = db.Column(db.Integer, nullable=True)
    lines = db.Column(db.Integer, nullable=True)
    level = db.Column(db.Integer, nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)
