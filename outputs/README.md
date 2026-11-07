# Generated outputs

Run `python time_series.py` after downloading the data to create:

- `monthly_sales.csv` — month-end observations and monthly sales totals.
- `quarterly_sales.csv` — quarterly totals summed from the monthly, non-seasonally-adjusted series.
- `sales_changes.csv` — prior-month and prior-year observations, absolute changes, and percentage changes.
- `seasonal_summary.csv` — observation count, mean, median, minimum, and maximum for each calendar month.
- `missing_months.csv` — any calendar months absent between the first and last source observations.
- `run_summary.json` — date range, observation count, latest and average sales, configured rolling window, and missing-month count.
- `vehicle_sales_rolling_mean.png` — original monthly series with its configurable trailing rolling mean.
- `seasonal_monthly_average.png` — average observed sales by calendar month across all years.

These files are generated locally and ignored by Git.
