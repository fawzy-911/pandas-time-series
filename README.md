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

Generate resampled tables, change measures, seasonal summaries, and charts:

```bash
python time_series.py
```

Choose a different rolling window or data/output paths:

```bash
python time_series.py --rolling-window 6
python time_series.py --data data/light_vehicle_sales.csv --output-dir outputs/run-2
```

Run `python time_series.py --help` for all options.

Explore the steps interactively:

```bash
jupyter notebook pandas_time_series.ipynb
```

## Analysis notes

- The CSV's observation date is parsed and used as a sorted `DatetimeIndex`.
- `pd.date_range()` demonstrates daily (`D`), weekly (`W`), and month-end (`ME`) ranges. Pandas 2.2 deprecated the older month-end `M` alias in favor of `ME`.
- Since this FRED series is already monthly and contains monthly units, quarterly totals are calculated by summing three monthly observations. These are not annualized rates.
- `.shift(1)` and `.diff()` compare a month with its previous observation; a 12-period shift calculates year-over-year changes.
- The rolling mean is trailing and appears only after a full configured window.
- Seasonal summaries compare calendar months across all years. Missing months in the overall date span are listed; the analysis does not interpolate or invent values for gaps.

## Outputs

The `outputs/` folder contains monthly and quarterly CSVs, monthly and year-over-year changes, seasonal summaries, gap and run reports, and two charts. See [`outputs/README.md`](outputs/README.md).

## Source

U.S. Bureau of Economic Analysis, Light Weight Vehicle Sales [LTOTALNSA], retrieved from FRED, Federal Reserve Bank of St. Louis. [Series page](https://fred.stlouisfed.org/series/LTOTALNSA). The series is public domain; citation is requested. Source notes are in [`data/README.md`](data/README.md).

See [`docs/methodology.md`](docs/methodology.md) for more detail on resampling and interpretation. Contributions and issue reports are welcome; see [`CONTRIBUTING.md`](CONTRIBUTING.md).
