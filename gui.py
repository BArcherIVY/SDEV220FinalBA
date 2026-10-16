
import tkinter as tk
from tkinter import ttk, messagebox
import math

from inventory import Inventory
from register import Register
from register_gui import RegisterGUI
from sales_history_gui import SalesHistoryGUI


class InventoryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Disc Replay Inventory System")

        # Open Inventory maximized.
        self.root.state("zoomed")

        self.inventory = Inventory()
        self.register = Register(self.inventory)

        self.register_window = None
        self.history_window = None

        ttk.Label(
            root,
            text="Disc Replay Inventory System",
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        # Inventory table
        table_frame = ttk.LabelFrame(
            root,
            text="Current Inventory"
        )
        table_frame.pack(
            padx=10,
            pady=5,
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
            self.inventory_table.heading(name, text=name)
            self.inventory_table.column(
                name,
                width=width,
                minwidth=55,
                stretch=True
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.inventory_table.yview
        )

        self.inventory_table.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(side="right", fill="y")

        self.inventory_table.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        self.inventory_table.bind(
            "<<TreeviewSelect>>",
            self.select_item
        )

        # Item details
        details_frame = ttk.LabelFrame(
            root,
            text="Item Details"
        )
        details_frame.pack(
            padx=10,
            pady=5,
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
                text=label
            ).grid(
                row=row_number * 2,
                column=column_number,
                padx=8,
                pady=(4, 0),
                sticky="w"
            )

            ttk.Entry(
                details_frame,
                textvariable=variable
            ).grid(
                row=row_number * 2 + 1,
                column=column_number,
                padx=8,
                pady=(0, 4),
                sticky="ew"
            )

        details_frame.columnconfigure(0, weight=1)
        details_frame.columnconfigure(1, weight=1)

        # Inventory controls
        button_frame = ttk.LabelFrame(
            root,
            text="Inventory Controls"
        )
        button_frame.pack(
            padx=10,
            pady=5,
            fill="x"
        )

        buttons = [
            ("Add Item", self.add_item),
            ("Remove Item", self.remove_item),
            ("Search Item", self.search_item),
            ("Update Quantity", self.update_quantity),
            ("Update Price", self.update_price),
            ("Clear Fields", self.clear_fields)
        ]

        for index, (text, command) in enumerate(buttons):
            row_number = index // 3
            column_number = index % 3

            ttk.Button(
                button_frame,
                text=text,
                command=command
            ).grid(
                row=row_number,
                column=column_number,
                padx=5,
                pady=5,
                sticky="ew"
            )

        for column in range(3):
            button_frame.columnconfigure(column, weight=1)

        # Cash register section
        register_frame = ttk.LabelFrame(
            root,
            text="Cash Register"
        )
        register_frame.pack(
            padx=10,
            pady=8,
            fill="x"
        )

        self.till_label = ttk.Label(
            register_frame,
            text="Current Till: $150.00",
            font=("Arial", 11, "bold")
        )
        self.till_label.grid(
            row=0,
            column=0,
            padx=8,
            pady=8,
            sticky="w"
        )

        self.sales_label = ttk.Label(
            register_frame,
            text="Daily Sales: $0.00",
            font=("Arial", 11, "bold")
        )
        self.sales_label.grid(
            row=0,
            column=1,
            padx=8,
            pady=8,
            sticky="w"
        )

        ttk.Button(
            register_frame,
            text="Open Cash Register",
            command=self.open_register
        ).grid(
            row=1,
            column=0,
            padx=8,
            pady=8,
            sticky="ew"
        )

        ttk.Button(
            register_frame,
            text="Sale History",
            command=self.open_sales_history
        ).grid(
            row=1,
            column=1,
            padx=8,
            pady=8,
            sticky="ew"
        )

        register_frame.columnconfigure(0, weight=1)
        register_frame.columnconfigure(1, weight=1)

        self.refresh_inventory()
        self.refresh_register()

    def refresh_inventory(self):
        for row in self.inventory_table.get_children():
            self.inventory_table.delete(row)

        for item in self.inventory.view_inventory():
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

    def refresh_register(self):
        self.till_label.config(
            text=f"Current Till: ${self.register.current_till:.2f}"
        )

        self.sales_label.config(
            text=f"Daily Sales: ${self.register.daily_sales:.2f}"
        )

    def select_item(self, event=None):
        selected = self.inventory_table.selection()

        if not selected:
            return

        values = self.inventory_table.item(
            selected[0],
            "values"
        )

        self.title_var.set(values[0])
        self.category_var.set(values[1])
        self.type_var.set(values[2])
        self.price_var.set(values[3].replace("$", ""))
        self.quantity_var.set(values[4])

    def clear_fields(self):
        selected = self.inventory_table.selection()

        if selected:
            self.inventory_table.selection_remove(selected)

        self.title_var.set("")
        self.category_var.set("")
        self.type_var.set("")
        self.price_var.set("")
        self.quantity_var.set("")

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

    def search_item(self):
        item = self.get_item_from_fields()

        if item is None:
            return

        self.title_var.set(item.title)
        self.category_var.set(item.category)
        self.type_var.set(item.type)
        self.price_var.set(f"{item.price:.2f}")
        self.quantity_var.set(str(item.quantity))

        for row in self.inventory_table.get_children():
            values = self.inventory_table.item(row, "values")

            if (
                values[0].casefold() == item.title.casefold()
                and values[2].casefold() == item.type.casefold()
            ):
                self.inventory_table.selection_set(row)
                self.inventory_table.see(row)
                break

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

    def update_after_sale(self):
        self.refresh_inventory()
        self.refresh_register()
        self.clear_fields()

        if (
            self.history_window is not None
            and self.history_window.window.winfo_exists()
        ):
            self.history_window.refresh_history()
