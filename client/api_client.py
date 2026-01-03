import requests

class BookLoopAPI:
    BASE_URL = "http://localhost:8000"

    def __init__(self):
        self.token = None

    def login(self, username, password):
        """
        Logs in the user and returns (success, message).
        If success is True, message is the token (also stored in self.token).
        If success is False, message is the error description.
        """
        url = f"{self.BASE_URL}/auth/login"
        data = {
            "username": username,
            "password": password
        }
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                self.token = response.json().get("access_token")
                return True, self.token
            else:
                try:
                    detail = response.json().get("detail", "Login failed")
                except:
                    detail = f"Login failed: {response.status_code}"
                return False, detail
        except requests.RequestException as e:
            return False, f"Connection error: {e}"

    def register(self, email, username, password):
        """
        Registers a new user. Returns (success, message).
        """
        url = f"{self.BASE_URL}/auth/register"
        json_data = {
            "email": email,
            "username": username,
            "password": password
        }
        try:
            response = requests.post(url, json=json_data)
            if response.status_code == 200:
                return True, "Registration successful"
            else:
                try:
                    detail = response.json().get("detail", "Registration failed")
                except:
                    detail = f"Registration failed: {response.status_code}"
                return False, detail
        except requests.RequestException as e:
            return False, f"Connection error: {e}"

    def get_books(self):
        """
        Fetches the list of books.
        Since the /books endpoint is not implemented in the backend yet,
        this returns a mock list for demonstration.
        """
        # Mock data (Backend implementation for /books is pending)
        return [
            {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "status": "AVAILABLE"},
            {"title": "1984", "author": "George Orwell", "status": "SWAPPED"},
            {"title": "To Kill a Mockingbird", "author": "Harper Lee", "status": "AVAILABLE"},
            {"title": "The Python Bible", "author": "Ziad", "status": "PENDING"},
             {"title": "Clean Code", "author": "Robert C. Martin", "status": "AVAILABLE"},
        ]
