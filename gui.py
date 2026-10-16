
import tkinter as tk
from tkinter import ttk, messagebox
import math

from inventory import Inventory
from register import Register
from register_gui import RegisterGUI
from sales_history_gui import SalesHistoryGUI


# Sets the colors and styles used throughout the main window
def apply_theme(root):
    style = ttk.Style(root)
    style.theme_use("clam")

    background = "#F3F5F9"
    surface = "#FFFFFF"
    accent = "#2563EB"
    accent_hover = "#1D4ED8"
    text = "#1F2937"
    muted = "#64748B"
    border = "#DCE3EC"

    root.configure(bg=background)

    style.configure(
        ".",
        font=("Segoe UI", 10),
        background=background,
        foreground=text
    )

    style.configure("TFrame", background=background)

    style.configure(
        "TLabel",
        background=background,
        foreground=text,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Header.TLabel",
        background=background,
        foreground=text,
        font=("Segoe UI", 21, "bold")
    )

    style.configure(
        "Stats.TLabel",
        background=surface,
        foreground=text,
        font=("Segoe UI", 12, "bold")
    )

    style.configure(
        "TLabelframe",
        background=surface,
        bordercolor=border,
        borderwidth=1,
        relief="solid"
    )

    style.configure(
        "TLabelframe.Label",
        background=surface,
        foreground=text,
        font=("Segoe UI", 11, "bold"),
        padding=(6, 4)
    )

    style.configure(
        "TEntry",
        fieldbackground=surface,
        foreground=text,
        bordercolor=border,
        lightcolor=border,
        darkcolor=border,
        padding=7
    )

    style.map(
        "TEntry",
        bordercolor=[("focus", accent)]
    )

    style.configure(
        "TButton",
        font=("Segoe UI", 10),
        padding=(14, 9),
        background="#E8EDF5",
        foreground=text,
        borderwidth=0,
        relief="flat"
    )

    style.map(
        "TButton",
        background=[
            ("pressed", "#CBD5E1"),
            ("active", "#DCE5F1")
        ],
        foreground=[("disabled", muted)]
    )

    style.configure(
        "Accent.TButton",
        background=accent,
        foreground="#FFFFFF",
        font=("Segoe UI", 10, "bold"),
        padding=(14, 9),
        borderwidth=0
    )

    style.map(
        "Accent.TButton",
        background=[
            ("pressed", "#1E40AF"),
            ("active", accent_hover)
        ],
        foreground=[
            ("active", "#FFFFFF"),
            ("pressed", "#FFFFFF")
        ]
    )

    style.configure(
        "Danger.TButton",
        background="#DC2626",
        foreground="#FFFFFF",
        font=("Segoe UI", 10, "bold"),
        padding=(14, 9),
        borderwidth=0
    )

    style.map(
        "Danger.TButton",
        background=[
            ("pressed", "#991B1B"),
            ("active", "#B91C1C")
        ],
        foreground=[
            ("active", "#FFFFFF"),
            ("pressed", "#FFFFFF")
        ]
    )

    style.configure(
        "Treeview",
        background=surface,
        fieldbackground=surface,
        foreground=text,
        rowheight=32,
        font=("Segoe UI", 10),
        borderwidth=0
    )

    style.map(
        "Treeview",
        background=[("selected", accent)],
        foreground=[("selected", "#FFFFFF")]
    )

    style.configure(
        "Treeview.Heading",
        background="#E8EDF5",
        foreground=text,
        font=("Segoe UI", 10, "bold"),
        padding=(8, 9),
        relief="flat"
    )

    style.map(
        "Treeview.Heading",
        background=[("active", "#DCE5F1")]
    )

    style.configure(
        "TScrollbar",
        background="#CBD5E1",
        troughcolor=background,
        borderwidth=0,
        arrowsize=13
    )


