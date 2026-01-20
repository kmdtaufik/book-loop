import customtkinter as ctk
import keyring
import os
import sys
from api_client import BookLoopAPI
from ui.dashboard_screen import DashboardScreen
from ui.login_screen import LoginScreen
from ui.register_screen import RegisterScreen
from ui.swaps_screen import SwapsScreen

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

SERVICE_ID = "BookLoop_Desktop"
USER_KEY = "auth_token"

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(base_path, relative_path)

class BookLoopApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        #app window setup
        self.title("BookLoop Desktop Client")
        self.geometry("1000x600")

        # Set window icon
        try:
            icon_path = resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Failed to load icon: {e}")

        # API Client
        self.api = BookLoopAPI()
        self.token = None

        # Container for screens
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        # Initialize screens
        self.init_frames()

        # Try to load session
        if self.load_session():
            self.show_dashboard()
        else:
            self.show_frame("LoginScreen")

    def init_frames(self):
        # We only create LoginScreen and RegisterScreen initially. Dashboard requires login.
        login_frame = LoginScreen(self.container, self.on_login_success, self.on_go_to_register)
        self.frames["LoginScreen"] = login_frame
        login_frame.grid(row=0, column=0, sticky="nsew")

        register_frame = RegisterScreen(self.container, self.on_register_success, self.on_back_to_login)
        self.frames["RegisterScreen"] = register_frame
        register_frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if page_name == "SwapsScreen" or page_name == "DashboardScreen":
             # Refresh data if possible
             if hasattr(frame, "load_data"):
                 frame.load_data()
            # If dashboard, maybe refresh books.
             if hasattr(frame, "load_books"):
                 frame.load_books()

    def on_login_success(self):
        # Create DashboardScreen now that we are logged in
        dashboard_frame = DashboardScreen(self.container)
        self.frames["DashboardScreen"] = dashboard_frame
        dashboard_frame.grid(row=0, column=0, sticky="nsew")

        # Create SwapsScreen
        swaps_frame = SwapsScreen(self.container)
        self.frames["SwapsScreen"] = swaps_frame
        swaps_frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("DashboardScreen")

    def on_go_to_register(self):
        self.show_frame("RegisterScreen")

    def on_register_success(self):
        # Could auto-login or just go back to login screen
        # Let's go back to login screen for now so user can login with new creds
        self.show_frame("LoginScreen")

    def on_back_to_login(self):
        self.show_frame("LoginScreen")

    def show_swaps(self):
        self.show_frame("SwapsScreen")

    def show_dashboard(self):
        self.show_frame("DashboardScreen")

    def save_session(self, token):
        self.token = token
        self.api.token = token
        try:
            keyring.set_password(SERVICE_ID, USER_KEY, token)
        except Exception as e:
            print(f"Failed to save session: {e}")

    def load_session(self):
        try:
            token = keyring.get_password(SERVICE_ID, USER_KEY)
            if token:
                self.token = token
                self.api.token = token
                # Verify token validity by calling /me
                user = self.api.get_me()
                if user:
                    self.on_login_success() # Setup dashboard frames
                    return True
                else:
                    return False
        except Exception as e:
            print(f"Failed to load session: {e}")
            return False
        return False

    def logout(self):
        try:
            keyring.delete_password(SERVICE_ID, USER_KEY)
        except:
            pass
        self.token = None
        self.api.token = None
        # Clean up frames if needed
        self.show_frame("LoginScreen")

if __name__ == "__main__":
    app = BookLoopApp()
    app.mainloop()
