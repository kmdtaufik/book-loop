import customtkinter as ctk

class RegisterScreen(ctk.CTkFrame):
    def __init__(self, master, on_register_success, on_back_to_login):
        super().__init__(master)
        self.on_register_success = on_register_success
        self.on_back_to_login = on_back_to_login

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=0, padx=20, pady=20)

        self.label = ctk.CTkLabel(self.main_frame, text="Create Account", font=("Roboto", 24, "bold"))
        self.label.pack(pady=(40, 5), padx=40)

        self.sub_label = ctk.CTkLabel(self.main_frame, text="Join the BookLoop Community", font=("Roboto", 14), text_color="gray70")
        self.sub_label.pack(pady=(0, 30), padx=40)

        # Error Label
        self.error_label = ctk.CTkLabel(self.main_frame, text="", text_color="#FF5555", font=("Roboto", 12))
        self.error_label.pack(pady=(0, 10), padx=20)

        self.username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Username", width=300, height=40, font=("Roboto", 14))
        self.username_entry.pack(pady=10, padx=40)

        self.email_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Email Address", width=300, height=40, font=("Roboto", 14))
        self.email_entry.pack(pady=10, padx=40)

        self.password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Password", show="*", width=300, height=40, font=("Roboto", 14))
        self.password_entry.pack(pady=10, padx=40)

        self.register_button = ctk.CTkButton(
            self.main_frame,
            text="Sign Up",
            command=self.register_event,
            width=300,
            height=40,
            font=("Roboto", 15, "bold"),
            corner_radius=20,
            bg_color="transparent"
        )
        self.register_button.pack(pady=(30, 20), padx=40)

        self.back_button = ctk.CTkButton(
            self.main_frame,
            text="Already have an account? Login",
            command=self.on_back_to_login,
            width=300,
            height=30,
            font=("Roboto", 13),
            fg_color="transparent",
            hover_color=("gray85", "gray25"),
            text_color=("gray10", "gray90")
        )
        self.back_button.pack(pady=(0, 30), padx=40)

    def register_event(self):
        email = self.email_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Validation
        if not email or not username or not password:
            self.error_label.configure(text="Please fill in all fields", text_color="#FF5555")
            return

        if len(password) < 8:
            self.error_label.configure(text="Password must be at least 8 characters", text_color="#FF5555")
            return

        self.error_label.configure(text="Registering...", text_color="white")

        # Call API
        success, message = self.winfo_toplevel().api.register(email, username, password)

        if success:
            self.error_label.configure(text="")
            # Optionally clear fields
            self.email_entry.delete(0, "end")
            self.username_entry.delete(0, "end")
            self.password_entry.delete(0, "end")
            self.on_register_success()
        else:
            self.error_label.configure(text=message, text_color="#FF5555")
