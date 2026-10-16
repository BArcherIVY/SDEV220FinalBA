
import tkinter as tk
from gui import InventoryGUI


# Starts the main inventory window and keeps the program running
if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryGUI(root)
    root.mainloop()
