import customtkinter as ctk
from tkinter import messagebox

class SwapsScreen(ctk.CTkFrame):
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

        self.sidebar_button_1 = ctk.CTkButton(self.sidebar_frame, text="Browse Books", command=self.go_to_browse, height=40, width=160, font=("Roboto", 14), corner_radius=8, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)

        # My Swaps is active here
        self.sidebar_button_2 = ctk.CTkButton(self.sidebar_frame, text="My Swaps", command=self.go_to_swaps, height=40, width=160, font=("Roboto", 14), corner_radius=8)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)

        self.sidebar_button_3 = ctk.CTkButton(self.sidebar_frame, text="Profile", height=40, width=160, font=("Roboto", 14), corner_radius=8, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"))
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)

        # Main Content Area - Tabs
        self.tabview = ctk.CTkTabview(self, width=800, height=500, corner_radius=10)
        self.tabview.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")

        self.tabview.add("Incoming Books")  # Books I requested
        self.tabview.add("Outgoing Books")  # Books others requested from me

        # Configure grid for tabs
        self.tabview.tab("Incoming Books").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Incoming Books").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Outgoing Books").grid_columnconfigure(0, weight=1)
        self.tabview.tab("Outgoing Books").grid_rowconfigure(0, weight=1)

        # Scrollable Frames for lists
        self.incoming_frame = ctk.CTkScrollableFrame(self.tabview.tab("Incoming Books"), label_text="My Requests")
        self.incoming_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.outgoing_frame = ctk.CTkScrollableFrame(self.tabview.tab("Outgoing Books"), label_text="Requests for My Books")
        self.outgoing_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Start loading data
        self.load_data()

    def go_to_browse(self):
        self.winfo_toplevel().show_dashboard()

    def go_to_swaps(self):
        self.winfo_toplevel().show_swaps()

    def load_data(self):
        # Clear existing
        for widget in self.incoming_frame.winfo_children(): widget.destroy()
        for widget in self.outgoing_frame.winfo_children(): widget.destroy()

        # Fetch swaps & user info
        swaps = self.winfo_toplevel().api.get_my_swaps()
        if swaps == 401:
            self.winfo_toplevel().logout()
            return

        user_info = self.winfo_toplevel().api.get_me()
        if user_info == 401:
             self.winfo_toplevel().logout()
             return

        if not user_info:
            return

        my_id = user_info['id']
        self.render_swaps(swaps, my_id)

    def render_swaps(self, swaps, my_id):
        for tx in swaps:
            if tx['receiver_id'] == my_id:
                self.render_incoming_card(tx)
            elif tx['giver_id'] == my_id:
                self.render_outgoing_card(tx)

    def render_incoming_card(self, tx):
        card = ctk.CTkFrame(self.incoming_frame, corner_radius=10, border_width=1, border_color="gray30", bg_color="transparent")
        card.pack(fill="x", padx=10, pady=5)

        info = f"Book ID: {tx['book_id']} | Status: {tx['status']}"
        if tx['tracking_number']:
            info += f" | Tracking: {tx['tracking_number']}"

        label = ctk.CTkLabel(card, text=info, font=("Roboto", 14))
        label.pack(side="left", padx=10, pady=10)

        if tx['status'] == "SHIPPED":
            btn = ctk.CTkButton(card, text="Confirm Receipt", command=lambda t=tx['id']: self.confirm_action(t),
                                font=("Roboto", 12), height=30, bg_color="transparent")
            btn.pack(side="right", padx=10, pady=10)

    def render_outgoing_card(self, tx):
        card = ctk.CTkFrame(self.outgoing_frame, corner_radius=10, border_width=1, border_color="gray30", bg_color="transparent")
        card.pack(fill="x", padx=10, pady=5)

        info = f"Book ID: {tx['book_id']} | Status: {tx['status']}"
        label = ctk.CTkLabel(card, text=info, font=("Roboto", 14))
        label.pack(side="left", padx=10, pady=10)

        if tx['status'] == "REQUESTED":
            btn = ctk.CTkButton(card, text="Accept", command=lambda t=tx['id']: self.accept_action(t),
                                font=("Roboto", 12), height=30, fg_color="#2CC985", hover_color="#229C68", bg_color="transparent")
            btn.pack(side="right", padx=10, pady=10)
        elif tx['status'] == "ACCEPTED":
            btn = ctk.CTkButton(card, text="Ship", command=lambda t=tx['id']: self.ship_action(t),
                                font=("Roboto", 12), height=30, bg_color="transparent")
            btn.pack(side="right", padx=10, pady=10)

    def accept_action(self, tx_id):
        success, msg = self.winfo_toplevel().api.accept_request(tx_id)
        if success: self.show_success("Accepted!")
        else: self.show_error(msg)
        self.load_data()

    def ship_action(self, tx_id):
        dialog = ctk.CTkInputDialog(text="Enter Tracking Number:", title="Ship Book")
        tracking = dialog.get_input()
        if tracking:
            success, msg = self.winfo_toplevel().api.ship_book(tx_id, tracking)
            if success: self.show_success("Shipped!")
            else: self.show_error(msg)
            self.load_data()

    def confirm_action(self, tx_id):
        success, msg = self.winfo_toplevel().api.confirm_receipt(tx_id)
        if success: self.show_success("Confirmed! Points released.")
        else: self.show_error(msg)
        self.load_data()

    def show_error(self, msg):
        messagebox.showerror("Error", msg)

    def show_success(self, msg):
        messagebox.showinfo("Success", msg)
