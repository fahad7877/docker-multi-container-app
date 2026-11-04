from flask import Flask, jsonify, request
import psycopg2
import os

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "myapp"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "admin123")
    )

@app.route("/")
def home():
    return jsonify({"message": "API is working!"})

@app.route("/api/users", methods=["POST"])
def add_user():
    data = request.get_json()

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
        (data["name"], data["email"])
    )

    user_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "message": "User registered successfully",
        "id": user_id
    })

@app.route("/api/users", methods=["GET"])
def get_users():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, name, email FROM users ORDER BY id")

    users = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([
        {"id": u[0], "name": u[1], "email": u[2]}
        for u in users
    ])

@app.route("/api/health")
def health():
    try:
        conn = get_db()
        conn.close()
        return jsonify({
            "api": "running",
            "database": "connected"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
