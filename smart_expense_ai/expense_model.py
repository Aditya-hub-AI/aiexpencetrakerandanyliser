# expense_model.py
"""
Data layer and simple AI analysis for Smart Expense AI.

Features:
- CSV-based persistent storage
- Helpers for loading, adding and filtering expenses
- Monthly spending prediction using a simple linear regression model
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, Dict, Any

import pandas as pd
from sklearn.linear_model import LinearRegression

# Store data next to this file
DATA_FILE = Path(__file__).with_name("expenses.csv")


def _init_file() -> pd.DataFrame:
    """Create an empty CSV if it does not exist and return a DataFrame."""
    df = pd.DataFrame(columns=["date", "category", "amount"])
    df.to_csv(DATA_FILE, index=False)
    return df


def load_data() -> pd.DataFrame:
    """
    Load expenses from CSV, creating the file if needed.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: date (str), category (str), amount (float)
    """
    if not DATA_FILE.exists():
        df = _init_file()
    else:
        df = pd.read_csv(DATA_FILE)

    # Normalize columns
    expected_cols = ["date", "category", "amount"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None
    df = df[expected_cols]

    # Clean types
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    return df


def save_data(df: pd.DataFrame) -> None:
    """Persist DataFrame to CSV."""
    df.to_csv(DATA_FILE, index=False)


def add_expense(date: str, category: str, amount: float) -> pd.DataFrame:
    """
    Append a new expense to the dataset and save.

    Parameters
    ----------
    date : str
        Date string (recommended format: YYYY-MM-DD)
    category : str
        Expense category
    amount : float
        Expense amount

    Returns
    -------
    pd.DataFrame
        Updated DataFrame
    """
    df = load_data()
    new_row = {"date": date, "category": category, "amount": float(amount)}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)
    return df


def filter_data(
    df: Optional[pd.DataFrame] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
) -> pd.DataFrame:
    """
    Filter expenses by optional date range and category.

    Dates should be in a format recognized by pandas (e.g. YYYY-MM-DD).
    """
    if df is None:
        df = load_data()

    if df.empty:
        return df

    # Work on a copy
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    if start_date:
        start = pd.to_datetime(start_date, errors="coerce")
        if pd.notna(start):
            df = df[df["date"] >= start]

    if end_date:
        end = pd.to_datetime(end_date, errors="coerce")
        if pd.notna(end):
            df = df[df["date"] <= end]

    if category and category != "All":
        df = df[df["category"].astype(str).str.lower() == category.lower()]

    # Convert date back to string for display
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df


def compute_summary(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Compute basic summary stats for the given expenses.

    Returns a dictionary with:
    - total
    - average
    - max
    - count
    - by_category (dict)
    """
    if df is None:
        df = load_data()

    if df.empty:
        return {
            "total": 0.0,
            "average": 0.0,
            "max": 0.0,
            "count": 0,
            "by_category": {},
        }

    total = float(df["amount"].sum())
    count = int(df["amount"].count())
    average = float(total / count) if count else 0.0
    max_val = float(df["amount"].max()) if count else 0.0
    by_cat_series = df.groupby("category")["amount"].sum().sort_values(ascending=False)
    by_category = {str(k): float(v) for k, v in by_cat_series.items()}

    return {
        "total": round(total, 2),
        "average": round(average, 2),
        "max": round(max_val, 2),
        "count": count,
        "by_category": by_category,
    }


def _monthly_totals(df: pd.DataFrame) -> pd.Series:
    """Return a Series of monthly totals indexed by month (as datetime)."""
    if df.empty:
        return pd.Series(dtype=float)

    d = df.copy()
    d["date"] = pd.to_datetime(d["date"], errors="coerce")
    d = d.dropna(subset=["date"])
    if d.empty:
        return pd.Series(dtype=float)

    d["month"] = d["date"].dt.to_period("M")
    monthly = d.groupby("month")["amount"].sum().sort_index()
    return monthly


def predict_next_month(
    df: Optional[pd.DataFrame] = None,
) -> Tuple[Optional[float], str]:
    """
    Predict next month's total spending using a simple linear regression.

    Returns
    -------
    (prediction, advice_text)
      prediction : float or None if prediction not possible
      advice_text : human-readable explanation
    """
    if df is None:
        df = load_data()

    monthly = _monthly_totals(df)
    if len(monthly) == 0:
        return None, "Not enough data to analyze yet. Add some expenses first."

    if len(monthly) == 1:
        # With only one month, just reuse that as a naive forecast
        pred = float(monthly.iloc[0])
        advice = (
            f"Based on last month, you may spend about ₹{pred:.2f} next month. "
            "Add more data for a smarter trend-based prediction."
        )
        return round(pred, 2), advice

    # Use simple index as time feature: 0, 1, 2, ...
    X = [[i] for i in range(len(monthly))]
    y = monthly.values

    model = LinearRegression()
    model.fit(X, y)

    next_idx = [[len(monthly)]]
    pred = float(model.predict(next_idx)[0])
    pred = round(pred, 2)

    # Simple rule-of-thumb safety band
    safe_limit = 0.9 * pred
    if pred <= 0:
        advice = (
            "Your recent spending trend is flat or declining. "
            "Great job! Keep tracking to maintain this habit."
        )
    else:
        advice = (
            f"Our AI estimates you may spend around ₹{pred:.2f} next month.\n"
            f"Try to keep your spending under ₹{safe_limit:.0f} as a safe limit.\n"
            "Tip: Focus on the categories where you spend the most."
        )

    return pred, advice
