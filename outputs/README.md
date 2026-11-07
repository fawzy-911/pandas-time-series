# Generated outputs

Run `python time_series.py` after downloading the data to create:

- `monthly_sales.csv` — month-end observations and monthly sales totals.
- `quarterly_sales.csv` — quarterly totals summed from the monthly, non-seasonally-adjusted series.
- `monthly_changes.csv` — previous observation, absolute change, and percentage change.
- `vehicle_sales_rolling_mean.png` — original monthly series with its trailing 12-month rolling mean.

These files are generated locally and ignored by Git.
