# Pandas Time Series: Vehicle Sales

Learn Pandas date and time tools using the FRED Light Weight Vehicle Sales series (`LTOTALNSA`). This is monthly U.S. light vehicle sales, in thousands of units, not seasonally adjusted. The project covers `DatetimeIndex`, frequency strings, resampling, shifting, differencing, rolling means, and plotting.

**Roadmap project:** <https://roadmap.sh/projects/pandas-time-series>

## Setup

```bash
python -m venv .venv
```

Activate the environment, then:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate

python -m pip install -r requirements.txt
python download_data.py
```

## Run

Generate resampled tables and a chart:

```bash
python time_series.py
```

Explore the steps interactively:

```bash
jupyter notebook pandas_time_series.ipynb
```

## Analysis notes

- The CSV's observation date is parsed and used as a sorted `DatetimeIndex`.
- `pd.date_range()` demonstrates daily (`D`), weekly (`W`), and month-end (`ME`) ranges. Pandas 2.2 deprecated the older month-end `M` alias in favor of `ME`.
- Since this FRED series is already monthly and contains monthly units, quarterly totals are calculated by summing three monthly observations. These are not annualized rates.
- `.shift(1)`, `.diff()`, and percentage change compare a month with its previous observation.
- The 12-month rolling mean is trailing and appears only after a full 12 observations.

## Outputs

The `outputs/` folder contains monthly and quarterly CSVs, month-over-month changes, and `vehicle_sales_rolling_mean.png`. See [`outputs/README.md`](outputs/README.md).

## Source

U.S. Bureau of Economic Analysis, Light Weight Vehicle Sales [LTOTALNSA], retrieved from FRED, Federal Reserve Bank of St. Louis. [Series page](https://fred.stlouisfed.org/series/LTOTALNSA). The series is public domain; citation is requested. Source notes are in [`data/README.md`](data/README.md).
