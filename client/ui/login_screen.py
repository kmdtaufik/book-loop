import customtkinter as ctk

class LoginScreen(ctk.CTkFrame):
    def __init__(self, master, on_login_success, on_go_to_register):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.on_go_to_register = on_go_to_register

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Main Frame with slight background distinction or just centered
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20)

        # Header
        self.label = ctk.CTkLabel(self.main_frame, text="Welcome Back", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(40, 5), padx=40)

        self.sub_label = ctk.CTkLabel(self.main_frame, text="Sign in to BookLoop", font=("Roboto", 14), text_color="gray70")
        self.sub_label.pack(pady=(0, 30), padx=40)

        # Error Label
        self.error_label = ctk.CTkLabel(self.main_frame, text="", text_color="navajo white", font=("Roboto", 12))
        self.error_label.pack(pady=(0, 10), padx=20)

        # Inputs
        self.email_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Email Address", width=300, height=40, font=("Roboto", 14))
        self.email_entry.pack(pady=10, padx=40)

        self.password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Password", show="*", width=300, height=40, font=("Roboto", 14))
        self.password_entry.pack(pady=10, padx=40)

        # Primary Action
        self.login_button = ctk.CTkButton(
            self.main_frame,
            text="Login",
            command=self.login_event,
            width=300,
            height=40,
            font=("Roboto", 15, "bold"),
            corner_radius=20,
            bg_color="transparent"
        )
        self.login_button.pack(pady=(30, 20), padx=40)

        # Divider or spacing

        # Secondary Action
        self.register_button = ctk.CTkButton(
            self.main_frame,
            text="Create an Account",
            command=self.on_go_to_register,
            width=300,
            height=30,
            font=("Roboto", 13),
            fg_color="transparent",
            hover_color=("gray85", "gray25"),
            text_color=("gray10", "gray90")
        )
        self.register_button.pack(pady=(0, 30), padx=40)

    def login_event(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            self.error_label.configure(text="Please fill in all fields", text_color="#FF5555")
            return

        self.error_label.configure(text="Logging in...", text_color="white")

        # Call the API via the master app controller
        success, message = self.winfo_toplevel().api.login(email, password)
        if success:
             self.error_label.configure(text="")
             self.on_login_success()
        else:
            self.error_label.configure(text=message, text_color="#FF5555")
