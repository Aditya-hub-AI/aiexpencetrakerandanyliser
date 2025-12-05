# gui_app.py
"""
Smart Expense AI - Pro Level GUI

Upgraded Tkinter UI with:
- Modern layout using ttk widgets
- Expense table with sortable columns
- Date & category filters
- Live summary panel
- AI-based monthly spending prediction
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from typing import Optional

from expense_model import (
    add_expense,
    load_data,
    filter_data,
    compute_summary,
    predict_next_month,
)


# ---------- Helper functions for UI ----------


def set_text(widget: tk.Text, text: str) -> None:
    widget.config(state="normal")
    widget.delete("1.0", tk.END)
    widget.insert(tk.END, text)
    widget.config(state="disabled")


# ---------- Main Application Class ----------


class SmartExpenseApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Expense AI")
        self.geometry("980x620")
        self.minsize(900, 550)

        # Use ttk styling for more professional look
        self.style = ttk.Style(self)
        self._configure_style()

        # Shared state
        self.df = load_data()

        # Build UI structure
        self._build_header()
        self._build_main_layout()
        self._populate_table(self.df)
        self._update_summary_panel()

    # ----- Styling -----
    def _configure_style(self):
        try:
            # Try a nicer theme if available
            if "clam" in self.style.theme_names():
                self.style.theme_use("clam")
        except Exception:
            pass

        self.style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"))
        self.style.configure("SubHeader.TLabel", font=("Segoe UI", 11, "bold"))
        self.style.configure("TButton", font=("Segoe UI", 10))
        self.style.configure("TEntry", font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    # ----- Layout building -----
    def _build_header(self):
        header_frame = ttk.Frame(self, padding=(15, 10))
        header_frame.pack(side=tk.TOP, fill=tk.X)

        title_label = ttk.Label(
            header_frame,
            text="Smart Expense AI",
            style="Header.TLabel",
        )
        title_label.pack(side=tk.LEFT)

        subtitle = ttk.Label(
            header_frame,
            text="Track, analyze and predict your monthly expenses",
            foreground="#555",
        )
        subtitle.pack(side=tk.LEFT, padx=(10, 0))

    def _build_main_layout(self):
        # Main container (left: forms+table, right: summary+AI)
        main_frame = ttk.Frame(self, padding=(10, 0))
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # ----- Left top: Add expense form -----
        form_frame = ttk.LabelFrame(
            left_frame, text="Add Expense", padding=(10, 10)
        )
        form_frame.pack(fill=tk.X, pady=(0, 8))

        # Date
        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(
            row=0, column=0, sticky="w"
        )
        self.entry_date = ttk.Entry(form_frame, width=18)
        self.entry_date.grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(0, 4))

        # Category
        ttk.Label(form_frame, text="Category:").grid(
            row=0, column=1, sticky="w"
        )
        self.category_var = tk.StringVar()
        default_categories = [
            "Food",
            "Transport",
            "Shopping",
            "Bills",
            "Entertainment",
            "Other",
        ]
        self.combo_category = ttk.Combobox(
            form_frame,
            textvariable=self.category_var,
            values=default_categories,
            width=18,
        )
        self.combo_category.grid(row=1, column=1, sticky="w", padx=(0, 8))
        self.combo_category.set("Food")

        # Amount
        ttk.Label(form_frame, text="Amount (₹):").grid(
            row=0, column=2, sticky="w"
        )
        self.entry_amount = ttk.Entry(form_frame, width=14)
        self.entry_amount.grid(row=1, column=2, sticky="w", padx=(0, 8))

        # Buttons row
        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=0, column=3, rowspan=2, sticky="e")

        self.btn_add = ttk.Button(btn_frame, text="Add", command=self.on_add_expense)
        self.btn_add.pack(side=tk.TOP, fill=tk.X, padx=(8, 0))

        self.btn_clear_form = ttk.Button(
            btn_frame, text="Clear", command=self.on_clear_form
        )
        self.btn_clear_form.pack(side=tk.TOP, fill=tk.X, padx=(8, 0), pady=(4, 0))

        # ----- Left middle: Filters -----
        filter_frame = ttk.LabelFrame(
            left_frame, text="Filter & Search", padding=(10, 8)
        )
        filter_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(filter_frame, text="From (YYYY-MM-DD):").grid(
            row=0, column=0, sticky="w"
        )
        self.entry_start_date = ttk.Entry(filter_frame, width=16)
        self.entry_start_date.grid(row=1, column=0, sticky="w", padx=(0, 8))

        ttk.Label(filter_frame, text="To (YYYY-MM-DD):").grid(
            row=0, column=1, sticky="w"
        )
        self.entry_end_date = ttk.Entry(filter_frame, width=16)
        self.entry_end_date.grid(row=1, column=1, sticky="w", padx=(0, 8))

        ttk.Label(filter_frame, text="Category:").grid(
            row=0, column=2, sticky="w"
        )
        self.filter_category_var = tk.StringVar(value="All")
        self.combo_filter_category = ttk.Combobox(
            filter_frame, textvariable=self.filter_category_var, width=14
        )
        self.combo_filter_category.grid(row=1, column=2, sticky="w", padx=(0, 8))
        self._refresh_filter_categories()

        btn_filter = ttk.Button(
            filter_frame, text="Apply Filter", command=self.on_apply_filter
        )
        btn_filter.grid(row=0, column=3, rowspan=2, padx=(8, 0), sticky="nswe")

        btn_reset = ttk.Button(
            filter_frame, text="Reset", command=self.on_reset_filter
        )
        btn_reset.grid(row=0, column=4, rowspan=2, padx=(4, 0), sticky="nswe")

        # ----- Left bottom: Table -----
        table_frame = ttk.LabelFrame(
            left_frame, text="Expenses", padding=(5, 5)
        )
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("date", "category", "amount")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("date", text="Date")
        self.tree.heading("category", text="Category")
        self.tree.heading("amount", text="Amount (₹)")

        self.tree.column("date", width=110, anchor="center")
        self.tree.column("category", width=160, anchor="w")
        self.tree.column("amount", width=100, anchor="e")

        vsb = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # ----- Right: Summary & AI panel -----
        summary_frame = ttk.LabelFrame(
            right_frame, text="Summary", padding=(10, 10)
        )
        summary_frame.pack(fill=tk.X, pady=(0, 8), padx=(8, 0))

        self.lbl_total = ttk.Label(summary_frame, text="Total: ₹0.00")
        self.lbl_total.pack(anchor="w")

        self.lbl_avg = ttk.Label(summary_frame, text="Average per entry: ₹0.00")
        self.lbl_avg.pack(anchor="w", pady=(2, 0))

        self.lbl_max = ttk.Label(summary_frame, text="Highest single expense: ₹0.00")
        self.lbl_max.pack(anchor="w", pady=(2, 0))

        self.lbl_count = ttk.Label(summary_frame, text="Number of entries: 0")
        self.lbl_count.pack(anchor="w", pady=(2, 0))

        ttk.Separator(right_frame, orient="horizontal").pack(
            fill=tk.X, pady=(8, 8), padx=(8, 0)
        )

        ai_frame = ttk.LabelFrame(right_frame, text="AI Insight", padding=(10, 10))
        ai_frame.pack(fill=tk.BOTH, expand=True, padx=(8, 0))

        self.btn_analyze = ttk.Button(
            ai_frame, text="Run AI Analysis", command=self.on_ai_analyze
        )
        self.btn_analyze.pack(fill=tk.X)

        self.ai_text = tk.Text(ai_frame, height=12, wrap="word")
        self.ai_text.pack(fill=tk.BOTH, expand=True, pady=(8, 0))
        self.ai_text.config(state="disabled")

    # ----- Event Handlers -----
    def on_add_expense(self):
        date = self.entry_date.get().strip()
        category = self.category_var.get().strip()
        amount_str = self.entry_amount.get().strip()

        if not date or not category or not amount_str:
            messagebox.showwarning("Missing Data", "Please fill all fields.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid Amount", "Please enter a valid positive number for amount."
            )
            return

        try:
            self.df = add_expense(date, category, amount)
        except Exception as e:
            messagebox.showerror(
                "Error", f"Failed to save expense:\n{e}"
            )
            return

        self._populate_table(self.df)
        self._update_summary_panel()
        self._refresh_filter_categories()
        self.on_clear_form()

        messagebox.showinfo("Success", "Expense added successfully!")

    def on_clear_form(self):
        self.entry_date.delete(0, tk.END)
        self.entry_amount.delete(0, tk.END)
        # keep last category

    def _refresh_filter_categories(self):
        # Build category list from data
        df = self.df
        categories = sorted(df["category"].dropna().unique().tolist()) if not df.empty else []
        values = ["All"] + categories
        self.combo_filter_category.configure(values=values)
        if self.filter_category_var.get() not in values:
            self.filter_category_var.set("All")

    def on_apply_filter(self):
        start = self.entry_start_date.get().strip() or None
        end = self.entry_end_date.get().strip() or None
        cat = self.filter_category_var.get().strip() or None

        filtered = filter_data(self.df, start_date=start, end_date=end, category=cat)
        self._populate_table(filtered)
        self._update_summary_panel(filtered)

    def on_reset_filter(self):
        self.entry_start_date.delete(0, tk.END)
        self.entry_end_date.delete(0, tk.END)
        self.filter_category_var.set("All")
        self._populate_table(self.df)
        self._update_summary_panel()

    def on_ai_analyze(self):
        filtered_df = self._get_current_table_df()
        pred, advice = predict_next_month(filtered_df if not filtered_df.empty else self.df)
        if pred is None:
            result_text = advice
        else:
            result_text = f"Predicted next month spending: ₹{pred:.2f}\n\n{advice}"
        set_text(self.ai_text, result_text)

    # ----- Helpers -----
    def _populate_table(self, df):
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)

        if df is None or df.empty:
            return

        for _, row in df.iterrows():
            self.tree.insert(
                "",
                tk.END,
                values=(
                    str(row.get("date", "")),
                    str(row.get("category", "")),
                    f"{float(row.get('amount', 0.0)):.2f}",
                ),
            )

    def _update_summary_panel(self, df: Optional[object] = None):
        summary = compute_summary(df)
        self.lbl_total.config(text=f"Total: ₹{summary['total']:.2f}")
        self.lbl_avg.config(
            text=f"Average per entry: ₹{summary['average']:.2f}"
        )
        self.lbl_max.config(
            text=f"Highest single expense: ₹{summary['max']:.2f}"
        )
        self.lbl_count.config(
            text=f"Number of entries: {summary['count']}"
        )

    def _get_current_table_df(self):
        """
        Reconstruct a DataFrame from the current contents of the Treeview.
        This lets AI analysis work on the filtered view as well.
        """
        import pandas as pd

        rows = []
        for item_id in self.tree.get_children():
            date, category, amount_str = self.tree.item(item_id, "values")
            try:
                amount = float(amount_str)
            except ValueError:
                amount = 0.0
            rows.append({"date": date, "category": category, "amount": amount})

        if not rows:
            return pd.DataFrame(columns=["date", "category", "amount"])

        return pd.DataFrame(rows)


if __name__ == "__main__":
    app = SmartExpenseApp()
    app.mainloop()
