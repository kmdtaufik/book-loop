import customtkinter as ctk
from tkinter import messagebox

class UploadDialog(ctk.CTkToplevel):
    def __init__(self, master, api_client, on_success):
        super().__init__(master)

        self.api_client = api_client
        self.on_success = on_success

        self.title("Smart List Book")
        self.geometry("400x300")

        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="List a Book via ISBN", font=("Roboto", 18, "bold")).grid(row=0, column=0, pady=20)

        self.isbn_entry = ctk.CTkEntry(self, placeholder_text="ISBN (e.g., 978014...)", width=250)
        self.isbn_entry.grid(row=1, column=0, pady=10)

        self.condition_opt = ctk.CTkOptionMenu(self, values=["New", "Like New", "Good", "Fair"])
        self.condition_opt.grid(row=2, column=0, pady=10)

        self.submit_btn = ctk.CTkButton(self, text="Auto-Fetch & List", command=self.submit, fg_color="#2CC985", hover_color="#229C68")
        self.submit_btn.grid(row=3, column=0, pady=20)

        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.grid(row=4, column=0)

    def submit(self):
        isbn = self.isbn_entry.get()
        condition = self.condition_opt.get()

        if not isbn:
            self.status_label.configure(text="Please enter an ISBN", text_color="red")
            return

        self.status_label.configure(text="Fetching data...", text_color="yellow")
        self.submit_btn.configure(state="disabled")

        # Run in main thread for now, ui might freeze slightly but ok for simple client
        success, msg = self.api_client.upload_book(isbn, condition)

        if success:
             messagebox.showinfo("Success", msg)
             self.on_success()
             self.destroy()
        else:
            self.status_label.configure(text=msg, text_color="red")
            self.submit_btn.configure(state="normal")
