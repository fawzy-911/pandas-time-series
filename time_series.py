"""Reusable Pandas analysis for the FRED light vehicle sales series."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_DIR = Path(__file__).parent
DATA_FILE = PROJECT_DIR / "data" / "light_vehicle_sales.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs"
DATE_COLUMN = "observation_date"
VALUE_COLUMN = "LTOTALNSA"
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


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
    if (frame[VALUE_COLUMN] < 0).any():
        raise ValueError("The CSV contains negative vehicle sales observations.")

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
    """Return monthly and quarterly sales totals from monthly unit observations."""
    monthly = series.resample("ME").sum(min_count=1)
    quarterly = series.resample("QE").sum(min_count=1)
    monthly.name = "Monthly sales (thousands)"
    quarterly.name = "Quarterly sales (thousands)"
    return monthly, quarterly


def complete_monthly_series(series: pd.Series) -> pd.Series:
    """Return a full calendar-month index without filling missing observations."""
    if series.empty:
        raise ValueError("Cannot align an empty sales series.")
    periods = series.index.to_period("M")
    if periods.duplicated().any():
        raise ValueError("Expected at most one sales observation per calendar month.")
    aligned = series.copy()
    aligned.index = periods
    full_periods = pd.period_range(periods.min(), periods.max(), freq="M")
    # Reindexing inserts NaN for gaps so shifts always mean calendar months, not rows.
    aligned = aligned.reindex(full_periods)
    aligned.index = aligned.index.to_timestamp(how="end").normalize()
    return aligned


def add_change_measures(series: pd.Series) -> pd.DataFrame:
    """Add prior-month and prior-year values with absolute and relative changes."""
    monthly = complete_monthly_series(series)
    result = monthly.to_frame(name="Sales (thousands)")
    result["Previous month"] = monthly.shift(1)
    result["Monthly change"] = monthly.diff()
    result["Monthly percent change"] = monthly.pct_change(fill_method=None).mul(100)
    result["Previous year"] = monthly.shift(12)
    result["Year-over-year change"] = monthly.diff(12)
    result["Year-over-year percent change"] = monthly.pct_change(periods=12, fill_method=None).mul(100)
    return result


def seasonal_summary(series: pd.Series) -> pd.DataFrame:
    """Summarize sales by calendar month across all observed years."""
    grouped = (
        series.groupby(series.index.month)
        .agg(["count", "mean", "median", "min", "max"])
        .reindex(range(1, 13))
    )
    grouped.index = pd.Index(MONTH_LABELS, name="Calendar month")
    return grouped.rename(columns={
        "count": "Observations",
        "mean": "Mean sales (thousands)",
        "median": "Median sales (thousands)",
        "min": "Minimum sales (thousands)",
        "max": "Maximum sales (thousands)",
    })


def missing_months(series: pd.Series) -> pd.DataFrame:
    """List calendar months absent between the first and last observation."""
    observed = pd.PeriodIndex(series.index.to_period("M").unique(), freq="M")
    expected = pd.period_range(observed.min(), observed.max(), freq="M")
    gaps = expected.difference(observed)
    return pd.DataFrame({"Missing month": gaps.astype(str)})


def rolling_mean(series: pd.Series, window: int = 12) -> pd.Series:
    """Calculate a trailing rolling mean, requiring a complete window."""
    if window < 1:
        raise ValueError("Rolling window must be at least 1 month.")
    monthly = complete_monthly_series(series)
    return monthly.rolling(window=window, min_periods=window).mean()


def save_analysis(series: pd.Series, output_dir: Path = OUTPUT_DIR, rolling_window: int = 12) -> None:
    """Write resampled tables, changes, seasonal summary, audit, and charts."""
    if rolling_window < 1:
        raise ValueError("Rolling window must be at least 1 month.")
    output_dir.mkdir(parents=True, exist_ok=True)
    monthly, quarterly = resample_sales(series)
    changes = add_change_measures(series)
    seasonal = seasonal_summary(series)
    gaps = missing_months(series)
    monthly.to_frame().to_csv(output_dir / "monthly_sales.csv", index_label="Date")
    quarterly.to_frame().to_csv(output_dir / "quarterly_sales.csv", index_label="Date")
    changes.to_csv(output_dir / "sales_changes.csv", index_label="Date")
    seasonal.to_csv(output_dir / "seasonal_summary.csv", index_label="Calendar month")
    gaps.to_csv(output_dir / "missing_months.csv", index=False)

    summary = {
        "observations": int(len(series)),
        "date_start": series.index.min().date().isoformat(),
        "date_end": series.index.max().date().isoformat(),
        "latest_sales_thousands": round(float(series.iloc[-1]), 3),
        "average_sales_thousands": round(float(series.mean()), 3),
        "rolling_window_months": rolling_window,
        "missing_months": int(len(gaps)),
    }
    (output_dir / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    average = rolling_mean(series, window=rolling_window)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(series.index, series, label="Monthly light vehicle sales", color="#2f6fed", linewidth=1.4)
    ax.plot(average.index, average, label=f"{rolling_window}-month rolling mean", color="#ef7c32", linewidth=2.2)
    ax.set_title("U.S. Light Vehicle Sales")
    ax.set_xlabel("Date")
    ax.set_ylabel("Thousands of vehicles (not seasonally adjusted)")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "vehicle_sales_rolling_mean.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(seasonal.index, seasonal["Mean sales (thousands)"], color="#2f6fed", alpha=0.85)
    ax.set_title("Average Light Vehicle Sales by Calendar Month")
    ax.set_xlabel("Calendar month")
    ax.set_ylabel("Mean sales (thousands)")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(output_dir / "seasonal_monthly_average.png", dpi=160)
    plt.close(fig)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Analyze FRED light vehicle sales with Pandas.")
    parser.add_argument("--data", type=Path, default=DATA_FILE, help="Path to the downloaded FRED CSV.")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, help="Directory for tables and charts.")
    parser.add_argument("--rolling-window", type=int, default=12, help="Rolling mean window in months (default: 12).")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.rolling_window < 1:
        raise SystemExit("--rolling-window must be at least 1.")
    series = load_sales(args.data)
    monthly, quarterly = resample_sales(series)
    gaps = missing_months(series)
    save_analysis(series, output_dir=args.output_dir, rolling_window=args.rolling_window)
    print(f"Observations: {len(series):,}")
    print(f"Date range: {series.index.min():%Y-%m} to {series.index.max():%Y-%m}")
    print(f"Latest month: {series.index[-1]:%Y-%m} — {series.iloc[-1]:,.1f} thousand vehicles")
    print(f"Monthly periods: {len(monthly):,}; quarterly periods: {len(quarterly):,}")
    print(f"Missing calendar months: {len(gaps):,}")
    print(f"Rolling window: {args.rolling_window} months")
    print(f"Outputs saved to: {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
