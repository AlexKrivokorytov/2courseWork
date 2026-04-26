from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")


def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "game_db"),
    )


def fetch_all(query, params=()):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    db.close()
    return rows


def fetch_one(query, params=()):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(query, params)
    row = cur.fetchone()
    cur.close()
    db.close()
    return row


def execute(query, params=()):
    db = get_db()
    cur = db.cursor()
    cur.execute(query, params)
    db.commit()
    last_id = cur.lastrowid
    cur.close()
    db.close()
    return last_id


def execute_many(query, params_list):
    db = get_db()
    cur = db.cursor()
    cur.executemany(query, params_list)
    db.commit()
    cur.close()
    db.close()


def get_form_choices():
    return {
        "developers": fetch_all("SELECT id, name FROM developers ORDER BY name"),
        "publishers": fetch_all("SELECT id, name FROM publishers ORDER BY name"),
        "genres": fetch_all("SELECT id, name FROM genres ORDER BY name"),
        "platforms": fetch_all("SELECT id, name, abbreviation FROM platforms ORDER BY name"),
        "critics": fetch_all("SELECT id, name, outlet FROM critics ORDER BY name"),
    }


@app.route("/")
def index():
    search = request.args.get("search", "").strip()
    sort = request.args.get("sort", "title")
    sort_map = {
        "title": "g.title ASC",
        "release_date": "g.release_date DESC",
        "user_score": "avg_user_score DESC, g.title ASC",
        "critic_score": "avg_critic_score DESC, g.title ASC",
    }
    order_by = sort_map.get(sort, "g.title ASC")
    where_clause = ""
    params = ()
    if search:
        where_clause = "WHERE g.title LIKE %s"
        params = (f"%{search}%",)

    games = fetch_all(
        f"""
        SELECT g.id, g.title, g.release_date, g.cover_url,
               d.name AS developer, p.name AS publisher,
               GROUP_CONCAT(DISTINCT ge.name SEPARATOR ', ') AS genres,
               GROUP_CONCAT(DISTINCT pl.abbreviation SEPARATOR ', ') AS platforms,
               (
                   SELECT ROUND(AVG(ur.score), 1)
                   FROM user_reviews ur
                   WHERE ur.game_id = g.id
               ) AS avg_user_score,
               (
                   SELECT COUNT(*)
                   FROM user_reviews ur
                   WHERE ur.game_id = g.id
               ) AS user_review_count,
               (
                   SELECT ROUND(AVG(cr.score), 1)
                   FROM critic_reviews cr
                   WHERE cr.game_id = g.id
               ) AS avg_critic_score,
               (
                   SELECT COUNT(*)
                   FROM critic_reviews cr
                   WHERE cr.game_id = g.id
               ) AS critic_review_count
        FROM games g
        JOIN developers d ON d.id = g.developer_id
        JOIN publishers p ON p.id = g.publisher_id
        LEFT JOIN game_genres gg ON gg.game_id = g.id
        LEFT JOIN genres ge ON ge.id = gg.genre_id
        LEFT JOIN game_platforms gp ON gp.game_id = g.id
        LEFT JOIN platforms pl ON pl.id = gp.platform_id
        {where_clause}
        GROUP BY g.id
        ORDER BY {order_by}
        """,
        params,
    )
    return render_template("index.html", games=games, search=search, sort=sort)


@app.route("/game/<int:game_id>")
def game(game_id):
    g = fetch_one(
        """
        SELECT g.id, g.title, g.release_date, g.description, g.cover_url,
               d.name AS developer, p.name AS publisher,
               GROUP_CONCAT(DISTINCT ge.name SEPARATOR ', ') AS genres,
               GROUP_CONCAT(DISTINCT pl.name SEPARATOR ', ') AS platforms,
               (
                   SELECT ROUND(AVG(ur.score), 1)
                   FROM user_reviews ur
                   WHERE ur.game_id = g.id
               ) AS avg_user_score,
               (
                   SELECT COUNT(*)
                   FROM user_reviews ur
                   WHERE ur.game_id = g.id
               ) AS user_review_count,
               (
                   SELECT ROUND(AVG(cr.score), 1)
                   FROM critic_reviews cr
                   WHERE cr.game_id = g.id
               ) AS avg_critic_score,
               (
                   SELECT COUNT(*)
                   FROM critic_reviews cr
                   WHERE cr.game_id = g.id
               ) AS critic_review_count
        FROM games g
        JOIN developers d ON d.id = g.developer_id
        JOIN publishers p ON p.id = g.publisher_id
        LEFT JOIN game_genres gg ON gg.game_id = g.id
        LEFT JOIN genres ge ON ge.id = gg.genre_id
        LEFT JOIN game_platforms gp ON gp.game_id = g.id
        LEFT JOIN platforms pl ON pl.id = gp.platform_id
        WHERE g.id = %s
        GROUP BY g.id
        """,
        (game_id,),
    )

    if not g:
        flash("Game not found.", "error")
        return redirect(url_for("index"))

    user_reviews = fetch_all(
        """
        SELECT ur.score, ur.review_text, ur.created_at, u.username
        FROM user_reviews ur
        JOIN users u ON u.id = ur.user_id
        WHERE ur.game_id = %s
        ORDER BY ur.created_at DESC
        """,
        (game_id,),
    )

    critic_reviews = fetch_all(
        """
        SELECT cr.score, cr.review_text, cr.created_at, c.name, c.outlet
        FROM critic_reviews cr
        JOIN critics c ON c.id = cr.critic_id
        WHERE cr.game_id = %s
        ORDER BY cr.created_at DESC
        """,
        (game_id,),
    )

    choices = get_form_choices()
    return render_template(
        "game.html",
        game=g,
        user_reviews=user_reviews,
        critic_reviews=critic_reviews,
        critics=choices["critics"],
    )


