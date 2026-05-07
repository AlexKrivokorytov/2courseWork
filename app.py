from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector, os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# Подключение к базе данных
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "game_db")
    )

# Функция для запросов к БД
def query_db(query, params=(), one=False):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute(query, params)
    rv = cur.fetchall()
    cur.close()
    db.close()
    return (rv[0] if rv else None) if one else rv

@app.route("/")
def index():
    s = request.args.get("search", "").strip()
    sort = request.args.get("sort", "title")
    sort_map = {"title": "g.title ASC", "release_date": "g.release_date DESC", "user_score": "avg_score DESC"}
    q = f"""
        SELECT g.*, d.name as developer, 
               (SELECT ROUND(AVG(score),1) FROM reviews WHERE game_id=g.id) as avg_score,
               (SELECT COUNT(*) FROM reviews WHERE game_id=g.id) as review_count
        FROM games g JOIN developers d ON g.developer_id=d.id
        WHERE g.title LIKE %s ORDER BY {sort_map.get(sort, "g.title")}
    """
    return render_template("index.html", games=query_db(q, (f"%{s}%",)), search=s, sort=sort)

@app.route("/game/<int:game_id>")
def game(game_id):
    g = query_db("SELECT g.*, d.name as developer FROM games g JOIN developers d ON g.developer_id=d.id WHERE g.id=%s", (game_id,), one=True)
    if not g: return redirect(url_for("index"))
    revs = query_db("SELECT r.*, u.username FROM reviews r JOIN users u ON r.user_id=u.id WHERE game_id=%s ORDER BY created_at DESC", (game_id,))
    return render_template("game.html", game=g, reviews=revs)

@app.route("/add-game", methods=["GET", "POST"])
def add_game():
    if request.method == "POST":
        db = get_db(); cur = db.cursor()
        # Вызов хранимой процедуры
        cur.callproc("sp_add_game_full", (request.form["title"], request.form["release_date"], request.form["description"], request.form["developer_id"], request.form["publisher_id"], request.form.get("cover_url")))
        for res in cur.stored_results(): gid = res.fetchone()[0]
        db.commit(); cur.close(); db.close()
        return redirect(url_for("game", game_id=gid))
    
    devs = query_db("SELECT id, name FROM developers")
    pubs = query_db("SELECT id, name FROM publishers")
    return render_template("add_game.html", developers=devs, publishers=pubs)

@app.route("/statistics")
def statistics():
    # Данные для графиков
    rankings = query_db("SELECT * FROM v_game_rankings LIMIT 10")
    # Динамика за полгода
    growth = query_db("SELECT DATE_FORMAT(created_at, '%b') as date, COUNT(*) as monthly_reviews FROM reviews GROUP BY 1 ORDER BY MIN(created_at) DESC LIMIT 6")
    growth.reverse()
    # Распределение
    dist = query_db("SELECT FLOOR(score) as rating, COUNT(*) as count FROM reviews GROUP BY 1 ORDER BY 1 DESC")
    return render_template("statistics.html", rankings=rankings, review_growth=growth, score_dist=dist)

@app.route("/logs")
def logs():
    # Список действий
    return render_template("logs.html", logs=query_db("SELECT * FROM review_audit_log ORDER BY id DESC LIMIT 20"))

@app.route("/game/<int:game_id>/review", methods=["POST"])
def add_review(game_id):
    if "user_id" not in session: return redirect(url_for("login"))
    db = get_db(); cur = db.cursor()
    cur.execute("INSERT INTO reviews (game_id, user_id, score, review_text) VALUES (%s,%s,%s,%s)", (game_id, session["user_id"], request.form["score"], request.form["review_text"]))
    db.commit(); cur.close(); db.close()
    flash("Review added!"); return redirect(url_for("game", game_id=game_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = query_db("SELECT * FROM users WHERE username=%s", (request.form["username"],), one=True)
        if u and check_password_hash(u["password_hash"], request.form["password"]):
            session["user_id"], session["username"] = u["id"], u["username"]
            return redirect(url_for("index"))
        flash("Error!")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        db = get_db(); cur = db.cursor()
        cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s,%s,%s)", (request.form["username"], request.form["email"], generate_password_hash(request.form["password"])))
        db.commit(); cur.close(); db.close()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear(); return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
