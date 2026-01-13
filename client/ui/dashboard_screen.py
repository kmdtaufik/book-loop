import customtkinter as ctk
from PIL import Image
import requests
from io import BytesIO
from threading import Thread
from ui.swap_dialog import SwapOfferDialog
from ui.upload_dialog import UploadDialog

class BookCard(ctk.CTkFrame):
    def __init__(self, master, book, user_id, on_swap):
        super().__init__(master, corner_radius=10, border_width=1, border_color="gray30", bg_color="transparent")
        self.book = book
        self.user_id = user_id
        self.on_swap = on_swap

        self.grid_columnconfigure(1, weight=1)

        # Image or Icon
        self.image_label = ctk.CTkLabel(self, text="📖", font=("Arial", 30))
        self.image_label.grid(row=0, column=0, rowspan=2, padx=15, pady=15)

        if book.get("image_url"):
            self.load_image(book["image_url"])

        # Info
        ctk.CTkLabel(self, text=book["title"], font=("Roboto", 18, "bold"), anchor="w").grid(row=0, column=1, padx=5, pady=(15, 0), sticky="w")
        ctk.CTkLabel(self, text=f"by {book['author']}", font=("Roboto", 14), text_color="gray70", anchor="w").grid(row=1, column=1, padx=5, pady=(0, 15), sticky="nw")

        # Button
        if book['owner_id'] != user_id:
            ctk.CTkButton(
                self,
                text="Swap Request",
                command=lambda: self.on_swap(book['id']),
                width=120,
                height=30,
                fg_color="#2CC985",
                hover_color="#229C68"
            ).grid(row=0, column=2, rowspan=2, padx=20, sticky="e")
        else:
             ctk.CTkLabel(self, text="Your Book", text_color="gray").grid(row=0, column=2, rowspan=2, padx=20, sticky="e")

    def load_image(self, url):
        def _load():
            try:
                if not url: return
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    img_data = BytesIO(response.content)
                    pil_img = Image.open(img_data)
                    # Resize locally
                    pil_img = pil_img.resize((50, 75))

                    # Schedule update on main thread, passing PIL image
                    # Check if widget still exists before scheduling
                    if self.winfo_exists():
                        self.after(0, lambda: self.update_image(pil_img))
            except Exception:
                pass # Silently fail for image errors

        Thread(target=_load, daemon=True).start()

    def update_image(self, pil_img):
        # Create CTkImage on MAIN THREAD
        try:
           if not self.winfo_exists(): return
           ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(50, 75))
           self.image_label.configure(image=ctk_img, text="")
        except Exception:
           pass

class OfferCard(ctk.CTkFrame):
    def __init__(self, master, tx, user_id, on_accept, on_ship, on_confirm):
        super().__init__(master, corner_radius=10, border_width=1, border_color="gray30", bg_color="transparent")
        self.tx = tx
        self.user_id = user_id

        self.grid_columnconfigure(1, weight=1)

        # Status Icon
        status_icon = "⏳"
        if tx['status'] == "ACCEPTED": status_icon = "✅"
        elif tx['status'] == "SHIPPED": status_icon = "🚚"
        elif tx['status'] == "COMPLETED": status_icon = "🎉"

        ctk.CTkLabel(self, text=status_icon, font=("Arial", 25)).grid(row=0, column=0, rowspan=2, padx=15)

        # Details
        # We need to handle "Direct Swap" vs "Point Swap" details
        # For now, simplistic view:
        # If I am receiver: "Request for [Book ID]" (Wait, transaction schema has book_id)
        # We need book title possibly? The schema returns IDs.
        # For MVP, we'll just show IDs or "Book #ID".
        # Ideally, backend should expand book details, but let's stick to what we have.

        info_text = f"Swap #{tx['id']} - {tx['status']}\nTarget Book: {tx['book_id']}"
        if tx.get('offered_book_id'):
            info_text += f"\nOffered Book: {tx['offered_book_id']}"

        role = "Outgoing" if tx['receiver_id'] == user_id else "Incoming"
        # Wait, if I am receiver, I REQUESTED the book?
        # Model: receiver_id = person GETTING the book (The requester)
        # giver_id = person GIVING the book (The owner)
        # So "Incoming Offer" means I am the GIVER (someone wants my book).

        if tx['giver_id'] == user_id :
             role = "Incoming Request (You Give)"
        else:
             role = "Outgoing Request (You Get)"

        ctk.CTkLabel(self, text=role, font=("Roboto", 14, "bold"), text_color="gray70", anchor="w").grid(row=0, column=1, sticky="w", padx=5, pady=(10,0))
        ctk.CTkLabel(self, text=info_text, font=("Roboto", 12), text_color="white", anchor="w", justify="left").grid(row=1, column=1, sticky="w", padx=5, pady=(0,10))

        # Actions
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=0, column=2, rowspan=2, padx=10)

        if tx['giver_id'] == user_id:
            # I am the owner, I can ACCEPT request
            if tx['status'] == 'REQUESTED':
                ctk.CTkButton(btn_frame, text="Accept", command=lambda: on_accept(tx['id']), width=80, fg_color="#2CC985", hover_color="#229C68").pack(pady=5)
            elif tx['status'] == 'ACCEPTED':
                 ctk.CTkButton(btn_frame, text="Ship", command=lambda: on_ship(tx['id']), width=80, fg_color="#3B8ED0", hover_color="#36719F").pack(pady=5)

        if tx['receiver_id'] == user_id:
             # I requested it. I can CONFIRM receipt
             if tx['status'] == 'SHIPPED':
                  ctk.CTkButton(btn_frame, text="Confirm", command=lambda: on_confirm(tx['id']), width=80, fg_color="#2CC985", hover_color="#229C68").pack(pady=5)


