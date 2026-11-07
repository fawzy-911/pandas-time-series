"""Reusable Pandas helpers for the FRED light vehicle sales series."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).parent
DATA_FILE = PROJECT_DIR / "data" / "light_vehicle_sales.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs"
DATE_COLUMN = "observation_date"
VALUE_COLUMN = "LTOTALNSA"


def load_sales(path: Path = DATA_FILE) -> pd.Series:
    """Load and validate the FRED CSV as a sorted monthly DatetimeIndex series."""
    if not path.is_file():
        raise FileNotFoundError(f"Data file not found: {path}. Run `python download_data.py` first.")
    frame = pd.read_csv(path, na_values=["."])
    missing = {DATE_COLUMN, VALUE_COLUMN} - set(frame.columns)
    if missing:
        raise ValueError(f"CSV is missing columns: {', '.join(sorted(missing))}")

    frame[DATE_COLUMN] = pd.to_datetime(frame[DATE_COLUMN], errors="coerce")
    frame[VALUE_COLUMN] = pd.to_numeric(frame[VALUE_COLUMN], errors="coerce")
    frame = frame.dropna(subset=[DATE_COLUMN, VALUE_COLUMN])
    if frame.empty:
        raise ValueError("The CSV contains no valid date and sales observations.")
    if frame[DATE_COLUMN].duplicated().any():
        raise ValueError("The CSV contains duplicate observation dates.")

    series = frame.set_index(DATE_COLUMN)[VALUE_COLUMN].sort_index().astype("float64")
    series.name = "Sales (thousands of vehicles)"
    return series


def make_frequency_examples(start: str, end: str) -> dict[str, pd.DatetimeIndex]:
    """Create daily, weekly, and month-end date ranges for frequency examples."""
    return {
        "daily (D)": pd.date_range(start=start, end=end, freq="D"),
        "weekly (W)": pd.date_range(start=start, end=end, freq="W"),
        # Pandas 2.2+ uses ME for month-end; the older M alias is deprecated.
        "month-end (ME; formerly M)": pd.date_range(start=start, end=end, freq="ME"),
    }


def resample_sales(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Return monthly and quarterly sales totals (the source is monthly units)."""
    monthly = series.resample("ME").sum(min_count=1)
    quarterly = series.resample("QE").sum(min_count=1)
    monthly.name = "Monthly sales (thousands)"
    quarterly.name = "Quarterly sales (thousands)"
    return monthly, quarterly


def add_change_measures(series: pd.Series) -> pd.DataFrame:
    """Add previous-month sales and month-over-month change measures."""
    result = series.to_frame(name="Sales (thousands)")
    result["Previous month"] = series.shift(1)
    result["Change"] = series.diff()
    result["Percent change"] = series.pct_change(fill_method=None).mul(100)
    return result


def rolling_mean(series: pd.Series, window: int = 12) -> pd.Series:
    """Calculate a trailing rolling mean, requiring a complete window."""
    if window < 1:
        raise ValueError("Rolling window must be at least 1 month.")
    return series.rolling(window=window, min_periods=window).mean()


def save_analysis(series: pd.Series, output_dir: Path = OUTPUT_DIR) -> None:
    """Write monthly, quarterly, change tables, and a time-series chart."""
    output_dir.mkdir(parents=True, exist_ok=True)
    monthly, quarterly = resample_sales(series)
    changes = add_change_measures(series)
    monthly.to_frame().to_csv(output_dir / "monthly_sales.csv", index_label="Date")
    quarterly.to_frame().to_csv(output_dir / "quarterly_sales.csv", index_label="Date")
    changes.to_csv(output_dir / "monthly_changes.csv", index_label="Date")

    average = rolling_mean(series)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(series.index, series, label="Monthly light vehicle sales", color="#2f6fed", linewidth=1.4)
    ax.plot(average.index, average, label="12-month rolling mean", color="#ef7c32", linewidth=2.2)
    ax.set_title("U.S. Light Vehicle Sales")
    ax.set_xlabel("Date")
    ax.set_ylabel("Thousands of vehicles (not seasonally adjusted)")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "vehicle_sales_rolling_mean.png", dpi=160)
    plt.close(fig)


def main() -> None:
    series = load_sales()
    monthly, quarterly = resample_sales(series)
    save_analysis(series)
    print(f"Observations: {len(series):,}")
    print(f"Date range: {series.index.min():%Y-%m} to {series.index.max():%Y-%m}")
    print(f"Latest month: {series.index[-1]:%Y-%m} — {series.iloc[-1]:,.1f} thousand vehicles")
    print(f"Monthly periods: {len(monthly):,}; quarterly periods: {len(quarterly):,}")
    print(f"Outputs saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
