# Disc Replay Inventory System

## Project Description

For my SDEV220 final project, I created an inventory system for a video game/movie/electronic store called Disc Replay. 

The program lets employees manage inventory, ring up cash sales, and keep track of previous transactions.

## How to Run the Program

1. Download or clone the project from GitHub.
2. Make sure Python 3 is installed on your computer.
3. Open the project folder in Visual Studio Code.
4. Open the terminal in VS Code.
5. Run the following command:

   `py main.py`

   If the `py` command is unavailable, try `python main.py`.

6. The Disc Replay Inventory System window will open.

No additional Python packages are required.

## Program Features

### Inventory Management

- **Add Item:** Add a new game or movie with its title, category, format, price, and quantity.
- **Remove Item:** Delete an existing item from inventory.
- **Search Inventory:** Find products by typing their title in the search field.
- **Update Quantity:** Change the number of copies available.
- **Update Price:** Change the price of an existing product.
- **View Inventory:** Display the products currently stored in inventory.

### Cash Register

- Search for products and add them to a shopping cart.
- Adjust the quantity of products being purchased.
- Remove individual products or clear the entire cart.
- Calculate the total cost of a sale.
- Enter the amount of cash received from a customer.
- Automatically calculate the change owed.
- Prevent sales when there is insufficient stock, insufficient payment, or not enough cash in the register to provide change.
- Automatically update inventory quantities after a completed sale.

### Sales History

- Record completed transactions in daily sales reports.
- View previous transactions through the Sales History window.
- Display the most recent sales first.
- Refresh the sales history to view updated records.

### Closing the Register

- The register starts with $150.00 in the till.
- Daily sales and the current till balance are tracked.
- Closing the register saves a summary of the day's sales.
- The till resets to $150.00 for the next session.

## Data Storage

The program uses JSON files to save inventory and register information.

- `data/inventory.json` stores inventory records.
- `data/register.json` stores the current register totals.
- `data/sales_reports/` stores daily sales reports as text files.

Inventory and register information are saved so they can be loaded again when the program restarts.

## Technologies Used

- Python 3
- Tkinter (GUI)
- JSON (Data Storage)

## Project Files

- `main.py` — Starts the application.
- `gui.py` — Main inventory interface.
- `item.py` — Defines individual inventory items.
- `inventory.py` — Handles inventory management and saving data.
- `register.py` — Processes sales and manages register totals.
- `register_gui.py` — Cash register interface.
- `sales_history_gui.py` — Displays saved sales reports.

## Project Information

**Course:** SDEV220 – Python Programming  
**Project:** Final Project – Disc Replay Inventory System
