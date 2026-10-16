
class Item:
    def __init__(self, title, category, type, price, quantity):
        self.title = title
        self.category = category
        self.type = type
        self.price = float(price)
        self.quantity = int(quantity)
