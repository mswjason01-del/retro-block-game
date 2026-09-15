import secrets
from datetime import datetime, timezone
from functools import wraps
from flask import Blueprint, abort, jsonify, render_template, request, session
from . import db
from .auth import valid_csrf
from .models import GameSession, User

main_bp = Blueprint("main", __name__)


def current_user():
    user_id = session.get("user_id")
    return db.session.get(User, user_id) if user_id else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user():
            if request.path.startswith("/api/"):
                return jsonify(error="Authentication required."), 401
            return render_template("error.html", code=401, message="Please log in to enter the arcade."), 401
        return view(*args, **kwargs)
    return wrapped


def rank_for(user):
    return User.query.filter(User.high_score > user.high_score).count() + 1


@main_bp.get("/")
def index():
    return render_template("index.html")


@main_bp.get("/game")
@login_required
def game():
    return render_template("game.html", user=current_user())


@main_bp.get("/leaderboard")
def leaderboard():
    players = User.query.order_by(User.high_score.desc(), User.high_score_lines.desc(), User.created_at.asc()).limit(10).all()
    return render_template("leaderboard.html", players=players, me=current_user())


@main_bp.get("/profile")
@login_required
def profile():
    user = current_user()
    completed = GameSession.query.filter_by(user_id=user.id, completed=True)
    total_games = completed.count()
    total_lines = db.session.query(db.func.coalesce(db.func.sum(GameSession.lines), 0)).filter_by(user_id=user.id, completed=True).scalar()
    average = db.session.query(db.func.coalesce(db.func.avg(GameSession.score), 0)).filter_by(user_id=user.id, completed=True).scalar()
    return render_template("profile.html", user=user, rank=rank_for(user), total_games=total_games, total_lines=total_lines, average=int(average))


@main_bp.get("/privacy")
def privacy():
    return render_template("privacy.html")


@main_bp.get("/api/leaderboard")
def leaderboard_api():
    players = User.query.order_by(User.high_score.desc(), User.high_score_lines.desc(), User.created_at.asc()).limit(10).all()
    return jsonify(players=[{"rank": i + 1, "username": p.username, "score": p.high_score, "lines": p.high_score_lines, "level": p.high_score_level} for i, p in enumerate(players)])


@main_bp.get("/api/me")
@login_required
def me_api():
    user = current_user()
    return jsonify(username=user.username, high_score=user.high_score, rank=rank_for(user))


@main_bp.post("/api/game/start")
@login_required
def start_game():
    if request.headers.get("X-CSRF-Token") != session.get("csrf_token"):
        return jsonify(error="Invalid request token."), 400
    game_session = GameSession(id=secrets.token_urlsafe(28), user_id=current_user().id)
    db.session.add(game_session)
    db.session.commit()
    return jsonify(session_id=game_session.id)


@main_bp.post("/api/game/finish")
@login_required
def finish_game():
    if request.headers.get("X-CSRF-Token") != session.get("csrf_token"):
        return jsonify(error="Invalid request token."), 400
    data = request.get_json(silent=True) or {}
    game_session = db.session.get(GameSession, data.get("session_id", ""))
    if not game_session or game_session.user_id != current_user().id or game_session.completed:
        return jsonify(error="Invalid or completed game session."), 400
    try:
        score, lines, level = int(data["score"]), int(data["lines"]), int(data["level"])
    except (KeyError, TypeError, ValueError):
        return jsonify(error="Invalid game result."), 400
    expected_level = 1 + lines // 10
    plausible_score = 500 + lines * 4000 + level * 500
    if not (0 <= lines <= 100000 and 1 <= level <= 10001 and level == expected_level and 0 <= score <= plausible_score):
        return jsonify(error="Game result failed validation."), 400
    game_session.score, game_session.lines, game_session.level = score, lines, level
    game_session.completed, game_session.ended_at = True, datetime.now(timezone.utc)
    user = current_user()
    new_high = score > user.high_score
    if new_high:
        user.high_score, user.high_score_lines, user.high_score_level = score, lines, level
    db.session.commit()
    is_global_one = new_high and rank_for(user) == 1
    return jsonify(saved=True, high_score=user.high_score, new_high_score=new_high, new_global_record=is_global_one, rank=rank_for(user))
