import customtkinter as ctk

class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BookLoop", font=("Roboto", 24, "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, text="Browse Books", height=40, width=160, font=("Roboto", 14), corner_radius=8)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, text="My Swaps", height=40, width=160, font=("Roboto", 14), corner_radius=8, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_3 = ctk.CTkButton(self.sidebar_frame, text="Profile", height=40, width=160, font=("Roboto", 14), corner_radius=8, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        # Main Content Area
        self.scrollable_frame = ctk.CTkScrollableFrame(self, label_text="Available Books", label_font=("Roboto", 20, "bold"))
        self.scrollable_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        self.load_books()

    def load_books(self):
        books = self.winfo_toplevel().api.get_books()
        for i, book in enumerate(books):
            card = ctk.CTkFrame(self.scrollable_frame, corner_radius=10, border_width=1, border_color="gray30", bg_color="transparent")
            card.grid(row=i, column=0, padx=10, pady=10, sticky="ew")

            # Use columns inside the card for better layout
            card.grid_columnconfigure(1, weight=1)

            # Simple Icon placeholder (Label)
            icon_label = ctk.CTkLabel(card, text="📖", font=("Arial", 30))
            icon_label.grid(row=0, column=0, rowspan=2, padx=15, pady=15)

            title_label = ctk.CTkLabel(card, text=book["title"], font=("Roboto", 18, "bold"), anchor="w")
            title_label.grid(row=0, column=1, padx=5, pady=(15, 0), sticky="w")

            author_label = ctk.CTkLabel(card, text=f"by {book['author']}", font=("Roboto", 14), text_color="gray70", anchor="w")
            author_label.grid(row=1, column=1, padx=5, pady=(0, 15), sticky="nw")

            status_color = "#2CC985" if book["status"] == "AVAILABLE" else "gray"
            status_label = ctk.CTkLabel(card, text=book["status"], font=("Roboto", 12, "bold"), text_color=status_color)
            status_label.grid(row=0, column=2, padx=20, pady=(15, 0), sticky="e")

            if book["status"] == "AVAILABLE":
                request_btn = ctk.CTkButton(
                    card,
                    text="Request",
                    width=100,
                    height=30,
                    font=("Roboto", 13, "bold"),
                    corner_radius=15,
                    fg_color="#2CC985",
                    hover_color="#229C68",
                    bg_color="transparent"
                )
                request_btn.grid(row=1, column=2, padx=20, pady=(0, 15), sticky="e")
