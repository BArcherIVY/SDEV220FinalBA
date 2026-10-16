
import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


# Rounds money to two decimal places
def money(value):
    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


# Creates the cash register window and handles the shopping cart
class RegisterGUI:
    def __init__(self, parent, inventory, register, on_update):
        self.inventory = inventory
        self.register = register
        self.on_update = on_update

        self.cart = {}
        self.selected_item = None
        self.matching_items = []

        self.window = tk.Toplevel(parent)
        self.window.title("Disc Replay - Cash Register")

        self.window.state("zoomed")

        # Sets up the colors and styles for the register window
        background = "#F3F5F9"
        surface = "#FFFFFF"
        text_color = "#1F2937"
        accent = "#2563EB"

        self.window.configure(bg=background)

        style = ttk.Style(self.window)

        style.configure(
            "RegisterSurface.TFrame",
            background=surface
        )

        style.configure(
            "RegisterSurface.TLabel",
            background=surface,
            foreground=text_color,
            font=("Segoe UI", 10)
        )

        style.configure(
            "RegisterTotal.TLabel",
            background=background,
            foreground=accent,
            font=("Segoe UI", 19, "bold")
        )

        style.configure(
            "RegisterChange.TLabel",
            background=surface,
            foreground=text_color,
            font=("Segoe UI", 14, "bold")
        )

        style.configure(
            "RegisterStats.TLabel",
            background=background,
            foreground=text_color,
            font=("Segoe UI", 11, "bold")
        )

        style.configure(
            "RegisterQuantity.TLabel",
            background=surface,
            foreground=text_color,
            font=("Segoe UI", 16, "bold")
        )

        ttk.Label(
            self.window,
            text="Disc Replay Cash Register",
            style="Header.TLabel"
        ).pack(pady=(18, 12))

        # Creates the payment section at the bottom of the window
        bottom_frame = ttk.Frame(self.window)
        bottom_frame.pack(
            side="bottom",
            fill="x",
            padx=18,
            pady=(7, 14)
        )

        self.total_label = ttk.Label(
            bottom_frame,
            text="Sale Total: $0.00",
            style="RegisterTotal.TLabel"
        )
        self.total_label.pack(pady=(5, 10))

        payment_frame = ttk.LabelFrame(
            bottom_frame,
            text="Cash Payment"
        )
        payment_frame.pack(
            fill="x",
            pady=5
        )

        payment_controls = ttk.Frame(
            payment_frame,
            style="RegisterSurface.TFrame"
        )
        payment_controls.pack(pady=8)

        ttk.Label(
            payment_controls,
            text="Cash Received: $",
            style="RegisterSurface.TLabel"
        ).pack(side="left", padx=6)

        self.cash_var = tk.StringVar()

        self.cash_entry = ttk.Entry(
            payment_controls,
            textvariable=self.cash_var,
            width=16
        )
        self.cash_entry.pack(side="left", padx=6)

        self.cash_var.trace_add(
            "write",
            self.update_change
        )

        self.change_label = ttk.Label(
            payment_frame,
            text="Change Due: $0.00",
            style="RegisterChange.TLabel"
        )
        self.change_label.pack(pady=(3, 10))

        # Displays the current till amount and daily sales
        totals_frame = ttk.Frame(bottom_frame)
        totals_frame.pack(pady=8)

        self.till_label = ttk.Label(
            totals_frame,
            style="RegisterStats.TLabel"
        )
        self.till_label.pack(side="left", padx=18)

        self.sales_label = ttk.Label(
            totals_frame,
            style="RegisterStats.TLabel"
        )
        self.sales_label.pack(side="left", padx=18)

        button_frame = ttk.Frame(bottom_frame)
        button_frame.pack(pady=8)

        ttk.Button(
            button_frame,
            text="Complete Sale",
            command=self.complete_sale,
            style="Accent.TButton"
        ).pack(side="left", padx=8)

        ttk.Button(
            button_frame,
            text="Close Register",
            command=self.close_register
        ).pack(side="left", padx=8)

        # Creates the product search field
        search_frame = ttk.LabelFrame(
            self.window,
            text="Search Products"
        )
        search_frame.pack(
            padx=18,
            pady=7,
            fill="x"
        )

        ttk.Label(
            search_frame,
            text="Start typing a movie or game title:",
            style="RegisterSurface.TLabel"
        ).pack(pady=(10, 4))

        self.search_var = tk.StringVar()

        self.search_entry = ttk.Entry(
            search_frame,
            textvariable=self.search_var
        )
        self.search_entry.pack(
            padx=14,
            pady=6,
            fill="x"
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self.search_products
        )
        self.search_entry.bind(
            "<Down>",
            self.focus_results
        )

        # Shows matching products as the user types
        self.results_frame = ttk.Frame(
            search_frame,
            style="RegisterSurface.TFrame"
        )
        self.results_frame.pack(
            padx=14,
            fill="x"
        )

        self.results_list = tk.Listbox(
            self.results_frame,
            height=4,
            font=("Segoe UI", 10),
            exportselection=False,
            background=surface,
            foreground=text_color,
            selectbackground=accent,
            selectforeground="#FFFFFF",
            borderwidth=1,
            relief="solid",
            highlightthickness=0,
            activestyle="none"
        )

        self.results_scrollbar = ttk.Scrollbar(
            self.results_frame,
            orient="vertical",
            command=self.results_list.yview
        )

        self.results_list.config(
            yscrollcommand=self.results_scrollbar.set
        )

        self.results_list.bind(
            "<<ListboxSelect>>",
            self.select_product
        )
        self.results_list.bind(
            "<Return>",
            self.select_product
        )

        self.results_visible = False

        # Displays the stock and price of the selected product
        info_frame = ttk.Frame(
            search_frame,
            style="RegisterSurface.TFrame"
        )
        info_frame.pack(pady=(8, 12))

        self.stock_label = ttk.Label(
            info_frame,
            text="Available Stock: 0",
            style="RegisterSurface.TLabel"
        )
        self.stock_label.pack(side="left", padx=14)

        self.price_label = ttk.Label(
            info_frame,
            text="Unit Price: $0.00",
            style="RegisterSurface.TLabel",
            font=("Segoe UI", 10, "bold")
        )
        self.price_label.pack(side="left", padx=14)

        # Creates the quantity buttons and Add to Cart button
        quantity_frame = ttk.LabelFrame(
            self.window,
            text="Quantity to Add"
        )
        quantity_frame.pack(
            padx=18,
            pady=7,
            fill="x"
        )

        controls = ttk.Frame(
            quantity_frame,
            style="RegisterSurface.TFrame"
        )
        controls.pack(pady=10)

        self.quantity_var = tk.IntVar(value=1)

        ttk.Button(
            controls,
            text="-",
            width=4,
            command=self.decrease_quantity
        ).grid(row=0, column=0, padx=6)

        ttk.Label(
            controls,
            textvariable=self.quantity_var,
            style="RegisterQuantity.TLabel"
        ).grid(row=0, column=1, padx=10)

        ttk.Button(
            controls,
            text="+",
            width=4,
            command=self.increase_quantity
        ).grid(row=0, column=2, padx=6)

        ttk.Button(
            controls,
            text="Add to Cart",
            command=self.add_to_cart,
            style="Accent.TButton"
        ).grid(row=0, column=3, padx=12)

        # Creates the shopping cart table and its controls
        cart_frame = ttk.LabelFrame(
            self.window,
            text="Current Sale / Shopping Cart"
        )
        cart_frame.pack(
            padx=18,
            pady=7,
            fill="both",
            expand=True
        )

        cart_buttons = ttk.Frame(
            cart_frame,
            style="RegisterSurface.TFrame"
        )
        cart_buttons.pack(
            side="bottom",
            pady=10
        )

        ttk.Button(
            cart_buttons,
            text="Remove Selected",
            command=self.remove_selected
        ).pack(side="left", padx=8)

        ttk.Button(
            cart_buttons,
            text="Clear Cart",
            command=self.clear_cart
        ).pack(side="left", padx=8)

        self.cart_table = ttk.Treeview(
            cart_frame,
            columns=("Item", "Qty", "Price", "Subtotal"),
            show="headings",
            height=5,
            selectmode="browse"
        )

        columns = [
            ("Item", 190),
            ("Qty", 50),
            ("Price", 75),
            ("Subtotal", 85)
        ]

        for name, column_width in columns:
            self.cart_table.heading(name, text=name)
            self.cart_table.column(
                name,
                width=column_width,
                minwidth=45,
                stretch=True,
                anchor="w" if name == "Item" else "center"
            )

        cart_scrollbar = ttk.Scrollbar(
            cart_frame,
            orient="vertical",
            command=self.cart_table.yview
        )

        self.cart_table.configure(
            yscrollcommand=cart_scrollbar.set
        )

        cart_scrollbar.pack(
            side="right",
            fill="y",
            pady=8,
            padx=(0, 8)
        )

        self.cart_table.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.refresh_items()
        self.refresh_cart()
        self.refresh_register()
        self.search_entry.focus_set()

    # Uses the title and format together to identify each product
    def item_key(self, item):
        return (item.title, item.type)

    # Reloads the available products and resets the search fields
    def refresh_items(self):
        self.items = self.inventory.view_inventory()
        self.selected_item = None
        self.matching_items = []

        self.search_var.set("")
        self.quantity_var.set(1)
        self.hide_results()

        self.stock_label.config(
            text="Available Stock: 0"
        )
        self.price_label.config(
            text="Unit Price: $0.00"
        )

    # Shows or hides the matching product list
    def show_results(self):
        if not self.results_visible:
            self.results_list.pack(
                side="left",
                fill="both",
                expand=True
            )
            self.results_scrollbar.pack(
                side="right",
                fill="y"
            )
            self.results_visible = True

    def hide_results(self):
        self.results_list.pack_forget()
        self.results_scrollbar.pack_forget()
        self.results_visible = False

    # Searches inventory for titles that match what the user types
    def search_products(self, event=None):
        search_text = self.search_var.get().strip().lower()
        self.selected_item = None

        self.stock_label.config(
            text="Select a product to see stock"
        )
        self.price_label.config(
            text="Unit Price: $0.00"
        )

        self.results_list.delete(0, tk.END)
        self.matching_items = []

        if not search_text:
            self.hide_results()
            return

        self.items = self.inventory.view_inventory()

        for item in self.items:
            if item.title.lower().startswith(search_text):
                self.matching_items.append(item)
                self.results_list.insert(
                    tk.END,
                    f"{item.title} ({item.type})"
                )

        if self.matching_items:
            self.show_results()
        else:
            self.hide_results()

    # Lets the user move from the search box to the results with the arrow key
    def focus_results(self, event=None):
        if self.results_visible and self.matching_items:
            self.results_list.focus_set()
            self.results_list.selection_clear(0, tk.END)
            self.results_list.selection_set(0)
            self.results_list.activate(0)
            return "break"

    # Selects a product from the search results
    def select_product(self, event=None):
        selection = self.results_list.curselection()

        if not selection:
            return

        index = selection[0]

        if index >= len(self.matching_items):
            return

        self.selected_item = self.matching_items[index]

        self.search_var.set(
            f"{self.selected_item.title} ({self.selected_item.type})"
        )

        self.hide_results()
        self.update_item_details()
        self.search_entry.focus_set()

    def get_selected_item(self):
        return self.selected_item

    # Updates the available stock and price for the selected product
    def update_item_details(self):
        item = self.get_selected_item()

        if item is None:
            return

        available = item.quantity - self.cart.get(
            self.item_key(item), 0
        )

        self.stock_label.config(
            text=f"Available to Add: {available}"
        )
        self.price_label.config(
            text=f"Unit Price: ${item.price:.2f}"
        )
        self.quantity_var.set(1)

    # Keeps the quantity within the available stock amount
    def increase_quantity(self):
        item = self.get_selected_item()

        if item is None:
            return

        available = item.quantity - self.cart.get(
            self.item_key(item), 0
        )

        if self.quantity_var.get() < available:
            self.quantity_var.set(
                self.quantity_var.get() + 1
            )

    def decrease_quantity(self):
        if self.quantity_var.get() > 1:
            self.quantity_var.set(
                self.quantity_var.get() - 1
            )

    # Adds the selected product to the cart if enough stock is available
    def add_to_cart(self):
        item = self.get_selected_item()

        if item is None:
            messagebox.showerror(
                "Error",
                "Search for and select a product first.",
                parent=self.window
            )
            return

        quantity = self.quantity_var.get()
        key = self.item_key(item)
        already_added = self.cart.get(key, 0)

        if quantity <= 0:
            messagebox.showerror(
                "Error",
                "Quantity must be greater than zero.",
                parent=self.window
            )
            return

        if already_added + quantity > item.quantity:
            messagebox.showerror(
                "Error",
                "Not enough stock available.",
                parent=self.window
            )
            return

        self.cart[key] = already_added + quantity
        self.refresh_cart()

        self.selected_item = None
        self.search_var.set("")
        self.hide_results()
        self.quantity_var.set(1)

        self.stock_label.config(
            text="Available Stock: 0"
        )
        self.price_label.config(
            text="Unit Price: $0.00"
        )

        self.search_entry.focus_set()

    # Calculates the total price of everything in the cart
    def get_cart_total(self):
        total = Decimal("0.00")

        for (title, item_type), quantity in self.cart.items():
            item = self.inventory.search_item(title, item_type)

            if item is not None:
                total += money(item.price) * quantity

        return total.quantize(Decimal("0.01"))

    # Updates the cart table, total price, and change due
    def refresh_cart(self):
        for row in self.cart_table.get_children():
            self.cart_table.delete(row)

        for index, ((title, item_type), quantity) in enumerate(
            self.cart.items()
        ):
            item = self.inventory.search_item(title, item_type)

            if item is None:
                continue

            subtotal = money(item.price) * quantity

            self.cart_table.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    f"{item.title} ({item.type})",
                    quantity,
                    f"${item.price:.2f}",
                    f"${subtotal:.2f}"
                )
            )

        self.total_label.config(
            text=f"Sale Total: ${self.get_cart_total():.2f}"
        )
        self.update_change()

    # Removes the selected product from the cart
    def remove_selected(self):
        selection = self.cart_table.selection()

        if not selection:
            messagebox.showerror(
                "Error",
                "Select an item in the cart first.",
                parent=self.window
            )
            return

        row_id = selection[0]
        row_index = int(row_id)
        keys = list(self.cart.keys())

        if row_index < len(keys):
            self.cart.pop(keys[row_index], None)

        self.refresh_cart()

        if self.selected_item is not None:
            self.update_item_details()

    # Empties the cart without changing the inventory
    def clear_cart(self):
        self.cart.clear()
        self.refresh_cart()

        if self.selected_item is not None:
            self.update_item_details()

    # Calculates the customer's change or shows how much is still owed
    def update_change(self, *args):
        total = self.get_cart_total()
        entered = self.cash_var.get().strip()

        if not entered:
            self.change_label.config(
                text="Change Due: $0.00"
            )
            return

        try:
            cash = money(entered)
        except (InvalidOperation, ValueError):
            self.change_label.config(
                text="Enter a valid cash amount"
            )
            return

        if not cash.is_finite() or cash < 0:
            self.change_label.config(
                text="Enter a valid cash amount"
            )

        elif cash < total:
            shortage = total - cash
            self.change_label.config(
                text=f"Amount Still Owed: ${shortage:.2f}"
            )

        else:
            change = cash - total
            self.change_label.config(
                text=f"Change Due: ${change:.2f}"
            )

    # Refreshes the current till and daily sales amounts
    def refresh_register(self):
        self.till_label.config(
            text=f"Current Till: ${self.register.current_till:.2f}"
        )
        self.sales_label.config(
            text=f"Daily Sales: ${self.register.daily_sales:.2f}"
        )

    # Processes the payment and updates the inventory after a successful sale
    def complete_sale(self):
        if not self.cart:
            messagebox.showerror(
                "Error",
                "Add at least one product to the cart.",
                parent=self.window
            )
            return

        cash_received = self.cash_var.get().strip()

        success, message = self.register.complete_cart_sale(
            self.cart,
            cash_received
        )

        if not success:
            messagebox.showerror(
                "Payment Error",
                message,
                parent=self.window
            )
            return

        self.cart.clear()
        self.cash_var.set("")

        self.refresh_cart()
        self.refresh_items()
        self.refresh_register()
        self.on_update()

        messagebox.showinfo(
            "Sale Completed",
            message,
            parent=self.window
        )

        self.search_entry.focus_set()

    # Closes out the day's sales and resets the register to $150
    def close_register(self):
        if self.cart:
            messagebox.showerror(
                "Cart Not Empty",
                "Complete the sale or clear the cart first.",
                parent=self.window
            )
            return

        confirm = messagebox.askyesno(
            "Close Register",
            "Close the register and reset the till to $150?",
            parent=self.window
        )

        if not confirm:
            return

        total = self.register.close_register()

        self.cash_var.set("")
        self.refresh_register()
        self.on_update()

        messagebox.showinfo(
            "Register Closed",
            f"Total Daily Sales: ${total:.2f}\n"
            "Register reset to $150.00.",
            parent=self.window
        )
