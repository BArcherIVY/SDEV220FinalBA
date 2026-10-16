
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from datetime import datetime


# Creates the window for viewing previous sales
class SalesHistoryGUI:
    def __init__(self, parent):
        self.reports_folder = (
            Path(__file__).parent / "data" / "sales_reports"
        )

        self.window = tk.Toplevel(parent)
        self.window.title("Disc Replay - Sales History")
        self.window.transient(parent)

        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        width = min(850, screen_width - 80)
        height = min(750, screen_height - 100)

        self.window.geometry(f"{width}x{height}")

        ttk.Label(
            self.window,
            text="Disc Replay Sales History",
            font=("Arial", 20, "bold")
        ).pack(pady=(15, 5))

        ttk.Label(
            self.window,
            text="Most recent sales first"
        ).pack(pady=(0, 10))

        # Creates the refresh and close buttons
        button_frame = ttk.Frame(self.window)
        button_frame.pack(side="bottom", pady=12)

        ttk.Button(
            button_frame,
            text="Refresh History",
            command=self.refresh_history
        ).pack(side="left", padx=10)

        ttk.Button(
            button_frame,
            text="Close Window",
            command=self.window.destroy
        ).pack(side="left", padx=10)

        # Creates the area where saved sales reports are displayed
        report_frame = ttk.LabelFrame(
            self.window,
            text="Recorded Sales"
        )
        report_frame.pack(
            padx=20,
            pady=10,
            fill="both",
            expand=True
        )

        self.report_text = tk.Text(
            report_frame,
            wrap="word",
            font=("Consolas", 11),
            state="disabled",
            padx=12,
            pady=12
        )

        scrollbar = ttk.Scrollbar(
            report_frame,
            orient="vertical",
            command=self.report_text.yview
        )

        self.report_text.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(side="right", fill="y")

        self.report_text.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.report_text.tag_configure(
            "date_heading",
            font=("Consolas", 13, "bold"),
            spacing1=12,
            spacing3=6
        )

        self.refresh_history()

    # Separates each transaction and register closing into its own entry
    def split_report_into_entries(self, contents):
        lines = contents.splitlines(keepends=True)
        entries = []
        current_entry = []

        for line in lines:
            if (
                line.startswith("TRANSACTION - ")
                or "REGISTER CLOSED" in line
            ):
                if current_entry:
                    entries.append("".join(current_entry))
                current_entry = [line]
            elif current_entry:
                current_entry.append(line)

        if current_entry:
            entries.append("".join(current_entry))

        return entries

    # Loads saved reports and displays the newest sales first
    def refresh_history(self):
        self.report_text.config(state="normal")
        self.report_text.delete("1.0", tk.END)

        if not self.reports_folder.exists():
            self.report_text.insert(
                tk.END,
                "No sales history has been recorded yet.\n\n"
                "Complete a sale in the cash register "
                "to create the first daily report."
            )
            self.report_text.config(state="disabled")
            return

        report_files = sorted(
            self.reports_folder.glob("sales_????-??-??.txt"),
            reverse=True
        )

        if not report_files:
            self.report_text.insert(
                tk.END,
                "No sales reports found.\n\n"
                "Complete a sale to begin recording history."
            )
            self.report_text.config(state="disabled")
            return

        for report_file in report_files:
            date_string = report_file.stem.replace(
                "sales_", ""
            )

            try:
                report_date = datetime.strptime(
                    date_string, "%Y-%m-%d"
                )
                date_heading = report_date.strftime(
                    "%B %d, %Y"
                )
            except ValueError:
                date_heading = date_string

            self.report_text.insert(
                tk.END,
                f"\n{'=' * 55}\n"
                f"SALES DATE: {date_heading}\n"
                f"{'=' * 55}\n\n",
                "date_heading"
            )

            try:
                with open(
                    report_file,
                    "r",
                    encoding="utf-8"
                ) as file:
                    contents = file.read()

                entries = self.split_report_into_entries(
                    contents
                )

                # Displays the latest transaction at the top
                for entry in reversed(entries):
                    self.report_text.insert(
                        tk.END,
                        entry.strip() + "\n\n"
                    )

            except OSError as error:
                self.report_text.insert(
                    tk.END,
                    f"Unable to read report: {error}\n"
                )

            self.report_text.insert(tk.END, "\n")

        self.report_text.config(state="disabled")

        # Scrolls to the top when the history is refreshed
        self.report_text.see("1.0")
