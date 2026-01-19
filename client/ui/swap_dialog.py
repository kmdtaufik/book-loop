import customtkinter as ctk

class SwapOfferDialog(ctk.CTkToplevel):
    def __init__(self, master, my_books, target_book_id, on_confirm):
        super().__init__(master)
        self.title("Make an Offer")
        self.geometry("400x300")

        self.my_books = my_books
        self.target_book_id = target_book_id
        self.on_confirm = on_confirm

        self.label = ctk.CTkLabel(self, text="Select a book to offer:", font=("Roboto", 16, "bold"))
        self.label.pack(pady=20)

        if not my_books:
            ctk.CTkLabel(self, text="You have no available books to trade.").pack(pady=10)
            return

        # Create book titles list for dropdown
        self.book_map = {f"{b['title']} (ID: {b['id']})": b['id'] for b in my_books}
        self.book_titles = list(self.book_map.keys())

        self.option_menu = ctk.CTkOptionMenu(self, values=self.book_titles, width=250)
        self.option_menu.pack(pady=10)

        self.confirm_btn = ctk.CTkButton(self, text="Confirm Trade", command=self.confirm_trade, fg_color="#2CC985", hover_color="#229C68")
        self.confirm_btn.pack(pady=20)

    def confirm_trade(self):
        selected_title = self.option_menu.get()
        my_book_id = self.book_map[selected_title]

        # Logic: Just print for now as requested
        print(f"[BARTER] Trading My Book ID {my_book_id} for Target Book ID {self.target_book_id}")

        if self.on_confirm:
            self.on_confirm(my_book_id, self.target_book_id)

        self.destroy()
