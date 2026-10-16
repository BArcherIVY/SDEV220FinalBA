
import json
from pathlib import Path
from item import Item


# Handles adding, removing, searching, and updating inventory items
class Inventory:
    def __init__(self):
        self.items = []
        self.file_path = Path(__file__).parent / "data" / "inventory.json"
        self.load_inventory()

    # Adds a new item and saves it to the inventory file
    def add_item(self, title, category, type, price, quantity):
        if self.search_item(title, type):
            return None

        item = Item(title, category, type, price, quantity)
        self.items.append(item)
        self.save_inventory()
        return item

    # Removes an item from inventory
    def remove_item(self, title, type=None):
        item = self.search_item(title, type)

        if item:
            self.items.remove(item)
            self.save_inventory()
            return True

        return False

    # Searches by title and format so different versions don't get mixed up
    def search_item(self, title, type=None):
        matches = []

        for item in self.items:
            if item.title.casefold() != title.casefold():
                continue

            if type is None or item.type.casefold() == type.casefold():
                matches.append(item)

        if len(matches) == 1:
            return matches[0]

        return None

    # Updates the quantity of an existing item
    def update_quantity(self, title, quantity, type=None):
        item = self.search_item(title, type)

        if item and int(quantity) >= 0:
            item.quantity = int(quantity)
            self.save_inventory()
            return True

        return False

    # Updates the price of an existing item
    def update_price(self, title, price, type=None):
        item = self.search_item(title, type)

        if item and float(price) >= 0:
            item.price = float(price)
            self.save_inventory()
            return True

        return False

    # Sorts the inventory alphabetically by title and format
    def view_inventory(self):
        return sorted(
            self.items,
            key=lambda item: (
                item.title.casefold(),
                item.type.casefold()
            )
        )

    # Saves all inventory items to the JSON file
    def save_inventory(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        data = []

        for item in self.items:
            data.append({
                "title": item.title,
                "category": item.category,
                "type": item.type,
                "price": item.price,
                "quantity": item.quantity
            })

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    # Loads saved inventory items when the program starts
    def load_inventory(self):
        if not self.file_path.exists():
            return

        with open(self.file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        for entry in data:
            self.items.append(
                Item(
                    entry["title"],
                    entry["category"],
                    entry["type"],
                    entry["price"],
                    entry["quantity"]
                )
            )
