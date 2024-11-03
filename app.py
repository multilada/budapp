from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with a strong, random secret key

# Database configuration
DATABASE = "budgeting.db"


def get_db_connection():
    """Connects to the database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def close_db(conn=None):
    """Closes the database connection."""
    if conn is not None:
        conn.close()


# Define the database schema
def create_tables():
    """Creates the database tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS users (
          user_id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL
      )
  """
    )
    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS incomes (
          income_id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER,
          source TEXT NOT NULL,
          amount REAL NOT NULL,
          frequency TEXT NOT NULL,
          FOREIGN KEY (user_id) REFERENCES users(user_id)
      )
  """
    )
    cursor.execute(
        """
      CREATE TABLE IF NOT EXISTS expenses (
          expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER,
          category TEXT NOT NULL,
          spending_category TEXT NOT NULL,
          amount REAL NOT NULL,
          frequency TEXT NOT NULL,
          FOREIGN KEY (user_id) REFERENCES users(user_id)
      )
  """
    )
    conn.commit()
    close_db(conn)


# Create tables if they don't exist
create_tables()


@app.route("/")
def index():
    """Renders the home page."""
    return render_template("index.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handles user signup."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash),
            )
            conn.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            return render_template("signup.html", error="Username already exists.")
        finally:
            close_db(conn)

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash),
        )
        user = cursor.fetchone()
        close_db(conn)

        if user:
            session["user_id"] = user["user_id"]
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    """Displays the user's dashboard."""
    user_id = session.get("user_id")
    if user_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM incomes WHERE user_id = ?", (user_id,))
        incomes = cursor.fetchall()
        cursor.execute("SELECT * FROM expenses WHERE user_id = ?", (user_id,))
        expenses = cursor.fetchall()
        close_db(conn)
        return render_template("dashboard.html", incomes=incomes, expenses=expenses)
    else:
        return redirect(url_for("login"))


@app.route("/add_income", methods=["GET", "POST"])
def add_income():
    """Handles adding a new income source."""
    user_id = session.get("user_id")
    if user_id:
        if request.method == "POST":
            source = request.form["source"]
            amount = request.form["amount"]
            frequency = request.form["frequency"]

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO incomes (user_id, source, amount, frequency) VALUES (?, ?, ?, ?)",
                (user_id, source, amount, frequency),
            )
            conn.commit()
            close_db(conn)
            return redirect(url_for("dashboard"))
        return render_template("add_income.html")
    else:
        return redirect(url_for("login"))


@app.route("/add_expense", methods=["GET", "POST"])
def add_expense():
    """Handles adding a new expense."""
    user_id = session.get("user_id")
    if user_id:
        if request.method == "POST":
            category = request.form["category"]
            spending_category = request.form["spending_category"]
            amount = request.form["amount"]
            frequency = request.form["frequency"]

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO expenses (user_id, category, spending_category, amount, frequency) VALUES (?, ?, ?, ?, ?)",
                (user_id, category, spending_category, amount, frequency),
            )
            conn.commit()
            close_db(conn)
            return redirect(url_for("dashboard"))
        return render_template("add_expense.html")
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    """Logs the user out."""
    session.pop("user_id", None)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