# Builds the main inventory window and connects it to the other parts of the program
class InventoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Disc Replay Inventory System")
        self.root.state("zoomed")

        apply_theme(self.root)

        self.inventory = Inventory()
        self.register = Register(self.inventory)

        self.register_window = None
        self.history_window = None

        self.updating_fields = False

        ttk.Label(
            root,
            text="Disc Replay Inventory System",
            style="Header.TLabel"
        ).pack(pady=(18, 12))

        # Creates the table that displays all inventory items
        table_frame = ttk.LabelFrame(
            root,
            text="Current Inventory"
        )
        table_frame.pack(
            padx=18,
            pady=7,
            fill="both",
            expand=True
        )

        self.inventory_table = ttk.Treeview(
            table_frame,
            columns=(
                "Title",
                "Category",
                "Type",
                "Price",
                "Quantity"
            ),
            show="headings",
            selectmode="browse"
        )

        columns = [
            ("Title", 200),
            ("Category", 100),
            ("Type", 100),
            ("Price", 75),
            ("Quantity", 75)
        ]

        for name, width in columns:
            self.inventory_table.heading(
                name,
                text=name,
                anchor="center"
            )
            self.inventory_table.column(
                name,
                width=width,
                minwidth=55,
                stretch=True,
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.inventory_table.yview
        )

        self.inventory_table.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y",
            pady=8,
            padx=(0, 8)
        )

        self.inventory_table.pack(
            side="left",
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.inventory_table.bind(
            "<<TreeviewSelect>>",
            self.select_item
        )

        # Creates the input fields for adding or editing inventory items
        details_frame = ttk.LabelFrame(
            root,
            text="Item Details"
        )
        details_frame.pack(
            padx=18,
            pady=7,
            fill="x"
        )

        self.title_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.type_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.quantity_var = tk.StringVar()

        fields = [
            ("Title", self.title_var),
            ("Category", self.category_var),
            ("Type", self.type_var),
            ("Price", self.price_var),
            ("Quantity", self.quantity_var)
        ]

        for index, (label, variable) in enumerate(fields):
            row_number = index // 2
            column_number = index % 2

            ttk.Label(
                details_frame,
                text=label,
                background="#FFFFFF"
            ).grid(
                row=row_number * 2,
                column=column_number,
                padx=12,
                pady=(7, 0),
                sticky="w"
            )

            ttk.Entry(
                details_frame,
                textvariable=variable
            ).grid(
                row=row_number * 2 + 1,
                column=column_number,
                padx=12,
                pady=(2, 7),
                sticky="ew"
            )

        details_frame.columnconfigure(0, weight=1)
        details_frame.columnconfigure(1, weight=1)

        # Searches the inventory automatically as the title is typed
        self.title_var.trace_add(
            "write",
            self.filter_inventory
        )

        # Creates the buttons for managing inventory
        button_frame = ttk.LabelFrame(
            root,
            text="Inventory Controls"
        )
        button_frame.pack(
            padx=18,
            pady=7,
            fill="x"
        )

        buttons = [
            ("Add Item", self.add_item),
            ("Remove Item", self.remove_item),
            ("Update Quantity", self.update_quantity),
            ("Update Price", self.update_price),
            ("Clear Fields", self.clear_fields)
        ]

        for index, (button_text, command) in enumerate(buttons):
            row_number = index // 3
            column_number = index % 3

            if button_text == "Add Item":
                button_style = "Accent.TButton"
            elif button_text == "Clear Fields":
                button_style = "Danger.TButton"
            else:
                button_style = "TButton"

            column_span = (
                2 if button_text == "Clear Fields" else 1
            )

            ttk.Button(
                button_frame,
                text=button_text,
                command=command,
                style=button_style
            ).grid(
                row=row_number,
                column=column_number,
                columnspan=column_span,
                padx=8,
                pady=8,
                sticky="ew"
            )

        for column in range(3):
            button_frame.columnconfigure(column, weight=1)

        # Shows the current till balance and daily sales
        register_frame = ttk.LabelFrame(
            root,
            text="Cash Register"
        )
        register_frame.pack(
            padx=18,
            pady=(7, 14),
            fill="x"
        )

        self.till_label = ttk.Label(
            register_frame,
            text="Current Till: $150.00",
            style="Stats.TLabel"
        )
        self.till_label.grid(
            row=0,
            column=0,
            padx=14,
            pady=10,
            sticky="w"
        )

        self.sales_label = ttk.Label(
            register_frame,
            text="Daily Sales: $0.00",
            style="Stats.TLabel"
        )
        self.sales_label.grid(
            row=0,
            column=1,
            padx=14,
            pady=10,
            sticky="w"
        )

        ttk.Button(
            register_frame,
            text="Open Cash Register",
            command=self.open_register,
            style="Accent.TButton"
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=(2, 12),
            sticky="ew"
        )

        ttk.Button(
            register_frame,
            text="Sale History",
            command=self.open_sales_history
        ).grid(
            row=1,
            column=1,
            padx=10,
            pady=(2, 12),
            sticky="ew"
        )

        register_frame.columnconfigure(0, weight=1)
        register_frame.columnconfigure(1, weight=1)

        self.refresh_inventory()
        self.refresh_register()

    # Refreshes the inventory table and filters items by title
    def refresh_inventory(self):
        search_text = self.title_var.get().strip().casefold()

        for row in self.inventory_table.get_children():
            self.inventory_table.delete(row)

        for item in self.inventory.view_inventory():
            if search_text and search_text not in item.title.casefold():
                continue

            self.inventory_table.insert(
                "",
                "end",
                values=(
                    item.title,
                    item.category,
                    item.type,
                    f"${item.price:.2f}",
                    item.quantity
                )
            )

    def filter_inventory(self, *args):
        if self.updating_fields:
            return

        self.refresh_inventory()

    # Updates the register totals shown on the main screen
    def refresh_register(self):
        self.till_label.config(
            text=f"Current Till: ${self.register.current_till:.2f}"
        )

        self.sales_label.config(
            text=f"Daily Sales: ${self.register.daily_sales:.2f}"
        )

    # Fills in the item details when a row is selected
    def select_item(self, event=None):
        selected = self.inventory_table.selection()

        if not selected:
            return

        values = self.inventory_table.item(
            selected[0],
            "values"
        )

        self.updating_fields = True

        try:
            self.title_var.set(values[0])
            self.category_var.set(values[1])
            self.type_var.set(values[2])
            self.price_var.set(values[3].replace("$", ""))
            self.quantity_var.set(values[4])
        finally:
            self.updating_fields = False

    # Clears the input fields and shows the full inventory again
    def clear_fields(self):
        self.updating_fields = True

        try:
            selected = self.inventory_table.selection()

            if selected:
                self.inventory_table.selection_remove(selected)

            self.title_var.set("")
            self.category_var.set("")
            self.type_var.set("")
            self.price_var.set("")
            self.quantity_var.set("")
        finally:
            self.updating_fields = False

        self.refresh_inventory()

    # Finds the selected item using its title and format
    def get_item_from_fields(self):
        title = self.title_var.get().strip()
        item_type = self.type_var.get().strip()

        if not title:
            messagebox.showerror(
                "Error",
                "Select or enter an item title.",
                parent=self.root
            )
            return None

        if item_type:
            item = self.inventory.search_item(title, item_type)
        else:
            item = self.inventory.search_item(title)

        if item is None:
            messagebox.showerror(
                "Item Not Found",
                "No matching item was found.\n\n"
                "If this title has multiple formats, "
                "enter its Type (such as DVD or Blu Ray), "
                "or select the exact row in the inventory table.",
                parent=self.root
            )

        return item

    # Adds a new item after checking that the information is valid
    def add_item(self):
        title = self.title_var.get().strip()
        category = self.category_var.get().strip()
        item_type = self.type_var.get().strip()

        if not title or not category or not item_type:
            messagebox.showerror(
                "Error",
                "Please complete all item fields.",
                parent=self.root
            )
            return

        try:
            price = float(self.price_var.get())
            quantity = int(self.quantity_var.get())
        except ValueError:
            messagebox.showerror(
                "Error",
                "Price and quantity must be valid numbers.",
                parent=self.root
            )
            return

        if not math.isfinite(price) or price < 0 or quantity < 0:
            messagebox.showerror(
                "Error",
                "Enter a valid non-negative price and quantity.",
                parent=self.root
            )
            return

        if self.inventory.search_item(title, item_type):
            messagebox.showerror(
                "Duplicate Item",
                f"{title} ({item_type}) already exists.",
                parent=self.root
            )
            return

        self.inventory.add_item(
            title,
            category,
            item_type,
            price,
            quantity
        )

        self.refresh_inventory()
        self.clear_fields()

        messagebox.showinfo(
            "Success",
            f"{title} ({item_type}) added to inventory!",
            parent=self.root
        )

    # Removes an item from inventory after confirming with the user
    def remove_item(self):
        item = self.get_item_from_fields()

        if item is None:
            return

        confirm = messagebox.askyesno(
            "Confirm Removal",
            f"Are you sure you want to remove "
            f"'{item.title} ({item.type})' from inventory?\n\n"
            "This action cannot be undone.",
            parent=self.root
        )

        if not confirm:
            return

        if self.inventory.remove_item(item.title, item.type):
            self.refresh_inventory()
            self.clear_fields()

            messagebox.showinfo(
                "Success",
                f"{item.title} ({item.type}) removed from inventory!",
                parent=self.root
            )
        else:
            messagebox.showerror(
                "Error",
                "Unable to remove item.",
                parent=self.root
            )

    # Updates the stock quantity for an existing item
    def update_quantity(self):
        item = self.get_item_from_fields()

        if item is None:
            return

        try:
            quantity = int(self.quantity_var.get())
        except ValueError:
            messagebox.showerror(
                "Error",
                "Enter a valid quantity.",
                parent=self.root
            )
            return

        if quantity < 0:
            messagebox.showerror(
                "Error",
                "Quantity cannot be negative.",
                parent=self.root
            )
            return

        if self.inventory.update_quantity(
            item.title, quantity, item.type
        ):
            self.refresh_inventory()
            self.clear_fields()

            messagebox.showinfo(
                "Success",
                f"Quantity updated for {item.title} ({item.type})!",
                parent=self.root
            )

    # Updates the price of an existing item
    def update_price(self):
        item = self.get_item_from_fields()

        if item is None:
            return

        try:
            price = float(self.price_var.get())
        except ValueError:
            messagebox.showerror(
                "Error",
                "Enter a valid price.",
                parent=self.root
            )
            return

        if not math.isfinite(price) or price < 0:
            messagebox.showerror(
                "Error",
                "Enter a valid non-negative price.",
                parent=self.root
            )
            return

        if self.inventory.update_price(
            item.title, price, item.type
        ):
            self.refresh_inventory()
            self.clear_fields()

            messagebox.showinfo(
                "Success",
                f"Price updated for {item.title} ({item.type})!",
                parent=self.root
            )

    # Opens the cash register or brings it to the front if already open
    def open_register(self):
        if (
            self.register_window is not None
            and self.register_window.window.winfo_exists()
        ):
            self.register_window.window.lift()
            self.register_window.window.focus_force()
            return

        self.register_window = RegisterGUI(
            self.root,
            self.inventory,
            self.register,
            self.update_after_sale
        )

    # Opens the sales history window
    def open_sales_history(self):
        if (
            self.history_window is not None
            and self.history_window.window.winfo_exists()
        ):
            self.history_window.refresh_history()
            self.history_window.window.lift()
            self.history_window.window.focus_force()
            return

        self.history_window = SalesHistoryGUI(self.root)

    # Refreshes the inventory and register totals after a sale
    def update_after_sale(self):
        self.refresh_inventory()
        self.refresh_register()
        self.clear_fields()

        if (
            self.history_window is not None
            and self.history_window.window.winfo_exists()
        ):
            self.history_window.refresh_history()
