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

    def upload_book(self, isbn, condition):
        """
        Uploads a book using Smart Upload (ISBN only).
        """
        url = f"{self.BASE_URL}/books/"
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "isbn": isbn,
            "condition": condition
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return True, "Book listed successfully!"
            elif response.status_code == 404:
                return False, "Book not found."
            elif response.status_code == 401:
                return False, "Unauthorized"
            else:
                return False, f"Error: {response.text}"
        except requests.RequestException as e:
            return False, f"Connection error: {e}"

    def get_books(self):
        """
        Fetches all books. Returns a list of dicts.
        """
        url = f"{self.BASE_URL}/books"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return 401
            else:
                return []
        except requests.RequestException:
            return []

    def get_me(self):
        """Fetches current user info"""
        if not self.token: return None
        url = f"{self.BASE_URL}/auth/me"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
           response = requests.get(url, headers=headers)
           if response.status_code == 200:
               return response.json()
           elif response.status_code == 401:
               return 401 # Signal to logout
           return None
        except:
           return None

    def update_profile(self, email=None, password=None, old_password=None):
        """Updates user profile (email/password)"""
        url = f"{self.BASE_URL}/auth/me"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {}
        if email: data["email"] = email
        if password: data["password"] = password
        if old_password: data["old_password"] = old_password

        try:
            response = requests.put(url, json=data, headers=headers)
            if response.status_code == 200:
                return True, "Profile updated successfully"
            else:
                 try: detail = response.json().get("detail", "Update failed")
                 except: detail = f"Update failed: {response.status_code}"
                 return False, detail
        except requests.RequestException as e:
            return False, str(e)

    def get_my_swaps(self):
        """
        Fetches user's transactions (incoming & outgoing).
        """
        if not self.token: return []
        url = f"{self.BASE_URL}/transactions/my-swaps"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return 401
            return []
        except requests.RequestException:
            return []

    def request_book(self, book_id, offered_book_id=None):
        """Returns (success, message)"""
        url = f"{self.BASE_URL}/transactions/request"
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"book_id": book_id}
        if offered_book_id:
            payload["offered_book_id"] = offered_book_id

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return True, "Request sent successfully"
            else:
                try: detail = response.json().get("detail", "Request failed")
                except: detail = f"Request failed: {response.status_code}"
                return False, detail
        except requests.RequestException as e:
            return False, str(e)

    def accept_request(self, tx_id):
        """Returns (success, message)"""
        url = f"{self.BASE_URL}/transactions/{tx_id}/accept"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.put(url, headers=headers)
            if response.status_code == 200:
                return True, "Request accepted"
            else:
                return False, response.text
        except requests.RequestException as e:
            return False, str(e)

    def ship_book(self, tx_id, tracking_number):
        """Returns (success, message)"""
        url = f"{self.BASE_URL}/transactions/{tx_id}/ship"
        headers = {"Authorization": f"Bearer {self.token}"}
        data = {"tracking_number": tracking_number}
        try:
            response = requests.put(url, json=data, headers=headers)
            if response.status_code == 200:
                return True, "Book marked as shipped"
            else:
                return False, response.text
        except requests.RequestException as e:
            return False, str(e)

    def confirm_receipt(self, tx_id):
        """Returns (success, message)"""
        url = f"{self.BASE_URL}/transactions/{tx_id}/confirm"
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.put(url, headers=headers)
            if response.status_code == 200:
                return True, "Receipt confirmed"
            else:
                return False, response.text
        except requests.RequestException as e:
            return False, str(e)

    def get_market_books(self):
        """
        Fetches all available books. (Filtering happens in UI)
        """
        return self.get_books()

    def get_my_available_books(self):
        """
        Fetches available books. (Filtering happens in UI)
        """
        return self.get_books()

    def get_market_books(self):
        """
        Fetches all available books. (Filtering happens in UI)
        """
        return self.get_books()

    def get_my_available_books(self):
        """
        Fetches available books. (Filtering happens in UI)
        """
        return self.get_books()
