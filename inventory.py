
import json
from pathlib import Path
from item import Item


class Inventory:
    def __init__(self):
        self.items = []
        self.file_path = Path(__file__).parent / "data" / "inventory.json"
        self.load_inventory()

    def add_item(self, title, category, type, price, quantity):
        if self.search_item(title, type):
            return None

        item = Item(title, category, type, price, quantity)
        self.items.append(item)
        self.save_inventory()
        return item

    def remove_item(self, title, type=None):
        item = self.search_item(title, type)

        if item:
            self.items.remove(item)
            self.save_inventory()
            return True

        return False

    def search_item(self, title, type=None):
        matches = []

        for item in self.items:
            if item.title.casefold() != title.casefold():
                continue

            if type is None or item.type.casefold() == type.casefold():
                matches.append(item)

        # Do not guess which format the user wants.
        if len(matches) == 1:
            return matches[0]

        return None

    def update_quantity(self, title, quantity, type=None):
        item = self.search_item(title, type)

        if item and int(quantity) >= 0:
            item.quantity = int(quantity)
            self.save_inventory()
            return True

        return False

    def update_price(self, title, price, type=None):
        item = self.search_item(title, type)

        if item and float(price) >= 0:
            item.price = float(price)
            self.save_inventory()
            return True

        return False

    def view_inventory(self):
        return sorted(
            self.items,
            key=lambda item: (
                item.title.casefold(),
                item.type.casefold()
            )
        )

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
