# Retro Block Game

A full-stack retro falling-block puzzle game built with Python, Flask, HTML, CSS, JavaScript, persistent player accounts, and a global leaderboard.

Players create a username, play on desktop or mobile, save validated scores, and compete for the top rank.

## Features

- Classic 10x20 falling-block gameplay, seven-piece bag randomization, score, levels, and fullscreen
- Keyboard and touch controls with a responsive retro interface
- Registration, login, logout, password hashing, CSRF checks, and rate limiting
- Persistent personal records, profiles, rankings, statistics, and global leaderboard
- Server-issued game sessions and server-side result validation
- SQLite development database, PostgreSQL production support, and automated pytest coverage

## Technology stack

| Technology | Role |
|---|---|
| Python and Flask | Backend routes, sessions, API, and server-rendered pages |
| HTML, CSS, JavaScript | Responsive interface and browser canvas game |
| SQLAlchemy | Safe Python-to-database mapping |
| SQLite / PostgreSQL | Local / production persistent data |
| pytest | Automated regression tests |
| Gunicorn | Production WSGI server |
| Git, GitHub, Render | Version control, repository hosting, and deployment |

## Project structure

```text
app/       Flask app, templates, static game files
tests/     Automated tests
instance/  Local SQLite database (ignored by Git)
config.py  Environment and database configuration
run.py     Local Flask entry point
render.yaml Render production Blueprint
```

## Windows installation and local run

Requirements: Python 3.10+ and Git. If `python` is not recognized, install Python from [python.org](https://www.python.org/downloads/windows/) and choose **Add python.exe to PATH**.

```text
cd C:\path\to\retro-block-game
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
flask --app run.py init-db
python run.py
```

Open `http://127.0.0.1:5000`. Run tests with `pytest` while the virtual environment is active.

## Environment variables

Copy `.env.example` to `.env` for local use. `.env` is ignored by Git.

| Variable | Local value | Production value |
|---|---|---|
| `SECRET_KEY` | Private random value | Render-generated secret; required |
| `DATABASE_URL` | SQLite URL | Render PostgreSQL connection string |
| `FLASK_ENV` | `development` | `production` |

Never commit a real `SECRET_KEY`, database URL, password, or `.env` file.

## Gameplay controls

| Desktop | Action |
|---|---|
| Left / Right | Move |
| Down | Soft drop |
| Up | Rotate |
| Space | Hard drop |
| P / Escape | Pause |

On mobile, use the visible Rotate, Left, Down, Right, and Hard Drop buttons.

## Deployment with Render

This repository includes `render.yaml`, defining a Flask web service, PostgreSQL database, production variables, table initialization, and Gunicorn start command.

1. Push this repository to GitHub.
2. In Render, select **New > Blueprint** and connect the repository.
3. Review the resources and create the Blueprint.
4. Wait for the build, open the generated `onrender.com` URL, and test before sharing.

Render officially supports Flask/Gunicorn and GitHub-triggered automatic deploys. Its free web services sleep after 15 idle minutes, and its free PostgreSQL database expires after 30 days. Upgrade the database before relying on it for long-term public player data. See [Render's Flask guide](https://render.com/docs/deploy-flask) and [free-tier limits](https://render.com/docs/free).

## Security

Passwords use Werkzeug hashes and are never stored as plaintext. State-changing requests use CSRF tokens; protected routes require a session; SQLAlchemy avoids string-built SQL; and score submissions must use an unused server game session and pass sanity checks. A browser game cannot completely stop a modified client, so a server-authoritative engine is a future anti-cheat improvement.


## Live Demo
You can view the live demo of this portfolio at: [Live Demo](https://retro-block-game.onrender.com)  

