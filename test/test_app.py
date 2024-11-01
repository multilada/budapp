import unittest
from app import app, get_db_connection, close_db
from flask import url_for
import hashlib


class BudgetingAppTests(unittest.TestCase):

    def setUp(self):
        """Set up the app before each test."""
        app.config["TESTING"] = True
        self.app = app.test_client()
        self.db = get_db_connection()

    def tearDown(self):
        """Teardown the app after each test."""
        close_db(self.db)

    def test_index(self):
        """Test the home page."""
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to Budgeting App", response.data)

    def test_signup_get(self):
        """Test the signup page (GET request)."""
        response = self.app.get("/signup")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sign Up", response.data)

    def test_signup_post(self):
        """Test the signup page (POST request)."""
        username = "testuser"
        password = "testpassword"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        response = self.app.post(
            "/signup", data={"username": username, "password": password}
        )
        self.assertEqual(response.status_code, 302)  # Redirects to login
        self.assertIn(b"login", response.headers["Location"])

        # Check if user is added to the database
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user["password_hash"], password_hash)

    def test_signup_post_existing_user(self):
        """Test signup with an existing username."""
        username = "testuser"
        password = "testpassword"
        self.app.post(
            "/signup", data={"username": username, "password": password}
        )  # Create a user first
        response = self.app.post(
            "/signup", data={"username": username, "password": password}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Username already exists", response.data)

    def test_login_get(self):
        """Test the login page (GET request)."""
        response = self.app.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Log In", response.data)

    def test_login_post_success(self):
        """Test the login page (POST request) with valid credentials."""
        username = "testuser"
        password = "testpassword"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.app.post(
            "/signup", data={"username": username, "password": password}
        )  # Create user first
        response = self.app.post(
            "/login", data={"username": username, "password": password}
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"dashboard", response.headers["Location"])

    def test_login_post_failure(self):
        """Test the login page (POST request) with invalid credentials."""
        response = self.app.post(
            "/login", data={"username": "invaliduser", "password": "invalidpassword"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid username or password", response.data)

    def test_dashboard_logged_in(self):
        """Test the dashboard page (logged in)."""
        username = "testuser"
        password = "testpassword"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.app.post(
            "/signup", data={"username": username, "password": password}
        )  # Create user
        self.app.post(
            "/login", data={"username": username, "password": password}
        )  # Log in
        response = self.app.get("/dashboard")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Your Dashboard", response.data)

    def test_dashboard_not_logged_in(self):
        """Test the dashboard page (not logged in)."""
        response = self.app.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"login", response.headers["Location"])

    def test_add_income_logged_in(self):
        """Test the add income page (logged in)."""
        username = "testuser"
        password = "testpassword"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.app.post(
            "/signup", data={"username": username, "password": password}
        )  # Create user
        self.app.post(
            "/login", data={"username": username, "password": password}
        )  # Log in
        response = self.app.get("/add_income")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add Income", response.data)

    def test_add_income_not_logged_in(self):
        """Test the add income page (not logged in)."""
        response = self.app.get("/add_income")
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"login", response.headers["Location"])

    def test_add_income_post(self):
        """Test adding income (POST request)."""
        username = "testuser"
        password = "testpassword"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.app.post(
            "/signup", data={"username": username, "password": password}
        )  # Create user
        self.app.post(
            "/login", data={"username": username, "password": password}
        )  # Log in
        response = self.app.post(
            "/add_income",
            data={"source": "Salary", "amount": 3000.00, "frequency": "Monthly"},
        )
        self.assertEqual(response.status_code, 302)  # Redirects to dashboard
        self.assertIn(b"dashboard", response.headers["Location"])

        # Check if income is added to the database
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM incomes WHERE source = ?", ("Salary",))
        income = cursor.fetchone()
        self.assertIsNotNone(income)
        self.assertEqual(income["amount"], 3000.00)
        self.assertEqual(income["frequency"], "Monthly")

    def test_add_expense_logged_in(self):
        """Test the add expense page (logged in)."""
        username = "testuser"
        password = "testpassword"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.app.post(
            "/signup", data={"username": username, "password": password}
        )  # Create user
        self.app.post(
            "/login", data={"username": username, "password": password}
        )  # Log in
        response = self.app.get("/add_expense")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add Expense", response.data)

    def test_add_expense_not_logged_in(self):
        """Test the add expense page (not logged in)."""
        response = self.app.get("/add_expense")
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"login", response.headers["Location"])

    def test_add_expense_post(self):
        """Test adding expense (POST request)."""
        username = "testuser"
        password = "testpassword"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.app.post(
            "/signup", data={"username": username, "password": password}
        )  # Create user
        self.app.post(
            "/login", data={"username": username, "password": password}
        )  # Log in
        response = self.app.post(
            "/add_expense",
            data={"category": "Food", "amount": 50.00, "date": "2023-12-12"},
        )
        self.assertEqual(response.status_code, 302)  # Redirects to dashboard
        self.assertIn(b"dashboard", response.headers["Location"])

        # Check if expense is added to the database
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM expenses WHERE category = ?", ("Food",))
        expense = cursor.fetchone()
        self.assertIsNotNone(expense)
        self.assertEqual(expense["amount"], 50.00)
        self.assertEqual(expense["date"], "2023-12-12")

    def test_logout(self):
        """Test the logout route."""
        username = "testuser"
        password = "testpassword"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.app.post(
            "/signup", data={"username": username, "password": password}
        )  # Create user
        self.app.post(
            "/login", data={"username": username, "password": password}
        )  # Log in
        response = self.app.get("/logout")
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"/", response.headers["Location"])  # Redirects to home page


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
