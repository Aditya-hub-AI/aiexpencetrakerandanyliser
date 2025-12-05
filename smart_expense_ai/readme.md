# Smart Expense AI 💰🤖

Smart Expense AI is a desktop-based **expense tracker** with a modern Tkinter GUI and a simple built-in **AI module** that predicts next month’s spending using linear regression.

It helps you:
- Add and manage daily expenses
- Filter expenses by date range and category
- View totals, averages, and category-wise summaries
- Get an AI-powered prediction of your future monthly spending

---

## 🚀 Features

### ✅ Expense Management
- Add expenses with:
  - Date (YYYY-MM-DD)
  - Category (Food, Transport, Shopping, Bills, Entertainment, Other, etc.)
  - Amount (₹)
- All data is stored in a simple `expenses.csv` file (auto-created).

### 🔍 Smart Filtering
- Filter expenses by:
  - **From date** and **To date**
  - **Category** (or “All”)
- View only what you need in the table.

### 📊 Summary Panel
Automatic summary for current view:
- Total spending
- Average expense per entry
- Highest single expense
- Number of entries

Category-wise spending is also calculated internally for insights.

### 🧠 AI Insights (Simple ML)
- Uses **monthly totals** and **linear regression** (`LinearRegression` from `sklearn`) to:
  - Predict **next month’s total spending**
  - Suggest a **safe limit**
  - Give basic tips for controlling expenses

Works on:
- Entire dataset, or
- Only the **filtered view** shown in the table

### 🎨 Pro-Level GUI (Tkinter + ttk)
- Clean, modern UI using `ttk` widgets
- Organized into:
  - Add Expense form
  - Filter panel
  - Expense table (scrollable)
  - Summary panel
  - AI Insight panel
- Minimum window size to keep layout neat

---

## 🧾 Tech Stack

- **Language:** Python 3.x
- **GUI:** Tkinter (`tk` and `ttk`)
- **Data Handling:** `pandas`
- **Machine Learning:** `scikit-learn` (Linear Regression)
- **Storage:** CSV file (`expenses.csv`)

---

## 📂 Project Structure

```text
smart_expense_ai/
├── gui_app.py         # Main GUI application
├── expense_model.py   # Data layer + AI logic (ML model & helpers)
├── expenses.csv       # Auto-generated CSV storage for expenses
└── README.md          # Project documentation (this file)
