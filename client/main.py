import customtkinter as ctk
from api_client import BookLoopAPI
from ui.login_screen import LoginScreen
from ui.dashboard_screen import DashboardScreen
from ui.register_screen import RegisterScreen

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BookLoopApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BookLoop Desktop Client")
        self.geometry("1000x600")

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

        # Show Login Screen initially
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

    def on_login_success(self):
        # Create DashboardScreen now that we are logged in
        dashboard_frame = DashboardScreen(self.container)
        self.frames["DashboardScreen"] = dashboard_frame
        dashboard_frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("DashboardScreen")

    def on_go_to_register(self):
        self.show_frame("RegisterScreen")

    def on_register_success(self):
        # Could auto-login or just go back to login screen
        # Let's go back to login screen for now so user can login with new creds
        self.show_frame("LoginScreen")

    def on_back_to_login(self):
        self.show_frame("LoginScreen")

if __name__ == "__main__":
    app = BookLoopApp()
    app.mainloop()
