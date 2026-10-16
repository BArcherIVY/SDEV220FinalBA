
import json
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


# Rounds money to two decimal places
def money(value):
    return Decimal(str(value)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


# Handles sales, cash payments, and saving register information
class Register:
    def __init__(self, inventory):
        self.inventory = inventory
        self.starting_till = 150.00
        self.current_till = 150.00
        self.daily_sales = 0.00

        self.file_path = Path(__file__).parent / "data" / "register.json"

        self.reports_folder = (
            Path(__file__).parent / "data" / "sales_reports"
        )

        self.load_register()

    # Processes a sale for a single item
    def complete_sale(
        self, title, quantity, cash_received=None, type=None
    ):
        if type is None:
            item = self.inventory.search_item(title)
            if item is None:
                return False, (
                    "Product not found, or multiple formats exist. "
                    "Please select a format."
                )
            type = item.type

        return self.complete_cart_sale(
            {(title, type): quantity},
            cash_received
        )

    # Calculates the total cost of the items in the cart
    def calculate_total(self, cart):
        total = Decimal("0.00")

        for (title, item_type), quantity in cart.items():
            item = self.inventory.search_item(title, item_type)

            if item is None:
                raise ValueError(
                    f"{title} ({item_type}) was not found."
                )

            total += money(item.price) * int(quantity)

        return money(total)

    # Checks the cart and payment before completing a sale
    def complete_cart_sale(self, cart, cash_received=None):
        if not cart:
            return False, "The cart is empty."

        sale_items = []
        total = Decimal("0.00")

        for (title, item_type), quantity in cart.items():
            item = self.inventory.search_item(title, item_type)
            product_name = f"{title} ({item_type})"

            try:
                quantity = int(quantity)
            except (TypeError, ValueError):
                return False, f"Invalid quantity for {product_name}."

            if item is None:
                return False, f"{product_name} was not found."

            if quantity <= 0:
                return False, "Quantity must be greater than zero."

            if item.quantity < quantity:
                return False, f"Not enough stock for {product_name}."

            unit_price = money(item.price)
            subtotal = unit_price * quantity

            sale_items.append(
                (item, quantity, unit_price, subtotal)
            )

            total += subtotal

        total = money(total)

        if cash_received is None:
            return False, "Enter the cash received."

        try:
            cash = money(cash_received)
        except (InvalidOperation, ValueError, TypeError):
            return False, "Enter a valid cash amount."

        if not cash.is_finite() or cash < 0:
            return False, "Enter a valid cash amount."

        if cash < total:
            shortage = total - cash
            return False, (
                f"Insufficient payment. "
                f"Need ${shortage:.2f} more."
            )

        change = money(cash - total)

        # Makes sure there is enough cash in the till to give change
        available_cash = money(self.current_till)

        if change > available_cash:
            return False, (
                "Insufficient Cash in Register!\n\n"
                f"Change Required: ${change:.2f}\n"
                f"Cash Available in Till: ${available_cash:.2f}\n\n"
                "There is not enough cash in the till to "
                "provide this amount of change.\n\n"
                "Please enter a different cash amount and try again."
            )

        # Updates the inventory and register after all payment checks pass
        for item, quantity, unit_price, subtotal in sale_items:
            item.quantity -= quantity

        self.current_till = float(
            money(self.current_till) + total
        )

        self.daily_sales = float(
            money(self.daily_sales) + total
        )

        self.inventory.save_inventory()
        self.save_register()

        try:
            self.save_transaction(
                sale_items,
                total,
                cash,
                change
            )
        except OSError as error:
            return True, (
                f"Sale completed!\n\n"
                f"Sale Total: ${total:.2f}\n"
                f"Change Due: ${change:.2f}\n\n"
                f"Warning: Could not save sales history:\n{error}"
            )

        return True, (
            f"Sale completed!\n\n"
            f"Sale Total: ${total:.2f}\n"
            f"Cash Received: ${cash:.2f}\n"
            f"Change Due: ${change:.2f}"
        )

    # Creates the file path for the current day's sales report
    def get_report_path(self):
        date = datetime.now().strftime("%Y-%m-%d")
        return self.reports_folder / f"sales_{date}.txt"

    # Saves each transaction to the daily sales report
    def save_transaction(self, sale_items, total, cash, change):
        self.reports_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        now = datetime.now()
        report_path = self.get_report_path()

        if not report_path.exists():
            with open(
                report_path,
                "w",
                encoding="utf-8"
            ) as file:
                file.write("=" * 55 + "\n")
                file.write("          DISC REPLAY DAILY SALES REPORT\n")
                file.write("=" * 55 + "\n")
                file.write(
                    f"Date: {now.strftime('%B %d, %Y')}\n"
                )
                file.write("=" * 55 + "\n\n")

        with open(
            report_path,
            "a",
            encoding="utf-8"
        ) as file:
            file.write(
                f"TRANSACTION - {now.strftime('%I:%M:%S %p')}\n"
            )
            file.write("-" * 55 + "\n")

            for item, quantity, unit_price, subtotal in sale_items:
                file.write(f"{item.title} ({item.type})\n")
                file.write(f"  Quantity: {quantity}\n")
                file.write(f"  Unit Price: ${unit_price:.2f}\n")
                file.write(f"  Subtotal: ${subtotal:.2f}\n")

            file.write("-" * 55 + "\n")
            file.write(f"Sale Total:      ${total:.2f}\n")
            file.write(f"Cash Received:   ${cash:.2f}\n")
            file.write(f"Change Given:    ${change:.2f}\n")
            file.write(
                f"Till Balance:    ${self.current_till:.2f}\n"
            )
            file.write(
                f"Session Sales:   ${self.daily_sales:.2f}\n"
            )
            file.write("=" * 55 + "\n\n")

    # Closes the register, saves the totals, and resets the till
    def close_register(self):
        total_sales = self.daily_sales
        closing_till = self.current_till

        self.save_closing_summary(
            total_sales,
            closing_till
        )

        self.current_till = self.starting_till
        self.daily_sales = 0.00

        self.save_register()

        return total_sales

    # Adds the closing totals to the daily sales report
    def save_closing_summary(self, total_sales, closing_till):
        self.reports_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        now = datetime.now()
        report_path = self.get_report_path()

        if not report_path.exists():
            with open(
                report_path,
                "w",
                encoding="utf-8"
            ) as file:
                file.write("DISC REPLAY DAILY SALES REPORT\n")
                file.write(
                    f"Date: {now.strftime('%B %d, %Y')}\n\n"
                )

        with open(
            report_path,
            "a",
            encoding="utf-8"
        ) as file:
            file.write("\n")
            file.write("*" * 55 + "\n")
            file.write("              REGISTER CLOSED\n")
            file.write("*" * 55 + "\n")
            file.write(
                f"Date: {now.strftime('%B %d, %Y')}\n"
            )
            file.write(
                f"Time: {now.strftime('%I:%M:%S %p')}\n"
            )
            file.write(
                f"Starting Till: ${self.starting_till:.2f}\n"
            )
            file.write(
                f"Session Sales: ${total_sales:.2f}\n"
            )
            file.write(
                f"Closing Till: ${closing_till:.2f}\n"
            )
            file.write("*" * 55 + "\n\n")

    # Saves the current till and daily sales totals to JSON
    def save_register(self):
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = {
            "starting_till": self.starting_till,
            "current_till": self.current_till,
            "daily_sales": self.daily_sales
        }

        with open(
            self.file_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(data, file, indent=4)

    # Loads the saved register totals when the program starts
    def load_register(self):
        if not self.file_path.exists():
            return

        with open(
            self.file_path,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        self.starting_till = float(
            data.get("starting_till", 150.00)
        )
        self.current_till = float(
            data.get("current_till", 150.00)
        )
        self.daily_sales = float(
            data.get("daily_sales", 0.00)
        )