@app.route("/add-game", methods=["GET", "POST"])
def add_game():
    if request.method == "POST":
        title = request.form["title"].strip()
        release = request.form["release_date"]
        description = request.form["description"].strip()
        cover_url = request.form.get("cover_url", "").strip() or None
        dev_id = int(request.form["developer_id"])
        pub_id = int(request.form["publisher_id"])
        genre_ids = request.form.getlist("genre_ids")
        platform_ids = request.form.getlist("platform_ids")

        game_id = execute(
            "INSERT INTO games (title, release_date, description, developer_id, publisher_id, cover_url) VALUES (%s,%s,%s,%s,%s,%s)",
            (title, release, description, dev_id, pub_id, cover_url),
        )
        if genre_ids:
            execute_many(
                "INSERT INTO game_genres (game_id, genre_id) VALUES (%s,%s)",
                [(game_id, int(gid)) for gid in genre_ids],
            )
        if platform_ids:
            execute_many(
                "INSERT INTO game_platforms (game_id, platform_id) VALUES (%s,%s)",
                [(game_id, int(pid)) for pid in platform_ids],
            )

        flash("Game added.", "success")
        return redirect(url_for("game", game_id=game_id))

    return render_template("add_game.html", **get_form_choices())


@app.route("/game/<int:game_id>/user-review", methods=["POST"])
def add_user_review(game_id):
    if "user_id" not in session:
        flash("Log in to leave a review.", "error")
        return redirect(url_for("login"))

    score = request.form.get("score", type=float)
    text = request.form["review_text"].strip()

    if score is None or not (0 <= score <= 10) or not text:
        flash("Fill in all fields. Score must be between 0 and 10.", "error")
        return redirect(url_for("game", game_id=game_id))

    existing_review = fetch_one(
        "SELECT id FROM user_reviews WHERE game_id = %s AND user_id = %s",
        (game_id, session["user_id"]),
    )
    if existing_review:
        flash("You have already reviewed this game.", "error")
        return redirect(url_for("game", game_id=game_id))

    execute(
        "INSERT INTO user_reviews (game_id, user_id, score, review_text, created_at) VALUES (%s,%s,%s,%s,NOW())",
        (game_id, session["user_id"], score, text),
    )
    flash("Review added.", "success")
    return redirect(url_for("game", game_id=game_id))


@app.route("/game/<int:game_id>/critic-review", methods=["POST"])
def add_critic_review(game_id):
    critic_id = request.form.get("critic_id", type=int)
    score = request.form.get("score", type=float)
    text = request.form["review_text"].strip()

    if not critic_id or score is None or not (0 <= score <= 10) or not text:
        flash("Fill in all fields. Score must be between 0 and 10.", "error")
        return redirect(url_for("game", game_id=game_id))

    existing_review = fetch_one(
        "SELECT id FROM critic_reviews WHERE game_id = %s AND critic_id = %s",
        (game_id, critic_id),
    )
    if existing_review:
        flash("This critic has already reviewed the game.", "error")
        return redirect(url_for("game", game_id=game_id))

    execute(
        "INSERT INTO critic_reviews (game_id, critic_id, score, review_text, created_at) VALUES (%s,%s,%s,%s,NOW())",
        (game_id, critic_id, score, text),
    )
    flash("Critic review added.", "success")
    return redirect(url_for("game", game_id=game_id))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        hashed = generate_password_hash(password)
        try:
            execute(
                "INSERT INTO users (username, email, password_hash, created_at) VALUES (%s,%s,%s,NOW())",
                (username, email, hashed),
            )
            flash("Account created. Log in now.", "success")
            return redirect(url_for("login"))
        except Exception:
            flash("A user with this username or email already exists.", "error")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = fetch_one("SELECT * FROM users WHERE username = %s", (username,))
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            flash(f"Welcome, {user['username']}!", "success")
            return redirect(url_for("index"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have logged out.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