class DashboardScreen(ctk.CTkFrame):
    def __init__(self, master, api=None, user_id=None):
        super().__init__(master)
        self.api = api
        self.user_id = int(user_id) if user_id is not None else None

        if not self.api and hasattr(master.winfo_toplevel(), 'api'):
             self.api = master.winfo_toplevel().api

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="BookLoop", font=("Roboto", 24, "bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_market = ctk.CTkButton(self.sidebar_frame, text="Marketplace", command=self.show_market, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
        self.btn_market.grid(row=1, column=0, padx=20, pady=10)

        self.btn_library = ctk.CTkButton(self.sidebar_frame, text="My Library", command=self.show_library, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
        self.btn_library.grid(row=2, column=0, padx=20, pady=10)

        self.btn_swaps = ctk.CTkButton(self.sidebar_frame, text="Transactions", command=self.show_offers, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
        self.btn_swaps.grid(row=3, column=0, padx=20, pady=10)

        self.btn_profile = ctk.CTkButton(self.sidebar_frame, text="My Profile", command=self.show_profile, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
        self.btn_profile.grid(row=4, column=0, padx=20, pady=10)

        self.sidebar_button_upload = ctk.CTkButton(self.sidebar_frame, text="+ List Book", command=self.open_upload_dialog_ui, height=40, font=("Roboto", 14, "bold"), fg_color="#2CC985", hover_color="#229C68")
        self.sidebar_button_upload.grid(row=5, column=0, padx=20, pady=20)

        self.logout_button = ctk.CTkButton(self.sidebar_frame, text="Logout", command=self.logout_event, fg_color="transparent", border_width=1, text_color=("red", "red"))
        self.logout_button.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # Main Content
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        self.tabview.add("Marketplace")
        self.tabview.add("My Library")
        self.tabview.add("Incoming Offers")
        self.tabview.add("Profile")

        self.market_frame = ctk.CTkScrollableFrame(self.tabview.tab("Marketplace"))
        self.market_frame.pack(fill="both", expand=True)

        self.library_frame = ctk.CTkScrollableFrame(self.tabview.tab("My Library"))
        self.library_frame.pack(fill="both", expand=True)

        self.offers_frame = ctk.CTkScrollableFrame(self.tabview.tab("Incoming Offers"))
        self.offers_frame.pack(fill="both", expand=True)

        # Profile Tab
        self.profile_frame = ctk.CTkFrame(self.tabview.tab("Profile"), fg_color="transparent")
        self.profile_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.stats_frame = ctk.CTkFrame(self.profile_frame)
        self.stats_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(self.stats_frame, text="Your Stats", font=("Roboto", 18, "bold")).pack(pady=10)
        self.label_listed = ctk.CTkLabel(self.stats_frame, text="Books Listed: -")
        self.label_listed.pack()
        self.label_swapped = ctk.CTkLabel(self.stats_frame, text="Books Received: -")
        self.label_swapped.pack(pady=(0, 10))

        self.edit_frame = ctk.CTkFrame(self.profile_frame)
        self.edit_frame.pack(fill="x", pady=10)
        ctk.CTkLabel(self.edit_frame, text="Edit Profile", font=("Roboto", 18, "bold")).pack(pady=10)

        self.entry_email = ctk.CTkEntry(self.edit_frame, placeholder_text="New Email (Optional)")
        self.entry_email.pack(pady=5)

        # Current Email Label (Initialized in load_data)
        self.label_current_email = ctk.CTkLabel(self.edit_frame, text="Current Email: -", text_color="gray70")
        self.label_current_email.pack(pady=(0, 5))

        self.entry_old_pass = ctk.CTkEntry(self.edit_frame, placeholder_text="Old Password (Required for Password Change)", show="*")
        self.entry_old_pass.pack(pady=5)

        self.entry_pass = ctk.CTkEntry(self.edit_frame, placeholder_text="New Password", show="*")
        self.entry_pass.pack(pady=5)

        ctk.CTkButton(self.edit_frame, text="Update Profile", command=self.update_profile_event, fg_color="#2CC985", hover_color="#229C68").pack(pady=10)

        self.load_data()

    # Navigation Helpers
    def show_market(self): self.tabview.set("Marketplace")
    def show_library(self): self.tabview.set("My Library")
    def show_offers(self): self.tabview.set("Incoming Offers")
    def show_profile(self): self.tabview.set("Profile")

    def load_data(self):
        if not self.api: return
        user = self.api.get_me()
        if user and user != 401:
            self.user_id = int(user['id'])
            self.label_listed.configure(text=f"Books Listed: {user.get('books_listed', 0)}")
            self.label_swapped.configure(text=f"Books Received: {user.get('books_swapped', 0)}")
            self.label_current_email.configure(text=f"Current Email: {user.get('email', '-')}")

        all_books = self.api.get_market_books()
        if all_books == 401:
            self.winfo_toplevel().logout()
            return
        if not isinstance(all_books, list): all_books = []

        market_books = []
        my_books = []
        for b in all_books:
            owner = int(b.get('owner_id', -1))
            if owner != self.user_id:
                if b.get('status') == 'AVAILABLE': market_books.append(b)
            else:
                 my_books.append(b)

        self.my_books = my_books
        self.render_market(market_books)
        self.render_library(self.my_books)

        # Load Swaps
        swaps = self.api.get_my_swaps()
        if isinstance(swaps, list):
             self.render_offers(swaps)

    def update_profile_event(self):
        email = self.entry_email.get()
        password = self.entry_pass.get()
        old_password = self.entry_old_pass.get()

        if not email and not password: return

        # If changing password, require old password
        if password and not old_password:
             from tkinter import messagebox
             messagebox.showerror("Error", "Old Password is required to set a New Password.")
             return

        success, msg = self.api.update_profile(
            email=email if email else None,
            password=password if password else None,
            old_password=old_password if old_password else None
        )

        from tkinter import messagebox
        if success:
            messagebox.showinfo("Success", "Profile updated!")
            self.entry_email.delete(0, 'end')
            self.entry_pass.delete(0, 'end')
            self.entry_old_pass.delete(0, 'end')
            self.load_data() # Refresh to update current email label
        else:
            messagebox.showerror("Error", msg)

    def render_market(self, books):
        for w in self.market_frame.winfo_children(): w.destroy()
        for book in books:
            card = BookCard(self.market_frame, book, self.user_id, self.open_swap_dialog)
            card.pack(fill="x", padx=10, pady=10)

    def render_library(self, books):
        for w in self.library_frame.winfo_children(): w.destroy()
        for book in books:
            card = BookCard(self.library_frame, book, self.user_id, lambda x: None)
            card.pack(fill="x", padx=10, pady=10)

    def render_offers(self, swaps):
        for w in self.offers_frame.winfo_children(): w.destroy()
        if not swaps:
             ctk.CTkLabel(self.offers_frame, text="No active transactions.").pack(pady=20)
             return

        for tx in swaps:
            card = OfferCard(
                self.offers_frame,
                tx,
                self.user_id,
                self.handle_accept,
                self.handle_ship,
                self.handle_confirm
            )
            card.pack(fill="x", padx=10, pady=10)

    def handle_accept(self, tx_id):
         success, msg = self.api.accept_request(tx_id)
         if success: self.load_data()
         else: print(f"Error: {msg}")

    def handle_ship(self, tx_id):
         # Prompt tracking?
         success, msg = self.api.ship_book(tx_id, "TRACK123") # Mock tracking for now
         if success: self.load_data()
         else: print(f"Error: {msg}")

    def handle_confirm(self, tx_id):
         success, msg = self.api.confirm_receipt(tx_id)
         if success: self.load_data()
         else: print(f"Error: {msg}")

    def open_swap_dialog(self, target_book_id):
        # Filter my books to only show AVAILABLE ones for offering
        available_books = [b for b in self.my_books if b.get('status') == 'AVAILABLE']
        if not available_books:
            from tkinter import messagebox
            messagebox.showinfo("No Books", "You don't have any 'AVAILABLE' books to swap! List one first.")
            return

        dialog = SwapOfferDialog(self.winfo_toplevel(), available_books, target_book_id, self.handle_trade_confirm)
        dialog.attributes('-topmost', True)

    def handle_trade_confirm(self, my_id, target_id):
        print(f"Swap Requested: Offering {my_id} for {target_id}")
        success, msg = self.api.request_book(book_id=target_id, offered_book_id=my_id)
        if success:
             print("Request sent.")
             self.tabview.set("Incoming Offers") # Switch to offers tab
             self.load_data()
        else:
             print(f"Server error: {msg}")

    def open_upload_dialog_ui(self):
         try:
             from ui.upload_dialog import UploadDialog
             UploadDialog(self.winfo_toplevel(), self.api, self.load_data)
         except ImportError:
             print("UploadDialog not found or import error")

    def logout_event(self):
         self.winfo_toplevel().logout()
